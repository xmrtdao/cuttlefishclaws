"""PVP-001 — Principal Verification Protocol (protocol-internal, no third-party KYC vendor).

Sprint 4 scope = STRUCTURAL verification (PVP-001 §5):
  * validate the PrincipalChain shape (terminates at natural_person|legal_entity, depth <= 3)
  * each level carries a signed attestation that verifies
  * entities/DAOs assert authority; DAOs carry a governance address
  * the terminal principal's binding_proof verifies (KYA-001 accountability acceptance)
  * a deterministic verification_hash is computed (idempotent)
  * a KYA_REGISTRATION event is emitted to the registry (mockable HTTP)

The §4 verification METHODS are protocol-internal: signed self-attestations verified via
registered keys (kya.py), not a third-party KYC vendor. Real document/liveness/entity-registry
proofing is the programmer's integration; here it is structural. TODO(PROGRAMMER).
"""

from __future__ import annotations

import hashlib
import os
import sys
from typing import Callable

# Reuse Sprint 2 KYA crypto (canonical_json, verify_payload, PublicKeyRef).
# TODO(PROGRAMMER): extract shared crypto into /shared/ instead of cross-service sys.path.
_REGISTRY_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cuttlefish-registry"))
if _REGISTRY_DIR not in sys.path:
    sys.path.append(_REGISTRY_DIR)   # APPEND: pvp's own modules (schema, storage, main) win; only `kya` resolves here
import kya  # noqa: E402

from schema import (  # noqa: E402
    AttestorSignature,
    DAO,
    LEGAL_ENTITY,
    PrincipalChain,
    PrincipalLevel,
    TERMINAL_TYPES,
)

REGISTRY_ENDPOINT = os.environ.get("REGISTRY_ENDPOINT", "http://localhost:8081")


class VerificationError(Exception):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


# --------------------------------------------------------------- signed payloads

def level_attestation_payload(level: PrincipalLevel) -> dict:
    """What the attestor signs for a level (everything but the signature itself)."""
    return {
        "level": level.level,
        "principal_type": level.principal_type,
        "principal_id": level.principal_id,
        "jurisdiction": level.jurisdiction,
        "verification_method": level.verification_method,
        "attested_at": level.attested_at,
        "authority": level.authority,
        "governance_address": level.governance_address,
    }


def binding_payload(chain: PrincipalChain) -> dict:
    """AIL-001 §3.2 accountability acceptance the terminal principal signs (binding_proof)."""
    return {
        "agent_id": chain.agent_id,
        "terminal_principal": chain.terminal_principal,
        "accept": "AIL-001 §3.2 responsibilities",
    }


def _verify_sig(sig: AttestorSignature, payload: dict) -> bool:
    try:
        key_ref = kya.PublicKeyRef(
            key_id="attestor", algorithm=sig.algorithm, public_key=bytes.fromhex(sig.public_key)
        )
        return kya.verify_payload(key_ref, payload, bytes.fromhex(sig.signature))
    except ValueError:
        return False


def _ial_for_chain(chain: PrincipalChain) -> str:
    # PVP-001 §3: PVP-1 -> IAL2 (default); supervised/notarized proofing -> PVP-2 -> IAL3.
    strong = {"supervised_proofing", "notarized_attestation"}
    return "IAL3" if any(lvl.verification_method in strong for lvl in chain.chain) else "IAL2"


# --------------------------------------------------------------- verification (§5)

def verify_chain(chain: PrincipalChain) -> dict:
    """PVP-001 §5 structural verification. Raises VerificationError on any failure."""
    # step 1 shape
    if not chain.chain:
        raise VerificationError("empty_chain")
    depth = len(chain.chain)
    if depth > chain.max_delegation_depth or depth > 3:
        raise VerificationError("depth_exceeds_max")
    for i, lvl in enumerate(chain.chain):
        if lvl.level != i:
            raise VerificationError("non_contiguous_levels")

    # step 3 termination check (asserted early; cheap)
    terminal = chain.chain[-1]
    if terminal.principal_type not in TERMINAL_TYPES:
        raise VerificationError("terminal_not_natural_or_legal")

    # step 2 per-level verification
    for lvl in chain.chain:
        if not _verify_sig(lvl.attestor_signature, level_attestation_payload(lvl)):
            raise VerificationError(f"level_{lvl.level}_attestation_invalid")
        if lvl.principal_type in {LEGAL_ENTITY, DAO} and not lvl.authority:
            raise VerificationError(f"level_{lvl.level}_authority_missing")
        if lvl.principal_type == DAO and not lvl.governance_address:
            raise VerificationError(f"level_{lvl.level}_governance_address_missing")

    # step 4 accountability binding
    if not _verify_sig(chain.binding_proof, binding_payload(chain)):
        raise VerificationError("binding_proof_invalid")

    # step 5 reachability
    if not chain.point_of_contact:
        raise VerificationError("reachability_missing")

    # deterministic verification_hash (idempotent: same chain -> same hash)
    verification_hash = hashlib.sha256(
        kya.canonical_json(chain.model_dump()).encode("utf-8")
    ).hexdigest()

    return {
        "verification_hash": verification_hash,
        "principal_id": chain.terminal_principal,
        "ial_level": _ial_for_chain(chain),
        "attested_at": terminal.attested_at,
        "jurisdiction": terminal.jurisdiction,
    }


# --------------------------------------------------------------- registry emission (mockable)

def _default_emit(payload: dict) -> dict:
    import httpx
    resp = httpx.post(f"{REGISTRY_ENDPOINT}/registry/v1/events", json=payload, timeout=5.0)
    return {"status_code": resp.status_code}


# Tests replace `emit_hook` to mock the HTTP call (no live registry needed).
emit_hook: Callable[[dict], dict] = _default_emit


def emit_kya_registration(verification_hash: str, principal_id: str, ial_level: str) -> dict:
    """PVP-001 §5 step 6 — emit a KYA_REGISTRATION event to the registry.

    TODO(NAVIGATOR): `KYA_REGISTRATION` must exist in the registry AR-001 ActivityType enum.
    TODO(PROGRAMMER): this emission must itself be KYA-signed (a PVP/registry system key)
    now that the write path enforces signatures (Sprint 3)."""
    payload = {
        "activity_type": "KYA_REGISTRATION",
        "primary_actor_id": principal_id,
        "activity_subject": {"type": "principal", "id": principal_id},
        "work_unit": {"quantity": 1, "unit": "registration"},
        "evidence_hash": verification_hash,
        "reward_eligibility": {},
        "metadata": {"ial_level": ial_level},
    }
    return emit_hook(payload)


def emit_revocation(principal_id: str) -> dict:
    payload = {
        "activity_type": "STANDING_ADJUSTED",   # placeholder lapse signal; see TODO below
        "primary_actor_id": principal_id,
        "activity_subject": {"type": "principal", "id": principal_id},
        "work_unit": {"quantity": 0, "unit": "revocation"},
        "evidence_hash": hashlib.sha256(f"revoke:{principal_id}".encode()).hexdigest(),
        "reward_eligibility": {},
    }
    # TODO(NAVIGATOR): the canonical revocation/lapse event type for a principal (PVP-001 §6).
    return emit_hook(payload)
