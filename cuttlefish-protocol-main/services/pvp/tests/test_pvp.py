"""PVP-001 service tests (Sprint 4). Protocol-internal structural verification."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # services/pvp

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from fastapi.testclient import TestClient

import pvp          # importing pvp puts services/cuttlefish-registry on sys.path for `kya`
import kya
import main
import storage
from schema import AttestorSignature, PrincipalChain, PrincipalLevel

# --- test keypairs (not protocol material) ---
PERSON_PRIV = ed25519.Ed25519PrivateKey.generate()
ENTITY_PRIV = ed25519.Ed25519PrivateKey.generate()
BINDING_PRIV = ed25519.Ed25519PrivateKey.generate()
_PLACEHOLDER = AttestorSignature(algorithm="ed25519", public_key="00", signature="00")


def _sign_struct(priv, payload) -> AttestorSignature:
    return AttestorSignature(
        algorithm="ed25519",
        public_key=priv.public_key().public_bytes_raw().hex(),
        signature=kya.sign_payload(priv, "ed25519", payload).hex(),
    )


def _level(level_no, ptype, pid, priv, method="attestation", jur="US-CA", authority=None, gov=None):
    lvl = PrincipalLevel(
        level=level_no, principal_type=ptype, principal_id=pid, jurisdiction=jur,
        verification_method=method, attested_at="2026-06-28T00:00:00Z",
        attestor_signature=_PLACEHOLDER, authority=authority, governance_address=gov,
    )
    lvl.attestor_signature = _sign_struct(priv, pvp.level_attestation_payload(lvl))
    return lvl


def _chain(levels, terminal_pid, binding_priv=BINDING_PRIV, poc="legal@example.com", max_depth=3):
    ch = PrincipalChain(
        agent_id="kya:agent:test", chain=levels, terminal_principal=terminal_pid,
        max_delegation_depth=max_depth, binding_proof=_PLACEHOLDER, point_of_contact=poc,
    )
    ch.binding_proof = _sign_struct(binding_priv, pvp.binding_payload(ch))
    return ch


def _natural_person_chain():
    lvl = _level(0, "natural_person", "person-1", PERSON_PRIV)
    return _chain([lvl], "person-1")


def _legal_entity_chain():
    lvl = _level(0, "legal_entity", "EIN-123", ENTITY_PRIV, authority={"role": "officer", "doc": "board_resolution"})
    return _chain([lvl], "EIN-123")


@pytest.fixture(autouse=True)
def mock_emit(monkeypatch):
    """Mock the registry HTTP emission — no live registry needed."""
    recorded = []
    monkeypatch.setattr(pvp, "emit_hook", lambda payload: (recorded.append(payload), {"status_code": 201})[1])
    return recorded


@pytest.fixture
def client():
    main.store = storage.PrincipalStore()   # fresh store per test
    return TestClient(main.app)


# --------------------------------------------------------------- accept


def test_valid_natural_person_chain_accepted(client):
    r = client.post("/pvp/v1/verify", json=_natural_person_chain().model_dump())
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["verification_hash"]) == 64
    assert body["principal_id"] == "person-1"
    assert body["ial_level"] == "IAL2"


def test_valid_legal_entity_chain_with_authority_accepted(client):
    r = client.post("/pvp/v1/verify", json=_legal_entity_chain().model_dump())
    assert r.status_code == 200, r.text
    assert r.json()["principal_id"] == "EIN-123"


# --------------------------------------------------------------- reject


def test_chain_depth_exceeds_3_rejected(client):
    levels = [_level(i, "agent", f"agent-{i}", PERSON_PRIV) for i in range(3)]
    levels.append(_level(3, "natural_person", "person-1", PERSON_PRIV))   # depth 4
    ch = _chain(levels, "person-1")
    r = client.post("/pvp/v1/verify", json=ch.model_dump())
    assert r.status_code == 422 and "depth_exceeds_max" in r.text


def test_chain_not_terminating_at_person_or_entity_rejected(client):
    lvl = _level(0, "agent", "agent-x", PERSON_PRIV)   # terminal is an agent
    ch = _chain([lvl], "agent-x")
    r = client.post("/pvp/v1/verify", json=ch.model_dump())
    assert r.status_code == 422 and "terminal_not_natural_or_legal" in r.text


def test_attestation_signature_failure_rejected(client):
    ch = _natural_person_chain()
    ch.chain[0].attestor_signature.signature = "00" * 64   # break the signature
    r = client.post("/pvp/v1/verify", json=ch.model_dump())
    assert r.status_code == 422 and "attestation_invalid" in r.text


def test_binding_proof_invalid_rejected(client):
    ch = _natural_person_chain()
    ch.binding_proof.signature = "00" * 64
    r = client.post("/pvp/v1/verify", json=ch.model_dump())
    assert r.status_code == 422 and "binding_proof_invalid" in r.text


def test_dao_without_governance_address_rejected(client):
    # DAO is not a terminal type, so put it at level 0 with a natural_person terminal at level 1
    dao = _level(0, "dao", "dao-1", ENTITY_PRIV, authority={"wrapper": "WY-DAO-LLC"}, gov=None)
    person = _level(1, "natural_person", "person-1", PERSON_PRIV)
    ch = _chain([dao, person], "person-1")
    r = client.post("/pvp/v1/verify", json=ch.model_dump())
    assert r.status_code == 422 and "governance_address_missing" in r.text


def test_reachability_missing_rejected(client):
    ch = _chain([_level(0, "natural_person", "person-1", PERSON_PRIV)], "person-1", poc=None)
    r = client.post("/pvp/v1/verify", json=ch.model_dump())
    assert r.status_code == 422 and "reachability_missing" in r.text


# --------------------------------------------------------------- assurance / emission / lifecycle


def test_ial3_for_supervised_proofing(client):
    lvl = _level(0, "natural_person", "person-1", PERSON_PRIV, method="supervised_proofing")
    r = client.post("/pvp/v1/verify", json=_chain([lvl], "person-1").model_dump())
    assert r.status_code == 200
    assert r.json()["ial_level"] == "IAL3"


def test_kya_registration_emitted(client, mock_emit):
    client.post("/pvp/v1/verify", json=_natural_person_chain().model_dump())
    assert len(mock_emit) == 1
    assert mock_emit[0]["activity_type"] == "KYA_REGISTRATION"
    assert mock_emit[0]["primary_actor_id"] == "person-1"


def test_idempotency_same_chain_same_hash(client):
    ch = _natural_person_chain().model_dump()
    h1 = client.post("/pvp/v1/verify", json=ch).json()["verification_hash"]
    h2 = client.post("/pvp/v1/verify", json=ch).json()["verification_hash"]
    assert h1 == h2


def test_revocation_marks_lapsed(client):
    client.post("/pvp/v1/verify", json=_natural_person_chain().model_dump())
    assert client.get("/pvp/v1/principals/person-1").json()["status"] == "verified"
    r = client.post("/pvp/v1/principals/person-1/revoke")
    assert r.status_code == 200 and r.json()["status"] == "lapsed"
    assert client.get("/pvp/v1/principals/person-1").json()["status"] == "lapsed"


def test_get_unknown_principal_404(client):
    assert client.get("/pvp/v1/principals/nobody").status_code == 404
