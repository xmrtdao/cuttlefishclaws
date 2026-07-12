"""Standing Gate tests — CFL-SPEC-SGQ-001.

The decision composes TrustGraph (TG-001) AND Standing (SS-001). These vectors prove
'fail on either axis': a perfect Standing with a revoked TrustGraph is blocked, and a
healthy TrustGraph with no domain competence is blocked, and every failure is listed.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from storage import ActivityType, RegistryStore  # noqa: E402
from trustgraph import TrustGraphEngine, _parse_ts  # noqa: E402
from standing import StandingEngine  # noqa: E402
from sgq import StandingGate, required_for  # noqa: E402

VC = ActivityType.VALIDATION_COMPLETED
SLASH = ActivityType.SLASH_APPLIED
DOMAIN = "engineering_review"


def _append(store, actor, atype, q=None, unit=None, qty=1, domain=None):
    wu = {"quantity": qty, "unit": unit or "x"}
    if q is not None:
        wu["quality_score"] = q
    if domain is not None:
        wu["rubric_id"] = domain
    store.append_event(
        activity_type=atype,
        primary_actor_id=actor,
        activity_subject={"type": "t", "id": "i"},
        work_unit=wu,
        evidence_hash="0" * 64,
        evidence_uri=None,
        reward_eligibility={},
    )


def _gate_and_asof(tmp_path, actor, builder):
    """Build a store via `builder`, return (gate, as_of=30d after the events)."""
    store = RegistryStore(tmp_path / "sgq.sqlite")
    builder(store, actor)
    gate = StandingGate(TrustGraphEngine(store), StandingEngine(store))
    ev0 = store.list_events(actor_id=actor)[0]["timestamp"]
    as_of = _parse_ts(ev0) + 30 * 86400          # 30 days later -> time-in-domain gate passes
    return gate, as_of


# --------------------------------------------------------------- thresholds


def test_thresholds_raise_bar_for_attestation():
    base = required_for("VALIDATION_COMPLETED", DOMAIN, "developer")
    assert base["min_standing"] == 30.0 and base["min_ladder_tier"] == "Contributor"
    att = required_for("ATTESTATION_ISSUED", DOMAIN, "developer")
    assert att["min_standing"] == 60.0 and att["min_ladder_tier"] == "Builder Steward"
    ent = required_for("VALIDATION_COMPLETED", DOMAIN, "enterprise")
    assert ent["min_ial"] == "IAL3"  # enterprise/anchor need IAL3


# --------------------------------------------------------------- allowed


def test_allowed_both_axes_pass(tmp_path):
    def build(store, actor):
        for _ in range(3):
            _append(store, actor, VC, q=1.0, domain=DOMAIN)
    gate, as_of = _gate_and_asof(tmp_path, "kya:ok", build)
    d = gate.evaluate("kya:ok", "VALIDATION_COMPLETED", DOMAIN, "developer", "IAL2", as_of)
    assert d["allowed"] is True
    assert d["reasons"] == []
    assert d["trustgraph"]["status"] == "ACTIVE"
    assert d["standing"]["value"] == 100.0


# --------------------------------------------------------------- fail on the TrustGraph axis


def test_blocked_by_trustgraph_even_with_perfect_standing(tmp_path):
    def build(store, actor):
        for _ in range(3):
            _append(store, actor, VC, q=1.0, domain=DOMAIN)     # perfect Standing + TG positives
        _append(store, actor, SLASH, unit="injection")          # TG -> REVOKED (no domain tag)
    gate, as_of = _gate_and_asof(tmp_path, "kya:revoked", build)
    d = gate.evaluate("kya:revoked", "VALIDATION_COMPLETED", DOMAIN, "developer", "IAL2", as_of)
    assert d["allowed"] is False
    assert d["trustgraph"]["status"] == "REVOKED"
    assert any(r.startswith("trustgraph_status") for r in d["reasons"])
    # Standing was untouched by the injection slash (no rubric_id) -> still perfect
    assert d["standing"]["value"] == 100.0
    assert not any(r.startswith("standing_below_min") for r in d["reasons"])


# --------------------------------------------------------------- fail on the Standing axis


def test_blocked_by_standing_in_wrong_domain(tmp_path):
    def build(store, actor):
        for _ in range(3):
            _append(store, actor, VC, q=1.0, domain="engineering_review")
    gate, as_of = _gate_and_asof(tmp_path, "kya:wrongdom", build)
    # behaviorally fine, but no competence in materials_science
    d = gate.evaluate("kya:wrongdom", "VALIDATION_COMPLETED", "materials_science", "developer", "IAL2", as_of)
    assert d["allowed"] is False
    assert d["trustgraph"]["status"] == "ACTIVE"          # TG passes
    assert d["standing"]["value"] == 0.0
    assert any(r.startswith("standing_below_min") for r in d["reasons"])
    assert any(r.startswith("ladder_below_min") for r in d["reasons"])


# --------------------------------------------------------------- tier / IAL axes


def test_blocked_by_cac_tier(tmp_path):
    def build(store, actor):
        for _ in range(3):
            _append(store, actor, VC, q=1.0, domain=DOMAIN)
    gate, as_of = _gate_and_asof(tmp_path, "kya:explorer", build)
    d = gate.evaluate("kya:explorer", "VALIDATION_COMPLETED", DOMAIN, "explorer", "IAL2", as_of)
    assert d["allowed"] is False
    assert any(r.startswith("cac_tier_below_min") for r in d["reasons"])


def test_blocked_by_ial(tmp_path):
    def build(store, actor):
        for _ in range(3):
            _append(store, actor, VC, q=1.0, domain=DOMAIN)
    gate, as_of = _gate_and_asof(tmp_path, "kya:ent", build)
    d = gate.evaluate("kya:ent", "VALIDATION_COMPLETED", DOMAIN, "enterprise", "IAL2", as_of)
    assert d["allowed"] is False
    assert any(r.startswith("ial_below_min") for r in d["reasons"])  # enterprise needs IAL3


# --------------------------------------------------------------- no silent denial


def test_multiple_failures_all_listed(tmp_path):
    def build(store, actor):
        _append(store, actor, SLASH, unit="injection")   # TG -> REVOKED; no domain competence
    gate, as_of = _gate_and_asof(tmp_path, "kya:bad", build)
    d = gate.evaluate("kya:bad", "VALIDATION_COMPLETED", DOMAIN, "developer", "IAL2", as_of)
    assert d["allowed"] is False
    assert any(r.startswith("trustgraph_status") for r in d["reasons"])
    assert any(r.startswith("standing_below_min") for r in d["reasons"])
    assert len(d["reasons"]) >= 2   # every failing condition is surfaced
