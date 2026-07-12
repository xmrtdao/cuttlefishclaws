"""RRC-001 Reward Router tests (Sprint 5). Distribution is record-only; write-backs mocked."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))   # services/rrc

import pytest
from fastapi.testclient import TestClient

import main
import rrc
import storage


@pytest.fixture(autouse=True)
def mock_emit(monkeypatch):
    """Mock the registry write-back HTTP — no live registry needed."""
    recorded = []
    monkeypatch.setattr(rrc, "emit_hook", lambda payload: (recorded.append(payload), {"status_code": 201})[1])
    return recorded


@pytest.fixture
def client():
    main.store = storage.RouterStore()   # fresh store per test
    return TestClient(main.app)


def _event(event_id="evt-1", activity_type="VALIDATION_COMPLETED", section="iii", quantity=1,
           quality=None, **elig):
    return {
        "event_id": event_id,
        "activity_type": activity_type,
        "section_404_category": section,
        "primary_actor_id": "kya:agent:1",
        "work_unit": {"quantity": quantity, "unit": "review", "quality_score": quality},
        "reward_eligibility": {
            "tier_1_usdc": elig.get("t1", False),
            "tier_2_cac": elig.get("t2", False),
            "tier_3_governance": elig.get("t3", False),
            "tier_4_e2r": elig.get("t4", False),
        },
    }


def _route(client, **kw):
    return client.post("/router/v1/events", json=_event(**kw)).json()


# --------------------------------------------------------------- tiers 1-2 (mocked)


def test_tier1_usdc_recorded_with_writeback(client, mock_emit):
    out = _route(client, t1=True)
    assert out["status"] == "routed"
    d = [x for x in out["distributions"] if x["tier"] == "tier_1_usdc"][0]
    assert d["rail"] == "utility" and d["status"] == "recorded"
    assert d["amount_usdc"] == 5.0           # base 5 * qty 1 * quality 1.0
    assert d["writeback_event_type"] == "PAYMENT_SETTLEMENT"
    assert any(p["activity_type"] == "PAYMENT_SETTLEMENT" for p in mock_emit)


def test_tier2_cac_recorded_with_writeback(client, mock_emit):
    out = _route(client, t2=True)
    d = [x for x in out["distributions"] if x["tier"] == "tier_2_cac"][0]
    assert d["credit_units"] == 1000 and d["writeback_event_type"] == "CAC_TOPUP"
    assert any(p["activity_type"] == "CAC_TOPUP" for p in mock_emit)


def test_both_tier1_and_tier2(client):
    out = _route(client, t1=True, t2=True)
    tiers = {d["tier"] for d in out["distributions"]}
    assert tiers == {"tier_1_usdc", "tier_2_cac"}


# --------------------------------------------------------------- idempotency / §404


def test_idempotency_no_double_pay(client, mock_emit):
    first = _route(client, event_id="dup-1", t1=True)
    assert first["status"] == "routed"
    second = _route(client, event_id="dup-1", t1=True)
    assert second["status"] == "duplicate" and second["distributions"] == []
    # only one PAYMENT_SETTLEMENT emitted across both calls
    assert sum(1 for p in mock_emit if p["activity_type"] == "PAYMENT_SETTLEMENT") == 1


def test_tier1_refused_when_section_404_null(client, mock_emit):
    out = _route(client, t1=True, section="null", activity_type="CAC_BURN_INFERENCE")
    assert out["status"] == "no_reward"
    assert not any(d["tier"] == "tier_1_usdc" for d in out["distributions"])
    assert not any(p["activity_type"] == "PAYMENT_SETTLEMENT" for p in mock_emit)


def test_no_eligibility_is_no_reward(client):
    out = _route(client)   # no tier flags
    assert out["status"] == "no_reward" and out["distributions"] == []


# --------------------------------------------------------------- tiers 3-4 (stubbed) + rail separation


def test_tier3_governance_stubbed(client):
    out = _route(client, t3=True)
    d = [x for x in out["distributions"] if x["tier"] == "tier_3_governance"][0]
    assert d["status"] == "stubbed" and d["rail"] == "none"


def test_tier4_e2r_stubbed_on_securities_rail_never_payment(client, mock_emit):
    out = _route(client, t4=True)
    d = [x for x in out["distributions"] if x["tier"] == "tier_4_e2r"][0]
    assert d["status"] == "stubbed" and d["rail"] == "securities"
    # load-bearing (§5.4): a Tier-4 event must NOT reach the utility payment rail
    assert not any(p["activity_type"] == "PAYMENT_SETTLEMENT" for p in mock_emit)


# --------------------------------------------------------------- amounts / ops


def test_usdc_amount_clamped_to_cap(client):
    out = _route(client, t1=True, quantity=1000)   # 5 * 1000 = 5000 -> capped at 100
    d = [x for x in out["distributions"] if x["tier"] == "tier_1_usdc"][0]
    assert d["amount_usdc"] == 100.0


def test_quality_multiplier_applied(client):
    out = _route(client, t1=True, quality=0.5)   # 5 * 1 * 0.5 = 2.5
    d = [x for x in out["distributions"] if x["tier"] == "tier_1_usdc"][0]
    assert d["amount_usdc"] == 2.5


def test_get_distributions_endpoint(client):
    _route(client, event_id="look-1", t2=True)
    r = client.get("/router/v1/distributions?event_id=look-1")
    assert r.status_code == 200 and len(r.json()["distributions"]) == 1
    assert client.get("/router/v1/distributions?event_id=nope").status_code == 404


def test_ratecard_and_health_endpoints(client):
    card = client.get("/router/v1/ratecard").json()
    assert card["version"] == "ratecard-001-pilot-PLACEHOLDER-v0"
    assert card["currency"] == "USDC"
    h = client.get("/router/v1/health").json()
    assert h["status"] == "ok" and h["ratecard_version"] == card["version"]


def test_ratecard_pinned_by_event_timestamp(client):
    body = _event(event_id="ts-1", t1=True)
    body["timestamp"] = "2026-03-01T00:00:00Z"   # after the placeholder card's effective_from
    out = client.post("/router/v1/events", json=body).json()
    d = [x for x in out["distributions"] if x["tier"] == "tier_1_usdc"][0]
    assert d["ratecard_version"] == "ratecard-001-pilot-PLACEHOLDER-v0"
