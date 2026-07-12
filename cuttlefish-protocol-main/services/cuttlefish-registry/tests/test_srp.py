"""SRP-001 Stewardship Review lifecycle tests (Sprint 9)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402

import council  # noqa: E402
import srp  # noqa: E402
from council import Candidate  # noqa: E402

DOMAIN = "engineering_review"


def _valid_filing():
    return {
        "attestation_event_ids": ["evt-1"],
        "alleged_defect": "validation missed a structural load case",
        "evidence": [{"hash": "ab" * 32}],
        "harm": "quality risk going forward",
    }


def _pool(n=5):
    return [Candidate(f"sr{i}", "Senior Steward", principal_id=f"p{i}") for i in range(n)]


# --------------------------------------------------------------- intake (§3)


def test_valid_intake_initiates():
    sr = srp.StewardshipReview()
    p = sr.initiate("rev-1", "kya:agent:resp", DOMAIN, _valid_filing())
    assert p.status == "initiated"
    assert sr.emitted[0]["activity_type"] == "STEWARDSHIP_REVIEW_INITIATED"


@pytest.mark.parametrize("missing,reason", [
    ("attestation_event_ids", "no_attestation_events_named"),
    ("alleged_defect", "no_alleged_defect"),
    ("evidence", "no_evidence"),
    ("harm", "no_identified_harm"),
])
def test_incomplete_filing_dismissed_at_intake(missing, reason):
    sr = srp.StewardshipReview()
    filing = _valid_filing()
    filing[missing] = None
    p = sr.initiate("rev-x", "resp", DOMAIN, filing)
    assert p.status == "dismissed_at_intake"
    assert p.finding == {"outcome": "intake_dismissal", "reason": reason}
    assert [e["activity_type"] for e in sr.emitted] == [
        "STEWARDSHIP_REVIEW_INITIATED", "STEWARDSHIP_REVIEW_OUTCOME"]


# --------------------------------------------------------------- panel (§5, AIL-001 §7.2)


def test_form_panel_uses_council_and_emits():
    sr = srp.StewardshipReview()
    sr.initiate("rev-2", "resp", DOMAIN, _valid_filing())
    result = sr.form_panel("rev-2", _pool(5), anchor_seed="anchor-1", size=3)
    p = sr.get("rev-2")
    assert p.status == "panel_formed" and len(p.panel) == 3
    assert result.complete and result.composition_hash
    assert "STEWARDSHIP_REVIEW_PANEL_FORMED" in [e["activity_type"] for e in sr.emitted]


def test_form_panel_insufficient_pool_raises():
    sr = srp.StewardshipReview()
    sr.initiate("rev-3", "resp", DOMAIN, _valid_filing())
    with pytest.raises(srp.SRPError):
        sr.form_panel("rev-3", _pool(2), anchor_seed="s", size=3)


def test_respondent_conflicted_candidate_excluded():
    sr = srp.StewardshipReview()
    sr.initiate("rev-c", "kya:resp", DOMAIN, _valid_filing())
    cands = _pool(4) + [Candidate("conflicted", "Senior Steward", "pX", conflicts={"kya:resp"})]
    res = sr.form_panel("rev-c", cands, anchor_seed="s", size=3)
    assert "conflicted" not in res.members


# --------------------------------------------------------------- full lifecycle (§9-§10)


def _drive_to_deliberation(sr, pid="rev-full"):
    sr.initiate(pid, "resp", DOMAIN, _valid_filing())
    sr.form_panel(pid, _pool(5), anchor_seed="a", size=3)
    sr.open_deliberation(pid)
    return pid


def test_full_lifecycle_with_defect_emits_all_events_in_order():
    sr = srp.StewardshipReview()
    pid = _drive_to_deliberation(sr)
    finding = sr.close_with_finding(pid, yes_votes=2, voting_members=3, standing_action="standing_cap:60")
    assert finding["outcome"] == "finding_of_defect"
    assert sr.get(pid).status == "concluded"
    assert sr.get(pid).history == [
        "STEWARDSHIP_REVIEW_INITIATED",
        "STEWARDSHIP_REVIEW_PANEL_FORMED",
        "STEWARDSHIP_REVIEW_DELIBERATION_OPENED",
        "STEWARDSHIP_REVIEW_DELIBERATION_CLOSED",
        "STEWARDSHIP_REVIEW_OUTCOME",
        "STANDING_ADJUSTED",
    ]


def test_no_defect_emits_no_standing_adjustment():
    sr = srp.StewardshipReview()
    pid = _drive_to_deliberation(sr, "rev-nd")
    finding = sr.close_with_finding(pid, yes_votes=1, voting_members=3, standing_action="standing_cap:60")
    assert finding["outcome"] == "no_defect"
    assert "STANDING_ADJUSTED" not in sr.get(pid).history


def test_preponderance_majority():
    sr = srp.StewardshipReview()
    pid = _drive_to_deliberation(sr, "rev-maj")
    assert sr.close_with_finding(pid, 2, 3)["outcome"] == "finding_of_defect"   # 2/3 majority


def test_heightened_standard_requires_unanimous():
    sr = srp.StewardshipReview()
    p1 = _drive_to_deliberation(sr, "rev-h1")
    assert sr.close_with_finding(p1, 2, 3, standard="heightened")["outcome"] == "no_defect"
    sr2 = srp.StewardshipReview()
    p2 = _drive_to_deliberation(sr2, "rev-h2")
    assert sr2.close_with_finding(p2, 3, 3, standard="heightened")["outcome"] == "finding_of_defect"


# --------------------------------------------------------------- transitions


def test_invalid_transition_raises():
    sr = srp.StewardshipReview()
    sr.initiate("rev-t", "resp", DOMAIN, _valid_filing())
    with pytest.raises(srp.SRPError):
        sr.open_deliberation("rev-t")          # no panel formed yet


def test_unknown_proceeding_raises():
    sr = srp.StewardshipReview()
    with pytest.raises(srp.SRPError):
        sr.open_deliberation("nope")
