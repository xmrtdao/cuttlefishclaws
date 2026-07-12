"""Stewardship Standing engine — CFL-SPEC-SS-001.

The earned-competence axis (sibling of trustgraph.py). A per-(agent, domain)
0-100 score that is a deterministic, recency-weighted quality average of the
agent's Activity Registry (AR-001) work events in that domain.

Design (SS-001 §7):
  * Domain-bounded: N scores per agent, one per validation domain.
  * Cross-domain ISOLATION (SS-001 §3): each domain is computed ONLY from events
    tagged to that domain. There is structurally no code path by which a domain-A
    event changes domain-B Standing.
  * Quality AVERAGE (not a sum): low-quality work drags the mean down; recency
    half-life H weights recent work more. (Contrast TG-001's cumulative sum.)
  * Event-sourced, deterministic, replayable (same guarantee as TG-001 §5.4).
  * Earned competence, NOT capital: the engine never reads balances/reserve.

Domain tagging convention (Phase 1): the domain key is carried in
`work_unit.rubric_id` (the rubric applied == the domain's review rubric).
Review/override events carry the effect in `work_unit.unit`
("standing_cap" | "standing_set" | "standing_restore") with `work_unit.quantity`.
"""

from __future__ import annotations

import calendar
import time
from typing import Optional

from storage import ActivityType, RegistryStore


# --------------------------------------------------------------- constants (SS-001 §7.1)

H_SECONDS = 90 * 24 * 3600       # quality half-life: 90 days
Q_DEFAULT = 1.0                  # clean positive event lacking an explicit quality_score
N_MIN = 3                        # min events for a non-provisional score
DAY_SECONDS = 86400

QUALITY_TYPES = {
    ActivityType.VALIDATION_COMPLETED.value,
    ActivityType.VALIDATION_PEER_REVIEWED.value,
    ActivityType.ATTESTATION_ISSUED.value,
    ActivityType.DISPUTE_RESOLUTION.value,
}
REVIEW_TYPES = {
    ActivityType.STEWARDSHIP_REVIEW_OUTCOME.value,
    ActivityType.STANDING_ADJUSTED.value,
}

# Maturation ladder (SS-001 §5): (name, min_days, min_standing). Both gates required.
_LADDER = [
    ("Contributor", 7, 30.0),
    ("Builder Steward", 30, 60.0),
    ("Senior Steward", 90, 80.0),
]
_LADDER_ORDER = ["Participant", "Contributor", "Builder Steward", "Senior Steward"]

# Council-eligibility (SS-001 §5): >= COUNCIL_STANDING in >= COUNCIL_DOMAINS, >= COUNCIL_DAYS.
COUNCIL_STANDING = 90.0
COUNCIL_DOMAINS = 2
COUNCIL_DAYS = 180


# --------------------------------------------------------------- helpers


def _parse_ts(ts: str) -> int:
    return calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))


def event_domain(event: dict) -> Optional[str]:
    """The domain key for an event (work_unit.rubric_id). None == untagged -> ignored."""
    rid = (event.get("work_unit") or {}).get("rubric_id")
    return rid or None


def _quality(event: dict) -> float:
    q = (event.get("work_unit") or {}).get("quality_score")
    if q is None:
        return Q_DEFAULT
    return max(0.0, min(1.0, float(q)))


def ladder_tier(standing: float, days: float, provisional: bool, has_events: bool) -> str:
    """SS-001 §5 — highest tier whose BOTH (time, standing) gates pass; provisional caps at Contributor."""
    if not has_events:
        return "Participant"
    tier = "Participant"
    for name, min_days, min_standing in _LADDER:
        if days >= min_days and standing >= min_standing:
            tier = name
    if provisional and _LADDER_ORDER.index(tier) > _LADDER_ORDER.index("Contributor"):
        tier = "Contributor"
    return tier


# --------------------------------------------------------------- pure core (SS-001 §7.2)


def compute_standing(domain_events: list[dict], as_of: Optional[int] = None) -> dict:
    """Recency-weighted quality average for ONE domain (events MUST already be that domain's).

    This function never reads a domain tag — the caller guarantees isolation (SS-001 §3).
    """
    if as_of is None:
        as_of = int(time.time())

    quality = [e for e in domain_events if e.get("activity_type") in QUALITY_TYPES]
    reviews = [e for e in domain_events if e.get("activity_type") in REVIEW_TYPES]

    if quality:
        num = den = 0.0
        for e in quality:
            w = 2.0 ** (-(as_of - _parse_ts(e["timestamp"])) / H_SECONDS)
            num += w * _quality(e)
            den += w
        raw = (num / den) if den > 0 else 0.0
        value = 100.0 * raw
        first_t = min(_parse_ts(e["timestamp"]) for e in quality)
        days = (as_of - first_t) / DAY_SECONDS
    else:
        value = 0.0
        days = 0.0

    # §6 caps / sets (apply in timestamp order; only those at or before as_of)
    cap = 100.0
    forced: Optional[float] = None
    for e in sorted(reviews, key=lambda x: x["timestamp"]):
        if _parse_ts(e["timestamp"]) > as_of:
            continue
        wu = e.get("work_unit") or {}
        unit = str(wu.get("unit", "")).lower()
        qty = wu.get("quantity")
        if unit == "standing_cap" and qty is not None:
            cap = float(qty)
        elif unit == "standing_set" and qty is not None:
            forced = float(qty)
        elif unit == "standing_restore":
            cap = 100.0
            forced = None

    if forced is not None:
        value = forced
    value = min(value, cap)
    value = round(max(0.0, min(100.0, value)), 2)

    count = len(quality)
    provisional = 0 < count < N_MIN
    has_events = count > 0
    return {
        "standing": value,
        "provisional": provisional,
        "event_count": count,
        "time_in_domain_days": round(days, 2),
        "active_cap": cap,
        "ladder_tier": ladder_tier(value, days, provisional, has_events),
    }


# --------------------------------------------------------------- engine


class StandingEngine:
    """Reads AR-001 events from the registry store and projects per-domain Standing.

    Consumer + projector only (SS-001 §8): no write path. Cross-domain isolation is
    enforced structurally — each domain is computed from a list containing ONLY that
    domain's events.
    """

    def __init__(self, store: RegistryStore) -> None:
        self._store = store

    def _events_by_domain(self, actor_id: str, scan_limit: int) -> dict[str, list[dict]]:
        buckets: dict[str, list[dict]] = {}
        for e in self._store.list_events(actor_id=actor_id, limit=scan_limit):
            d = event_domain(e)
            if d is None:
                continue
            buckets.setdefault(d, []).append(e)
        return buckets

    def domain(
        self,
        actor_id: str,
        domain: str,
        as_of: Optional[int] = None,
        scan_limit: int = 10000,
    ) -> dict:
        # ISOLATION: filter to this domain's events only; no other domain is read.
        events = [
            e
            for e in self._store.list_events(actor_id=actor_id, limit=scan_limit)
            if event_domain(e) == domain
        ]
        r = compute_standing(events, as_of=as_of)
        r["agent"] = actor_id
        r["domain"] = domain
        r["council_eligible"] = (
            r["standing"] >= COUNCIL_STANDING and r["time_in_domain_days"] >= COUNCIL_DAYS
        )
        return r

    def all_domains(
        self,
        actor_id: str,
        as_of: Optional[int] = None,
        scan_limit: int = 10000,
    ) -> dict:
        buckets = self._events_by_domain(actor_id, scan_limit)
        domains = {}
        council_domains = 0
        for d, events in buckets.items():
            r = compute_standing(events, as_of=as_of)  # each domain isolated
            if r["standing"] >= COUNCIL_STANDING and r["time_in_domain_days"] >= COUNCIL_DAYS:
                council_domains += 1
            domains[d] = r
        return {
            "agent": actor_id,
            "domains": domains,
            "council_eligible": council_domains >= COUNCIL_DOMAINS,
        }

    def history(self, actor_id: str, domain: str, limit: int = 100) -> list[dict]:
        out = []
        for e in self._store.list_events(actor_id=actor_id, limit=limit):
            if event_domain(e) != domain:
                continue
            atype = e.get("activity_type")
            if atype not in QUALITY_TYPES and atype not in REVIEW_TYPES:
                continue
            out.append(
                {
                    "event_id": e.get("event_id"),
                    "activity_type": atype,
                    "quality": _quality(e) if atype in QUALITY_TYPES else None,
                    "at": e.get("timestamp"),
                }
            )
        return out
