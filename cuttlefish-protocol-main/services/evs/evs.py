"""EVS-001 — Evidence storage: content-addressed custody, PII gate, retention, erasure-safe tombstones.

Implements `canon/EVS-001_EVIDENCE_STORAGE_SPEC.md`:
  * §3.2 content-addressed integrity (evidence_hash = SHA-256(payload), verifiable independent of location).
  * §3.3 / §6 no PII on a public/permanent store: `contains_pii=true` ⇒ storage_class ∈ {local, s3} only.
  * §5.1.1 fail-safe PII gate: default `contains_pii=true`; a public/permanent store (ipfs/ar) needs an
    explicit clearance, never a heuristic.
  * §6 least-authority access (public / actor / sponsor / auditor), resolved on every read.
  * §7 erasure-safe append-only: erase leaves a verifiable tombstone (410), not a gap; legal_hold blocks erase (423).

The payload is held off-registry; only its hash is anchored (AR-001 §5.3). TODO(PROGRAMMER): real
s3/ipfs/ar backends, encryption (aes-256-gcm / age), and KYA-resolved access (here access is a simple model).
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Optional

PII_ELIGIBLE_STORES = {"local", "s3"}            # §6 — encrypted, erasable, access-controlled
PUBLIC_PERMANENT_STORES = {"ipfs", "ar"}         # §6 — NON-PII only
ALL_STORES = PII_ELIGIBLE_STORES | PUBLIC_PERMANENT_STORES
RETENTION_CLASSES = {"transient", "standard", "compliance", "legal_hold"}
VISIBILITIES = {"public", "actor", "sponsor", "auditor"}


class EvidenceError(Exception):
    """code maps to an HTTP status (400 bad request, 403 forbidden, 404, 410 gone/tombstone, 423 locked)."""
    def __init__(self, code: int, reason: str) -> None:
        self.code = code
        self.reason = reason
        super().__init__(reason)


def content_hash(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


@dataclass
class EvidenceObject:
    evidence_hash: str
    storage_class: str
    contains_pii: bool
    visibility: str
    retention_class: str
    owner_kya_id: str
    sponsor_kya_id: Optional[str] = None
    payload: Optional[bytes] = None              # None once redacted (tombstone)
    redacted: bool = False
    granted: dict = field(default_factory=dict)  # auditor_kya_id -> expires_at (epoch)

    def evidence_uri(self) -> str:
        return f"{self.storage_class}://{self.evidence_hash}"


def _resolve_storage_class(contains_pii: bool, cleared_pii: bool, requested: Optional[str]) -> str:
    # §5.1.1 fail-safe: only an explicitly-cleared non-PII object may use a public/permanent store.
    eligible = ALL_STORES if (not contains_pii and cleared_pii) else PII_ELIGIBLE_STORES
    if requested is None:
        return "s3"                              # default warm tier (§4)
    if requested not in ALL_STORES:
        raise EvidenceError(400, f"unknown storage_class: {requested}")
    if requested not in eligible:
        raise EvidenceError(400, f"storage_class '{requested}' not permitted for contains_pii={contains_pii} (EVS-001 §6)")
    return requested


class EvidenceService:
    def __init__(self) -> None:
        self._objects: dict[str, EvidenceObject] = {}
        self._access_log: list[dict] = []

    # ----------- put (§5.1)

    def put(
        self,
        payload: bytes,
        owner_kya_id: str,
        contains_pii: bool = True,               # §5.1.1 default true
        cleared_pii: bool = False,
        retention_class: str = "standard",
        visibility: str = "actor",
        storage_class: Optional[str] = None,
        sponsor_kya_id: Optional[str] = None,
    ) -> EvidenceObject:
        if retention_class not in RETENTION_CLASSES:
            raise EvidenceError(400, f"unknown retention_class: {retention_class}")
        if visibility not in VISIBILITIES:
            raise EvidenceError(400, f"unknown visibility: {visibility}")
        if visibility == "public" and contains_pii:
            raise EvidenceError(400, "public visibility not allowed for PII-bearing evidence (EVS-001 §6)")
        sclass = _resolve_storage_class(contains_pii, cleared_pii, storage_class)
        ehash = content_hash(payload)
        obj = EvidenceObject(
            evidence_hash=ehash, storage_class=sclass, contains_pii=contains_pii,
            visibility=visibility, retention_class=retention_class, owner_kya_id=owner_kya_id,
            sponsor_kya_id=sponsor_kya_id, payload=payload,
        )
        self._objects[ehash] = obj               # content-addressed: identical payload -> same hash
        return obj

    # ----------- access (§6)

    def _can_read(self, obj: EvidenceObject, as_kya_id: Optional[str], now: int) -> bool:
        if obj.visibility == "public":
            return True
        if as_kya_id is None:
            return False
        if as_kya_id == obj.owner_kya_id:
            return True
        if obj.visibility == "sponsor" and as_kya_id == obj.sponsor_kya_id:
            return True
        exp = obj.granted.get(as_kya_id)          # auditor grant (time-boxed)
        return exp is not None and now < exp

    def get(self, evidence_hash: str, as_kya_id: Optional[str] = None, now: Optional[int] = None) -> bytes:
        now = int(time.time()) if now is None else now
        obj = self._objects.get(evidence_hash)
        if obj is None:
            raise EvidenceError(404, "unknown evidence")
        if obj.redacted:
            raise EvidenceError(410, "evidence redacted (tombstone)")   # §7
        if not self._can_read(obj, as_kya_id, now):
            raise EvidenceError(403, "not authorized")
        self._access_log.append({"hash": evidence_hash, "as": as_kya_id, "at": now})
        return obj.payload

    def verify(self, evidence_hash: str, payload: bytes) -> bool:
        """§3.2/§5.2 — anyone can confirm a payload matches the anchored hash, trustlessly."""
        return content_hash(payload) == evidence_hash

    # ----------- erase (§7) and grant

    def erase(self, evidence_hash: str, requester: str, reason: str) -> EvidenceObject:
        obj = self._objects.get(evidence_hash)
        if obj is None:
            raise EvidenceError(404, "unknown evidence")
        if obj.retention_class == "legal_hold":
            raise EvidenceError(423, "evidence under legal_hold; cannot erase")   # §7
        obj.payload = None
        obj.redacted = True                       # tombstone: hash remains, payload gone
        self._access_log.append({"hash": evidence_hash, "erased_by": requester, "reason": reason})
        return obj

    def grant(self, evidence_hash: str, auditor_kya_id: str, ttl_seconds: int, now: Optional[int] = None) -> int:
        now = int(time.time()) if now is None else now
        obj = self._objects.get(evidence_hash)
        if obj is None:
            raise EvidenceError(404, "unknown evidence")
        expires_at = now + ttl_seconds
        obj.granted[auditor_kya_id] = expires_at
        self._access_log.append({"hash": evidence_hash, "grant": auditor_kya_id, "expires_at": expires_at})
        return expires_at

    def meta(self, evidence_hash: str) -> Optional[EvidenceObject]:
        return self._objects.get(evidence_hash)

    @property
    def access_log(self) -> list[dict]:
        return self._access_log
