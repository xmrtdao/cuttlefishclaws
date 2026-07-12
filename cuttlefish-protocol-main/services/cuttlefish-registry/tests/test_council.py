"""CC-001 Council panel-composition + supermajority/timelock tests (Sprint 8)."""

from __future__ import annotations

import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import council  # noqa: E402
from council import Candidate  # noqa: E402

DOMAIN = "engineering_review"


def _pool(n=8, tier="Senior Steward"):
    # distinct principals so the diversity cap doesn't bind by default
    return [Candidate(steward_id=f"s{i}", domain_standing_tier=tier, principal_id=f"p{i}") for i in range(n)]


# --------------------------------------------------------------- eligibility (§4, §6)


def test_pool_requires_senior_or_above():
    cands = [
        Candidate("ok", "Senior Steward", "p1"),
        Candidate("council", "Council Steward", "p2"),
        Candidate("too_junior", "Builder Steward", "p3"),
        Candidate("contrib", "Contributor", "p4"),
    ]
    pool = {c.steward_id for c in council.eligible_pool(cands, DOMAIN)}
    assert pool == {"ok", "council"}


def test_pool_excludes_under_review_and_bad_standing():
    cands = [
        Candidate("good", "Senior Steward", "p1"),
        Candidate("reviewed", "Senior Steward", "p2", under_review=True),
        Candidate("bad", "Senior Steward", "p3", good_standing=False),
    ]
    assert {c.steward_id for c in council.eligible_pool(cands, DOMAIN)} == {"good"}


def test_pool_excludes_conflicted_members():
    cands = [
        Candidate("clean", "Senior Steward", "p1"),
        Candidate("conflicted", "Senior Steward", "p2", conflicts={"acme-corp"}),
    ]
    pool = {c.steward_id for c in council.eligible_pool(cands, DOMAIN, matter_parties=["acme-corp"])}
    assert pool == {"clean"}


# --------------------------------------------------------------- verifiable random draw (§4/§5.1)


def test_compose_is_deterministic_and_verifiable():
    cands = _pool(8)
    a = council.compose_panel("rev-1", DOMAIN, 3, cands, anchor_seed="anchor-abc")
    b = council.compose_panel("rev-1", DOMAIN, 3, cands, anchor_seed="anchor-abc")
    assert a.members == b.members
    assert a.composition_hash == b.composition_hash
    assert len(a.members) == 3 and a.complete


def test_different_matter_draws_differently():
    cands = _pool(8)
    a = council.compose_panel("rev-1", DOMAIN, 3, cands, anchor_seed="anchor-abc")
    b = council.compose_panel("rev-2", DOMAIN, 3, cands, anchor_seed="anchor-abc")
    assert a.members != b.members          # different seed -> different draw (anti-fixed-panel)


def test_principal_cap_prevents_packing():
    # five candidates, but four share one principal -> cap 1 keeps at most one of them
    cands = [
        Candidate("a1", "Senior Steward", "shared"),
        Candidate("a2", "Senior Steward", "shared"),
        Candidate("a3", "Senior Steward", "shared"),
        Candidate("a4", "Senior Steward", "shared"),
        Candidate("b1", "Senior Steward", "other"),
    ]
    panel = council.compose_panel("rev-x", DOMAIN, 3, cands, anchor_seed="s", principal_cap=1)
    shared_selected = [m for m in panel.members if m.startswith("a")]
    assert len(shared_selected) <= 1
    assert not panel.complete             # can't fill 3 distinct principals from this pool


def test_principal_cap_can_be_raised():
    cands = [Candidate(f"a{i}", "Senior Steward", "shared") for i in range(4)]
    panel = council.compose_panel("rev-y", DOMAIN, 3, cands, anchor_seed="s", principal_cap=3)
    assert len(panel.members) == 3 and panel.complete


def test_conflicted_member_never_selected():
    cands = _pool(6) + [Candidate("conf", "Senior Steward", "pX", conflicts={"party-1"})]
    for seed in ("a", "b", "c", "d", "e"):
        panel = council.compose_panel("m", DOMAIN, 5, cands, anchor_seed=seed, matter_parties=["party-1"])
        assert "conf" not in panel.members


def test_incomplete_when_pool_too_small():
    panel = council.compose_panel("m", DOMAIN, 5, _pool(2), anchor_seed="s")
    assert len(panel.members) == 2 and not panel.complete


# --------------------------------------------------------------- supermajority + timelock (§5.2.6)


def test_supermajority_two_thirds():
    assert council.is_supermajority(4, seated=6) is True       # 4/6 >= 2/3
    assert council.is_supermajority(3, seated=6) is False      # 3/6 < 2/3
    assert council.is_supermajority(4, seated=6, recused=1) is True   # 4/5 >= 2/3
    assert council.is_supermajority(3, seated=6, recused=1) is False  # 3/5 < 2/3
    assert council.is_supermajority(1, seated=1, recused=1) is False  # no effective members


def test_supermajority_custom_fraction():
    assert council.is_supermajority(3, seated=4, fraction=Fraction(3, 4)) is True
    assert council.is_supermajority(2, seated=4, fraction=Fraction(3, 4)) is False


def test_timelock_window():
    ratified = 1_000_000
    assert council.timelock_satisfied(ratified, ratified + 13 * council.DAY_SECONDS) is False
    assert council.timelock_satisfied(ratified, ratified + 14 * council.DAY_SECONDS) is True
    assert council.takes_effect_at(ratified, 30) == ratified + 30 * council.DAY_SECONDS
