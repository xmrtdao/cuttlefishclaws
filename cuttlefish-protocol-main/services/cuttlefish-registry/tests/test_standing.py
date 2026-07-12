"""Stewardship Standing engine tests — CFL-SPEC-SS-001 §13.

Deterministic: every case pins `as_of`. Includes the cross-domain ISOLATION
vector (§3) — an engineering_review zero-out must NOT affect arbitration_reliability.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from storage import ActivityType, RegistryStore  # noqa: E402
from standing import (  # noqa: E402
    COUNCIL_DAYS,
    COUNCIL_STANDING,
    StandingEngine,
    compute_standing,
    event_domain,
    ladder_tier,
    _parse_ts,
)

VC = ActivityType.VALIDATION_COMPLETED.value
REVIEW = ActivityType.STEWARDSHIP_REVIEW_OUTCOME.value

T0 = _parse_ts("2026-01-01T00:00:00Z")


def at(days: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(int(T0 + days * 86400)))


def qev(days: float, q: float = 1.0, domain: str = "engineering_review") -> dict:
    return {
        "activity_type": VC,
        "timestamp": at(days),
        "work_unit": {"quantity": 1, "unit": "review", "quality_score": q, "rubric_id": domain},
    }


def review(days: float, unit: str, value: float = 0.0, domain: str = "engineering_review") -> dict:
    return {
        "activity_type": REVIEW,
        "timestamp": at(days),
        "work_unit": {"quantity": value, "unit": unit, "rubric_id": domain},
    }


# --------------------------------------------------------------- helpers


def test_event_domain_and_ladder_gates():
    assert event_domain(qev(0, domain="materials_science")) == "materials_science"
    assert event_domain({"work_unit": {}}) is None
    # both gates required
    assert ladder_tier(100, 35, provisional=False, has_events=True) == "Builder Steward"
    assert ladder_tier(100, 5, provisional=False, has_events=True) == "Participant"   # time gate fails
    assert ladder_tier(25, 200, provisional=False, has_events=True) == "Participant"  # value gate fails
    assert ladder_tier(95, 200, provisional=False, has_events=True) == "Senior Steward"
    assert ladder_tier(0, 0, provisional=False, has_events=False) == "Participant"


# --------------------------------------------------------------- EWMA


def test_no_events_is_participant_zero():
    r = compute_standing([], as_of=int(T0))
    assert r["standing"] == 0.0
    assert r["ladder_tier"] == "Participant"
    assert r["event_count"] == 0


def test_quality_average_same_time():
    evs = [qev(10, 1.0), qev(10, 0.5), qev(10, 0.0)]  # equal weights -> mean
    r = compute_standing(evs, as_of=_parse_ts(at(10)))
    assert r["standing"] == 50.0
    assert r["provisional"] is False  # 3 events


def test_recency_weighting_recent_dominates():
    # old perfect (weight 0.5 at one half-life) + recent zero (weight 1.0)
    evs = [qev(0, 1.0), qev(90, 0.0)]
    r = compute_standing(evs, as_of=_parse_ts(at(90)))
    assert r["standing"] == 33.33  # 0.5/1.5
    assert r["provisional"] is True  # only 2 events


def test_volume_gaming_fails_quality_average():
    # 10 low-quality events cannot inflate Standing (it's an average, not a sum)
    evs = [qev(d, 0.2) for d in range(10)]
    r = compute_standing(evs, as_of=_parse_ts(at(9)))
    assert r["standing"] <= 20.0


# --------------------------------------------------------------- ladder


def test_ladder_builder_steward_value_and_time():
    evs = [qev(0), qev(1), qev(35)]  # q=1 -> standing 100 regardless of weights
    r = compute_standing(evs, as_of=_parse_ts(at(35)))
    assert r["standing"] == 100.0
    assert r["time_in_domain_days"] == 35.0
    assert r["ladder_tier"] == "Builder Steward"   # >=30d & >=60; Senior needs 90d


def test_provisional_caps_ladder_at_contributor():
    evs = [qev(0), qev(35)]  # standing 100 but only 2 events -> provisional
    r = compute_standing(evs, as_of=_parse_ts(at(35)))
    assert r["provisional"] is True
    assert r["ladder_tier"] == "Contributor"   # would be Builder Steward but provisional


# --------------------------------------------------------------- caps / set / restore (§6)


def test_review_cap():
    evs = [qev(0), qev(1), qev(2), review(5, "standing_cap", 40)]
    r = compute_standing(evs, as_of=_parse_ts(at(5)))
    assert r["standing"] == 40.0
    assert r["active_cap"] == 40.0


def test_off_protocol_set_zero():
    evs = [qev(0), qev(1), qev(2), review(5, "standing_set", 0)]
    r = compute_standing(evs, as_of=_parse_ts(at(5)))
    assert r["standing"] == 0.0


def test_restore_lifts_cap():
    evs = [qev(0), qev(1), qev(2), review(5, "standing_cap", 40), review(6, "standing_restore")]
    r = compute_standing(evs, as_of=_parse_ts(at(6)))
    assert r["standing"] == 100.0


# --------------------------------------------------------------- CROSS-DOMAIN ISOLATION (§3)


def test_cross_domain_isolation_pure():
    eng = [qev(0, 1.0, "engineering_review"), qev(1, 1.0, "engineering_review"),
           qev(2, 1.0, "engineering_review"), review(5, "standing_set", 0, "engineering_review")]
    arb = [qev(0, 1.0, "arbitration_reliability"), qev(1, 1.0, "arbitration_reliability"),
           qev(2, 1.0, "arbitration_reliability")]
    as_of = _parse_ts(at(5))
    # compute each domain ONLY from its own events
    assert compute_standing(eng, as_of=as_of)["standing"] == 0.0
    assert compute_standing(arb, as_of=as_of)["standing"] == 100.0


def test_cross_domain_isolation_via_engine(tmp_path):
    store = RegistryStore(tmp_path / "ss.sqlite")
    actor = "kya:test:steward"

    def append(atype, q=None, unit=None, qty=1, domain="engineering_review"):
        wu = {"quantity": qty, "unit": unit or "review", "rubric_id": domain}
        if q is not None:
            wu["quality_score"] = q
        store.append_event(
            activity_type=atype,
            primary_actor_id=actor,
            activity_subject={"type": "task", "id": "t"},
            work_unit=wu,
            evidence_hash="0" * 64,
            evidence_uri=None,
            reward_eligibility={},
        )

    for _ in range(3):
        append(ActivityType.VALIDATION_COMPLETED, q=1.0, domain="engineering_review")
    for _ in range(3):
        append(ActivityType.VALIDATION_COMPLETED, q=1.0, domain="arbitration_reliability")
    # zero out engineering_review only
    append(ActivityType.STEWARDSHIP_REVIEW_OUTCOME, unit="standing_set", qty=0, domain="engineering_review")

    engine = StandingEngine(store)
    as_of = _parse_ts(store.list_events(actor_id=actor)[0]["timestamp"])
    alld = engine.all_domains(actor, as_of=as_of)

    assert alld["domains"]["engineering_review"]["standing"] == 0.0
    assert alld["domains"]["arbitration_reliability"]["standing"] == 100.0  # UNAFFECTED
    assert alld["council_eligible"] is False  # near-now, time gate not met

    # single-domain read agrees
    assert engine.domain(actor, "arbitration_reliability", as_of=as_of)["standing"] == 100.0


def test_council_eligible_threshold_components():
    # a domain with >180d span and perfect quality reaches Senior + council component
    evs = [qev(0), qev(1), qev(COUNCIL_DAYS + 1)]
    r = compute_standing(evs, as_of=_parse_ts(at(COUNCIL_DAYS + 1)))
    assert r["standing"] >= COUNCIL_STANDING
    assert r["time_in_domain_days"] >= COUNCIL_DAYS
    assert r["ladder_tier"] == "Senior Steward"
