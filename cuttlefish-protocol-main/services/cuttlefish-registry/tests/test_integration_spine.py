"""End-to-end protocol spine (Sprint 11).

Proves the registry-internal pipeline composes as one system:

    KYA identity binding  →  signed AR-001 event (write path)  →  TrustGraph (behavioral)
    + Stewardship Standing (competence)  →  SGQ Standing Gate decision  →  reward eligibility (for RRC).

One agent does one validation; we then read its TrustGraph score, its domain Standing, and the
gate decision, and confirm the event carries the reward flags RRC-001 would route on.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from fastapi.testclient import TestClient

import kya

DOMAIN = "engineering_review"
FUTURE = 2_000_000_000   # well after the event's write time (matures the Standing ladder)

_PRIV = ed25519.Ed25519PrivateKey.generate()
_PUB = _PRIV.public_key().public_bytes_raw()
_KEY_ID = "spine-key"


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("REGISTRY_DB", str(tmp_path / "spine.sqlite"))
    for mod in ("main", "storage"):
        sys.modules.pop(mod, None)
    import main
    binding = kya.KYABinding(
        actor_kind="agent",
        principal_ref=kya.PrincipalRef("operator", "spine-op", b"\x00" * 8),
        public_keys=[kya.PublicKeyRef(_KEY_ID, "ed25519", _PUB)],
        ial_level="IAL2",
        issued_at="2020-01-01T00:00:00Z",
    )
    kya_id = main.kya_registry.register(binding)
    c = TestClient(main.app)
    c.kya_id = kya_id
    return c


def _post_signed_validation(client):
    import main
    from schema import EventWriteRequest
    body = {
        "activity_type": "VALIDATION_COMPLETED",
        "primary_actor_id": client.kya_id,          # actor == its own KYA_ID for the spine
        "activity_subject": {"type": "proposal", "id": "p-1"},
        "work_unit": {"quantity": 1, "unit": "review", "quality_score": 1.0, "rubric_id": DOMAIN},
        "evidence_payload": {"report": "load cases checked"},
        "reward_eligibility": {"tier_1_usdc": True, "tier_2_cac": True},
        "actor_kya_id": client.kya_id,
        "key_id": _KEY_ID,
        "signed_at": 1_900_000_000,
    }
    req = EventWriteRequest(**body)
    body["actor_signature"] = kya.sign_payload(_PRIV, "ed25519", main.event_request_signing_payload(req)).hex()
    return client.post("/registry/v1/events", json=body)


def test_spine_identity_event_scores_gate(client):
    # 1. KYA-signed validation event is accepted by the AR-001 write path
    written = _post_signed_validation(client)
    assert written.status_code == 201, written.text
    assert written.json()["section_404_category"] == "iii"   # §404 ecosystem participation

    actor = client.kya_id

    # 2. TrustGraph reflects the validation (+3 over the developer floor 30), behavioral axis
    tg = client.get(f"/trustgraph/v1/{actor}?tier=developer").json()
    assert tg["score"] == 33.0 and tg["status"] == "ACTIVE"

    # 3. Stewardship Standing reflects it in the domain (competence axis), matured by as_of
    ss = client.get(f"/standing/v1/{actor}/{DOMAIN}?as_of={FUTURE}").json()
    assert ss["standing"] == 100.0 and ss["domain"] == DOMAIN

    # 4. The Standing Gate composes both axes and authorizes the activity (fail-on-either AND)
    gate = client.post("/gate/v1/evaluate", json={
        "actor_kya_id": actor, "activity_type": "VALIDATION_COMPLETED",
        "domain": DOMAIN, "cac_tier": "developer", "ial": "IAL2", "as_of": FUTURE,
    }).json()
    assert gate["allowed"] is True, gate["reasons"]
    assert "trustgraph" in gate and "standing" in gate

    # 5. The event carries the reward flags RRC-001 routes on (Tier 1 USDC + Tier 2 CAC)
    ev = client.get(f"/registry/v1/events/{written.json()['event_id']}").json()
    assert ev["reward_eligibility"]["tier_1_usdc"] is True
    assert ev["reward_eligibility"]["tier_2_cac"] is True


def test_spine_unsigned_event_is_rejected(client):
    # the gate/economy can never see work that the identity layer didn't authorize
    r = client.post("/registry/v1/events", json={
        "activity_type": "VALIDATION_COMPLETED",
        "primary_actor_id": client.kya_id,
        "activity_subject": {"type": "proposal", "id": "p-2"},
        "work_unit": {"quantity": 1, "unit": "review"},
        "evidence_payload": {"x": 1},
        "reward_eligibility": {"tier_1_usdc": True},
        # no actor_kya_id / signature
    })
    assert r.status_code == 400   # missing actor_kya_id -> rejected before any reward path
