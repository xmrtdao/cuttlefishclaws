"""PVP-001 request/response models (AIL-001 §3.4 PrincipalChain)."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel

# principal_type values (AIL-001 §3.4)
NATURAL_PERSON = "natural_person"
LEGAL_ENTITY = "legal_entity"
DAO = "dao"
AGENT = "agent"
TERMINAL_TYPES = {NATURAL_PERSON, LEGAL_ENTITY}   # PVP-001 §2 / AIL-001 §3.1


class AttestorSignature(BaseModel):
    algorithm: str          # ed25519 | secp256k1 | rsa-pss (AR-001 §3.2)
    public_key: str         # hex
    signature: str          # hex


class PrincipalLevel(BaseModel):
    """One link of the PrincipalChain (AIL-001 §3.4)."""
    level: int
    principal_type: str                       # natural_person | legal_entity | dao | agent
    principal_id: str                         # gov_id_hash | EIN | DAO_address | KYA_ID
    jurisdiction: str                         # ISO-3166
    verification_method: str                  # id_doc | kyc_provider | attestation | supervised_proofing | notarized_attestation
    attested_at: str                          # ISO-8601 UTC
    attestor_signature: AttestorSignature     # signs this level's attestation payload
    authority: Optional[dict] = None          # entities/DAOs: authorization assertion (PVP-001 §4.2, placeholder shape)
    governance_address: Optional[str] = None  # DAO only (PVP-001 §4.3)


class PrincipalChain(BaseModel):
    """AIL-001 §3.4 PrincipalChain."""
    agent_id: str
    chain: List[PrincipalLevel]
    terminal_principal: str
    max_delegation_depth: int = 3
    binding_proof: AttestorSignature          # terminal principal's AIL-001 §3.2 acceptance
    point_of_contact: Optional[str] = None    # reachability (PVP-001 §5 step 5)


class VerifyResponse(BaseModel):
    verification_hash: str
    principal_id: str
    ial_level: str
    attested_at: str


class PrincipalRecordResponse(BaseModel):
    principal_id: str
    verification_hash: str
    ial_level: str
    attested_at: str
    jurisdiction: str
    status: str                               # verified | lapsed
    principal_chain: dict
