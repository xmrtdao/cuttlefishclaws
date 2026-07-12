"""KYA-001 — Know Your Agent: identity bindings and event signatures.

Implements CFL-SPEC-KYA-001:
  * §2  content-addressed KYA_ID over the binding document
  * §2  KYABinding / PublicKeyRef / PrincipalRef data model
  * §4.1 actor signing payload + signature construction
  * §4.2 signature verification (ed25519, secp256k1, rsa-pss)
  * in-memory KYA registry: register / get / rotate / revoke

This module is standalone. It is NOT wired into the AR-001 write path here —
that is Sprint 3 (KYA-001 §4.2 write-path enforcement).

Canonicalization note: `canonical_json` below is a JCS-style canonical form
(sorted keys, compact separators, UTF-8). KYA-001 §4.1 specifies RFC 8785 JCS;
for full cross-implementation interop a vetted JCS library should be substituted.
TODO(PROGRAMMER): swap in a verified RFC 8785 JCS implementation.

Multibase note: the KYA_ID subject uses multibase base64url ('u' prefix). The spec
says `multibase(SHA-256(binding_document))` without pinning the base; base64url is
deterministic and dependency-free. TODO(NAVIGATOR): confirm the canonical multibase
code (e.g. base58btc 'z') if it matters for external interop.
"""

from __future__ import annotations

import base64
import calendar
import hashlib
import json
import time
from dataclasses import dataclass
from typing import Optional

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, ed25519, padding, utils

# --------------------------------------------------------------- enums (KYA-001 §2/§3)

ACTOR_KINDS = {"agent", "human", "hybrid"}
ALGORITHMS = {"ed25519", "secp256k1", "rsa-pss"}   # exact AR-001 §3.2 set
KEY_STATUSES = {"active", "rotated", "revoked"}
IAL_LEVELS = {"IAL2", "IAL3"}
KEY_PURPOSES = {"actor_signing", "witness_signing", "rotation"}
KEY_BINDINGS = {"cac_card", "operator_hsm", "software_key"}


# --------------------------------------------------------------- canonicalization

def canonical_json(obj) -> str:
    """JCS-style canonical JSON (sorted keys, no whitespace). See module note."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _multibase_b64url(data: bytes) -> str:
    return "u" + base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _iso_to_epoch(ts: str) -> Optional[int]:
    try:
        return calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
    except (ValueError, TypeError):
        return None


# --------------------------------------------------------------- data model (§2)

@dataclass
class PublicKeyRef:
    key_id: str
    algorithm: str                      # ed25519 | secp256k1 | rsa-pss
    public_key: bytes                   # raw/encoded public key bytes
    purpose: str = "actor_signing"      # actor_signing | witness_signing | rotation
    bound_to: str = "software_key"      # cac_card | operator_hsm | software_key
    status: str = "active"              # active | rotated | revoked

    def to_doc(self) -> dict:
        return {
            "key_id": self.key_id,
            "algorithm": self.algorithm,
            "public_key": self.public_key.hex(),
            "purpose": self.purpose,
            "bound_to": self.bound_to,
            "status": self.status,
        }


@dataclass
class PrincipalRef:
    principal_kind: str                 # navigator | operator | organization | dao
    principal_id: str
    binding_proof: bytes                # principal signature accepting accountability

    def to_doc(self) -> dict:
        return {
            "principal_kind": self.principal_kind,
            "principal_id": self.principal_id,
            "binding_proof": self.binding_proof.hex(),
        }


@dataclass
class KYABinding:
    actor_kind: str
    principal_ref: PrincipalRef
    public_keys: list[PublicKeyRef]
    ial_level: str
    issued_at: str                      # ISO-8601 UTC
    issuer: str = "did:web:cuttlefishlabs.io"
    agent_did: Optional[str] = None
    cac_credential_id: Optional[str] = None

    def binding_document(self) -> dict:
        """KYA-001 §2 — the content the KYA_ID is addressed over."""
        return {
            "actor_kind": self.actor_kind,
            "agent_did": self.agent_did,
            "principal_ref": self.principal_ref.to_doc(),
            "cac_credential_id": self.cac_credential_id,
            "public_keys": [k.to_doc() for k in self.public_keys],
            "ial_level": self.ial_level,
            "issued_at": self.issued_at,
            "issuer": self.issuer,
        }

    def kya_id(self) -> str:
        """§2: kya:<namespace>:<multibase(SHA-256(binding_document))>."""
        digest = hashlib.sha256(canonical_json(self.binding_document()).encode("utf-8")).digest()
        return f"kya:{self.actor_kind}:{_multibase_b64url(digest)}"

    def find_key(self, key_id: str) -> Optional[PublicKeyRef]:
        for k in self.public_keys:
            if k.key_id == key_id:
                return k
        return None


# --------------------------------------------------------------- signing / verification (§4.1, §4.2)

# KYA-001 §4.1 — the actor signs the event MINUS the registry-added fields.
REGISTRY_ADDED_FIELDS = {"self_hash", "registry_signature", "witness_signatures"}


def actor_signing_payload(event: dict) -> dict:
    return {k: v for k, v in event.items() if k not in REGISTRY_ADDED_FIELDS}


def _payload_digest(payload: dict) -> bytes:
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).digest()


def sign_payload(private_key, algorithm: str, payload: dict) -> bytes:
    """Sign(actor_key, SHA-256(canonical_json(payload))) per §4.1."""
    d = _payload_digest(payload)
    if algorithm == "ed25519":
        return private_key.sign(d)
    if algorithm == "secp256k1":
        return private_key.sign(d, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
    if algorithm == "rsa-pss":
        return private_key.sign(
            d,
            padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
            utils.Prehashed(hashes.SHA256()),
        )
    raise ValueError(f"unsupported algorithm: {algorithm}")


def _load_public_key(algorithm: str, public_key: bytes):
    if algorithm == "ed25519":
        return ed25519.Ed25519PublicKey.from_public_bytes(public_key)
    if algorithm == "secp256k1":
        return ec.EllipticCurvePublicKey.from_encoded_point(ec.SECP256K1(), public_key)
    if algorithm == "rsa-pss":
        return serialization.load_der_public_key(public_key)
    raise ValueError(f"unsupported algorithm: {algorithm}")


def verify_payload(key_ref: PublicKeyRef, payload: dict, signature: bytes) -> bool:
    """§4.2 — verify a signature against a PublicKeyRef (key material + algorithm)."""
    d = _payload_digest(payload)
    try:
        pub = _load_public_key(key_ref.algorithm, key_ref.public_key)
        if key_ref.algorithm == "ed25519":
            pub.verify(signature, d)
        elif key_ref.algorithm == "secp256k1":
            pub.verify(signature, d, ec.ECDSA(utils.Prehashed(hashes.SHA256())))
        elif key_ref.algorithm == "rsa-pss":
            pub.verify(
                signature, d,
                padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH),
                utils.Prehashed(hashes.SHA256()),
            )
        else:
            return False
        return True
    except (InvalidSignature, ValueError, TypeError):
        return False


# --------------------------------------------------------------- in-memory registry

class KYARegistry:
    """In-memory KYA binding store. Sprint 2 scope: register / get / rotate / revoke.

    rotate/revoke mutate a key's status in place under the registration-time KYA_ID.
    A full implementation would supersede the binding via a KYA_RENEWAL event with a
    new content-addressed KYA_ID (KYA-001 §2 / AR-001 §5.4). TODO(NAVIGATOR/PROGRAMMER).
    """

    def __init__(self) -> None:
        self._bindings: dict[str, KYABinding] = {}

    def register(self, binding: KYABinding) -> str:
        kya_id = binding.kya_id()
        self._bindings[kya_id] = binding
        return kya_id

    def get(self, kya_id: str) -> Optional[KYABinding]:
        return self._bindings.get(kya_id)

    def get_key(self, kya_id: str, key_id: str) -> Optional[PublicKeyRef]:
        binding = self._bindings.get(kya_id)
        return binding.find_key(key_id) if binding else None

    def rotate(self, kya_id: str, key_id: str) -> bool:
        key = self.get_key(kya_id, key_id)
        if key is None:
            return False
        key.status = "rotated"
        return True

    def revoke(self, kya_id: str, key_id: str) -> bool:
        key = self.get_key(kya_id, key_id)
        if key is None:
            return False
        key.status = "revoked"
        return True

    def verify_event_signature(
        self,
        kya_id: str,
        key_id: str,
        event: dict,
        signature: bytes,
        signed_at: Optional[int] = None,
    ) -> tuple[bool, str]:
        """KYA-001 §4.2 checks 1 & 5: active key in current binding, sig verifies,
        signed_at >= key issued_at. Returns (ok, reason)."""
        binding = self._bindings.get(kya_id)
        if binding is None:
            return False, "unknown_kya_id"
        key = binding.find_key(key_id)
        if key is None:
            return False, "unknown_key_id"
        if key.status != "active":
            return False, f"key_status:{key.status}"
        if signed_at is not None:
            issued = _iso_to_epoch(binding.issued_at)
            if issued is not None and signed_at < issued:
                return False, "signed_before_issued"
        if not verify_payload(key, actor_signing_payload(event), signature):
            return False, "signature_invalid"
        return True, "ok"
