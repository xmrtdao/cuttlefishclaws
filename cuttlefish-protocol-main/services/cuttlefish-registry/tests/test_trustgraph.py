"""TrustGraph engine tests — CFL-SPEC-TG-001 §13 (test vectors).

Deterministic: every case pins `as_of` so decay/caps/asymmetry are exact.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from storage import ActivityType, RegistryStore  # noqa: E402
from trustgraph import (  # noqa: E402
    WEEK_SECONDS,
    TrustGraphEngine,
    band_and_status,
    compute_score,
    delta_for,
    _parse_ts,
)

VC = ActivityType.VALIDATION_COMPLETED.value
PROP = ActivityType.GOVERNANCE_PROPOSAL_AUTHORED.value
INF = ActivityType.INFERENCE_CONSUMPTION.value
SLASH = ActivityType.SLASH_APPLIED.value


def ev(atype: str, ts: str, unit: str = "x") -> dict:
    return {
        "activity_type": atype,
        "timestamp": ts,
        "work_unit": {"quantity": 1, "unit": unit},
    }


def ts(day: int, hour: int = 0) -> str:
    return f"2026-01-{day:02d}T{hour:02d}:00:00Z"


# --------------------------------------------------------------- rubric


def test_delta_lookup():
    assert delta_for(ev(VC, ts(1))) == 3.0
    assert delta_for(ev(PROP, ts(1))) == 5.0
    assert delta_for(ev(INF, ts(1))) == 0.05
    assert delta_for(ev(SLASH, ts(1), unit="injection")) == -50.0
    assert delta_for(ev(SLASH, ts(1), unit="fabrication")) == -25.0
    assert delta_for(ev(SLASH, ts(1))) == -15.0  # default == minor
    assert delta_for(ev("UNKNOWN_TYPE", ts(1))) == 0.0


def test_bands():
    assert band_and_status(95) == ("Trusted", "ACTIVE")
    assert band_and_status(75) == ("Standard", "ACTIVE")
    assert band_and_status(55) == ("Monitored", "ACTIVE")
    assert band_and_status(30) == ("Cautious", "ACTIVE")
    assert band_and_status(15) == ("Suspended", "SUSPENDED")
    assert band_and_status(5) == ("Revoked", "REVOKED")


# --------------------------------------------------------------- seed / accrual


def test_seed_is_tier_floor():
    r = compute_score([], tier="developer")
    assert r["score"] == 30.0
    assert r["band"] == "Cautious"
    assert r["below_floor"] is False


def test_positive_accrual_no_decay():
    evs = [ev(VC, ts(1)), ev(VC, ts(2)), ev(VC, ts(3))]
    r = compute_score(evs, tier="developer", as_of=_parse_ts(ts(3)))
    assert r["score"] == 39.0  # 30 + 3*3, no decay


# --------------------------------------------------------------- asymmetry


def test_asymmetry_attenuates_above_ceiling():
    # anchor floor 70; 5 proposals (+5). 4 reach exactly 90, the 5th is halved -> +2.5
    evs = [ev(PROP, ts(d)) for d in range(1, 6)]
    r = compute_score(evs, tier="anchor", as_of=_parse_ts(ts(5)))
    assert r["score"] == 92.5
    assert r["band"] == "Trusted"


def test_clamp_at_100():
    evs = [ev(PROP, ts(1, h)) for h in range(20)]
    r = compute_score(evs, tier="anchor", as_of=_parse_ts(ts(1, 19)))
    assert r["score"] == 100.0


# --------------------------------------------------------------- negatives


def test_violation_can_drop_below_tier_floor_without_suspension():
    evs = [ev(VC, ts(1, h)) for h in range(9)] + [ev(SLASH, ts(2), unit="injection")]
    r = compute_score(evs, tier="enterprise", as_of=_parse_ts(ts(2)))
    assert r["score"] == 32.0  # 55 + 27 - 50
    assert r["below_floor"] is True
    assert r["status"] == "ACTIVE"
    assert r["band"] == "Cautious"


def test_minor_violation_suspends():
    r = compute_score([ev(SLASH, ts(1), unit="violation_minor")], tier="developer", as_of=_parse_ts(ts(1)))
    assert r["score"] == 15.0  # 30 - 15
    assert r["status"] == "SUSPENDED"


def test_injection_revokes():
    r = compute_score([ev(SLASH, ts(1), unit="injection")], tier="developer", as_of=_parse_ts(ts(1)))
    assert r["score"] == 0.0  # max(0, 30 - 50)
    assert r["status"] == "REVOKED"


# --------------------------------------------------------------- decay


def test_decay_erodes_surplus_then_floors():
    evs = [ev(VC, ts(d)) for d in range(1, 6)]  # studio floor 40 -> 55
    last = _parse_ts(ts(5))
    assert compute_score(evs, tier="studio", as_of=last)["score"] == 55.0
    assert compute_score(evs, tier="studio", as_of=last + 3 * WEEK_SECONDS)["score"] == 49.0  # -6
    assert compute_score(evs, tier="studio", as_of=last + 100 * WEEK_SECONDS)["score"] == 40.0  # floored


# --------------------------------------------------------------- caps


def test_micro_daily_cap():
    evs = [ev(INF, ts(1)) for _ in range(250)]  # raw +12.5, capped +10
    r = compute_score(evs, tier="developer", as_of=_parse_ts(ts(1)))
    assert r["score"] == 40.0


# --------------------------------------------------------------- determinism


def test_deterministic_under_reordering():
    evs = [
        ev(VC, ts(1)), ev(PROP, ts(2)), ev(SLASH, ts(3), unit="violation_minor"),
        ev(VC, ts(4)), ev(INF, ts(5)),
    ]
    as_of = _parse_ts(ts(5))
    s1 = compute_score(evs, tier="studio", as_of=as_of)["score"]
    s2 = compute_score(list(reversed(evs)), tier="studio", as_of=as_of)["score"]
    assert s1 == s2


# --------------------------------------------------------------- engine + store


def test_engine_over_registry_store(tmp_path):
    store = RegistryStore(tmp_path / "tg.sqlite")
    actor = "kya:test:eng"
    for _ in range(3):
        store.append_event(
            activity_type=ActivityType.VALIDATION_COMPLETED,
            primary_actor_id=actor,
            activity_subject={"type": "task", "id": "t"},
            work_unit={"quantity": 1, "unit": "review"},
            evidence_hash="0" * 64,
            evidence_uri=None,
            reward_eligibility={},
        )
    engine = TrustGraphEngine(store)
    # as_of just after the events so decay is negligible (rounds to 0)
    r = engine.score(actor, tier="developer", as_of=_parse_ts(store.list_events(actor_id=actor)[0]["timestamp"]))
    assert r["score"] == 39.0
    assert r["event_count"] == 3
    assert r["agent"] == actor

    # an unrelated actor with no events seeds at floor
    empty = engine.score("kya:test:nobody", tier="studio")
    assert empty["score"] == 40.0
