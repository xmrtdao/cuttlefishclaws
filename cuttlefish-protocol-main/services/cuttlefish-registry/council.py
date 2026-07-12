"""CC-001 — Council governance: anti-faction panel composition + supermajority/timelock.

Implements the load-bearing anti-faction mechanics of `canon/CC-001_COUNCIL_CHARTER.md`:
  * §4 eligibility pool: Senior+ Standing in the domain, good standing, no active review.
  * §4/§5.1 selection = VERIFIABLE RANDOM DRAW (seeded by an AR-001 §5.3 anchor hash),
    uniform among the qualified pool — not election. No member chooses their panel.
  * §6 conflict/recusal exclusion; principal-diversity cap (no packing).
  * §5.2.6 supermajority (default ≥ 2/3 of seated, non-recused) + timelock window.

Determinism: same (candidates, anchor_seed, matter_id) -> same panel + composition_hash,
so a third party can re-run the draw and verify it (CC-001 §7 transparency, anti-seed-manipulation).
Standing is taken as input here; TODO(PROGRAMMER): read it live from the SS-001 standing engine.
"""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Iterable, Optional

# CC-001 §4 — eligible ladder tiers for the draw (Senior Steward and above).
ELIGIBLE_TIERS = {"Senior Steward", "Council Steward", "Council-eligible"}


@dataclass
class Candidate:
    steward_id: str
    domain_standing_tier: str            # SS-001 ladder tier IN the matter's domain
    principal_id: str = ""               # for principal-diversity caps (§6 / anti-packing)
    good_standing: bool = True
    under_review: bool = False           # active Stewardship Review -> excluded (§4)
    conflicts: set = field(default_factory=set)   # parties this steward must recuse from (§6)


@dataclass
class PanelResult:
    matter_id: str
    domain: str
    members: list[str]
    anchor_seed: str
    composition_hash: str
    requested_size: int
    complete: bool                       # True if the pool filled the requested size


def eligible_pool(candidates: Iterable[Candidate], domain: str, matter_parties: Iterable[str] = ()) -> list[Candidate]:
    """CC-001 §4 + §6 — the qualified, conflict-free pool for this matter."""
    parties = set(matter_parties)
    pool: list[Candidate] = []
    for c in candidates:
        if c.domain_standing_tier not in ELIGIBLE_TIERS:
            continue
        if not c.good_standing or c.under_review:
            continue
        if c.conflicts & parties:          # mandatory recusal
            continue
        pool.append(c)
    return pool


def _verifiable_rng(anchor_seed: str, matter_id: str) -> random.Random:
    digest = hashlib.sha256(f"{anchor_seed}:{matter_id}".encode("utf-8")).hexdigest()
    return random.Random(int(digest, 16))


def compose_panel(
    matter_id: str,
    domain: str,
    size: int,
    candidates: Iterable[Candidate],
    anchor_seed: str,
    matter_parties: Iterable[str] = (),
    principal_cap: int = 1,
) -> PanelResult:
    """CC-001 §4/§5.1 — verifiable random draw from the eligible pool, conflict-excluded,
    principal-diversity-capped. Deterministic from (candidates, anchor_seed, matter_id)."""
    pool = eligible_pool(candidates, domain, matter_parties)
    rng = _verifiable_rng(anchor_seed, matter_id)
    order = pool[:]
    rng.shuffle(order)                     # uniform among the qualified pool (§5 Q2)

    selected: list[Candidate] = []
    per_principal: dict[str, int] = {}
    for c in order:
        if len(selected) >= size:
            break
        if principal_cap and per_principal.get(c.principal_id, 0) >= principal_cap:
            continue                       # diversity cap: no principal packs the panel
        selected.append(c)
        per_principal[c.principal_id] = per_principal.get(c.principal_id, 0) + 1

    members = [c.steward_id for c in selected]
    composition_hash = hashlib.sha256(
        ("|".join([anchor_seed, matter_id, domain, *sorted(members)])).encode("utf-8")
    ).hexdigest()
    return PanelResult(
        matter_id=matter_id, domain=domain, members=members, anchor_seed=anchor_seed,
        composition_hash=composition_hash, requested_size=size, complete=len(members) == size,
    )


# --------------------------------------------------------------- supermajority + timelock (§5.2.6)

def is_supermajority(yes_votes: int, seated: int, recused: int = 0, fraction: Fraction = Fraction(2, 3)) -> bool:
    """yes / (seated - recused) >= fraction (default 2/3 of non-recused seated members)."""
    effective = seated - recused
    if effective <= 0:
        return False
    return yes_votes * fraction.denominator >= effective * fraction.numerator


DAY_SECONDS = 24 * 3600


def timelock_satisfied(ratified_at: int, now: int, timelock_days: int = 14) -> bool:
    """CC-001 §5.2.6 — a sensitive action takes effect only after the timelock window
    (recommend 14-30 days), during which the Navigator veto window is open."""
    return now - ratified_at >= timelock_days * DAY_SECONDS


def takes_effect_at(ratified_at: int, timelock_days: int = 14) -> int:
    return ratified_at + timelock_days * DAY_SECONDS
