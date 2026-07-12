"""Endpoint tests for cuttlefish-registry."""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Make the parent directory importable so `main`, `storage`, `schema` resolve
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from fastapi.testclient import TestClient

import kya

# Sprint 3: a test actor keypair + binding used to sign write-path events.
# Not protocol material; generated at module load.
_TEST_PRIV = ed25519.Ed25519PrivateKey.generate()
_TEST_PUB = _TEST_PRIV.public_key().public_bytes_raw()
_TEST_KEY_ID = "test-actor-key"
_DEFAULT_SIGNED_AT = 1_900_000_000   # ~2030; after the test binding's issued_at


def _make_test_binding():
    return kya.KYABinding(
        actor_kind="agent",
        principal_ref=kya.PrincipalRef("operator", "test-op", b"\x00" * 8),
        public_keys=[kya.PublicKeyRef(_TEST_KEY_ID, "ed25519", _TEST_PUB)],
        ial_level="IAL2",
        issued_at="2020-01-01T00:00:00Z",   # old, so a present-day signed_at is valid
    )


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("REGISTRY_DB", str(tmp_path / "test.sqlite"))
    # Force re-import so `app` (and a fresh kya_registry) pick up the new env var
    for mod in ("main", "storage"):
        sys.modules.pop(mod, None)
    import main  # noqa: WPS433
    kya_id = main.kya_registry.register(_make_test_binding())
    c = TestClient(main.app)
    c.test_kya_id = kya_id
    c.test_key_id = _TEST_KEY_ID
    return c


def _write_event(client, **overrides):
    """POST an event, signing it (KYA-001 §4.2) with the test key unless the caller
    overrides a signer field to exercise a failure mode."""
    import main
    from schema import EventWriteRequest

    body = {
        "activity_type": "INFERENCE_CONSUMPTION",
        "primary_actor_id": "kya:test:001",
        "activity_subject": {"type": "run", "id": "run-1"},
        "work_unit": {"quantity": 1234, "unit": "tokens"},
        "evidence_payload": {"hello": "world"},
        "reward_eligibility": {"tier_2_cac": True},
    }
    body.update(overrides)
    body.setdefault("actor_kya_id", getattr(client, "test_kya_id", None))
    body.setdefault("key_id", getattr(client, "test_key_id", None))
    body.setdefault("signed_at", _DEFAULT_SIGNED_AT)
    if "actor_signature" not in body:
        req = EventWriteRequest(**body)
        payload = main.event_request_signing_payload(req)
        body["actor_signature"] = kya.sign_payload(_TEST_PRIV, "ed25519", payload).hex()
    return client.post("/registry/v1/events", json=body)


# ------------------------------------------------------------- write


def test_root_returns_service_info(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["service"] == "cuttlefish-registry"


def test_write_event_returns_event_id_and_hash(client):
    r = _write_event(client)
    assert r.status_code == 201
    data = r.json()
    assert data["event_id"]
    assert len(data["self_hash"]) == 64
    assert data["section_404_category"] == "iii"
    assert "use of any product or service" in data["statutory_anchor"]


def test_write_event_unknown_activity_type_is_400(client):
    r = _write_event(client, activity_type="NOT_A_REAL_TYPE")
    assert r.status_code == 400


def test_write_event_requires_evidence_hash_or_payload(client):
    r = _write_event(client, evidence_payload=None)
    assert r.status_code == 400


def test_write_event_accepts_provided_evidence_hash(client):
    r = _write_event(
        client,
        evidence_payload=None,
        evidence_hash="a" * 64,
    )
    assert r.status_code == 201


# ------------------------------------------------------------- read


def test_get_event_round_trip(client):
    written = _write_event(client).json()
    r = client.get(f"/registry/v1/events/{written['event_id']}")
    assert r.status_code == 200
    fetched = r.json()
    assert fetched["event_id"] == written["event_id"]
    assert fetched["self_hash"] == written["self_hash"]


def test_get_missing_event_is_404(client):
    r = client.get("/registry/v1/events/does-not-exist")
    assert r.status_code == 404


# ------------------------------------------------------------- list


def test_list_events_filters_by_actor(client):
    _write_event(client, primary_actor_id="kya:alice")
    _write_event(client, primary_actor_id="kya:bob")
    _write_event(client, primary_actor_id="kya:alice")

    r = client.get("/registry/v1/events?actor_id=kya:alice")
    assert r.status_code == 200
    events = r.json()["events"]
    assert len(events) == 2
    assert all(e["primary_actor_id"] == "kya:alice" for e in events)


def test_list_events_filters_by_activity_type(client):
    _write_event(client, activity_type="INFERENCE_CONSUMPTION")
    _write_event(client, activity_type="VALIDATION_COMPLETED")

    r = client.get("/registry/v1/events?activity_type=VALIDATION_COMPLETED")
    events = r.json()["events"]
    assert len(events) == 1
    assert events[0]["activity_type"] == "VALIDATION_COMPLETED"


def test_list_events_filters_by_section_404(client):
    _write_event(client, activity_type="INFERENCE_CONSUMPTION")
    _write_event(client, activity_type="CAC_BURN_INFERENCE")  # null category

    r = client.get("/registry/v1/events?section_404=iii")
    assert all(e["section_404_category"] == "iii" for e in r.json()["events"])

    r2 = client.get("/registry/v1/events?section_404=null")
    assert all(e["section_404_category"] == "null" for e in r2.json()["events"])


# ------------------------------------------------------------- chain


def test_chain_head_advances(client):
    r1 = client.get("/registry/v1/chain/cfl-main/head")
    assert r1.json()["head_hash"] == ""

    first = _write_event(client).json()
    r2 = client.get("/registry/v1/chain/cfl-main/head")
    assert r2.json()["head_hash"] == first["self_hash"]

    second = _write_event(client).json()
    r3 = client.get("/registry/v1/chain/cfl-main/head")
    assert r3.json()["head_hash"] == second["self_hash"]


def test_second_event_chains_from_first(client):
    first = _write_event(client).json()
    second = _write_event(client).json()
    second_full = client.get(f"/registry/v1/events/{second['event_id']}").json()
    assert second_full["prev_event_hash"] == first["self_hash"]


# ------------------------------------------------------------- compliance


def test_compliance_report_counts_categories(client):
    _write_event(client, activity_type="INFERENCE_CONSUMPTION")  # iii
    _write_event(client, activity_type="VALIDATION_COMPLETED")   # iii
    _write_event(client, activity_type="CAC_BURN_INFERENCE")     # null
    _write_event(client, activity_type="PAYMENT_SETTLEMENT")     # i

    r = client.get(
        "/registry/v1/compliance/section-404"
        "?from=2020-01-01T00:00:00Z&to=2099-01-01T00:00:00Z"
    )
    counts = r.json()["event_counts_by_category"]
    assert counts["iii"] == 2
    assert counts["i"] == 1
    assert counts["null"] == 1
    assert counts["ii"] == 0


# ------------------------- CFL-NARR-003 §5 detection events (Sprint 1, additive) -------------

_NARR003_DETECTIONS = [
    "SOCIAL_ENGINEERING_DETECTED",
    "IDENTITY_FISHING_DETECTED",
    "COORDINATED_PROBING_DETECTED",
    "TRUST_MANIPULATION_DETECTED",
    "IDENTITY_INCONSISTENCY_DETECTED",
]


@pytest.mark.parametrize("detection", _NARR003_DETECTIONS)
def test_narr003_detection_event_round_trips(client, detection):
    """Each new CFL-NARR-003 §5 ActivityType is accepted, stored, and round-trips."""
    written = _write_event(client, activity_type=detection)
    assert written.status_code == 201, written.text
    event_id = written.json()["event_id"]

    fetched = client.get(f"/registry/v1/events/{event_id}").json()
    assert fetched["activity_type"] == detection

    listed = client.get(f"/registry/v1/events?activity_type={detection}").json()["events"]
    assert len(listed) == 1
    assert listed[0]["activity_type"] == detection


# ------------------------- KYA-001 §4.2 write-path signatures (Sprint 3) -------------------


def test_kya_valid_signature_accepted(client):
    r = _write_event(client)
    assert r.status_code == 201, r.text


def test_kya_invalid_signature_rejected_401(client):
    r = _write_event(client, actor_signature="00" * 64)  # valid hex, wrong signature
    assert r.status_code == 401
    assert "signature" in r.json()["detail"]


def test_kya_missing_actor_kya_id_400(client):
    r = _write_event(client, actor_kya_id=None)
    assert r.status_code == 400


def test_kya_unknown_actor_kya_id_404(client):
    r = _write_event(client, actor_kya_id="kya:agent:does-not-exist")
    assert r.status_code == 404


def test_kya_revoked_key_rejected_401(client):
    import main
    assert main.kya_registry.revoke(client.test_kya_id, client.test_key_id)
    r = _write_event(client)
    assert r.status_code == 401
    assert "revoked" in r.json()["detail"]


def test_kya_signed_at_before_key_issued_at_401(client):
    # binding issued_at is 2020-01-01; sign with a signed_at well before that
    r = _write_event(client, signed_at=1_000_000_000)  # 2001
    assert r.status_code == 401
    assert "signed_before_issued" in r.json()["detail"]
