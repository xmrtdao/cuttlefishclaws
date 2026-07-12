"""TrustGraph scoring engine — CFL-SPEC-TG-001.

The behavioral trust layer. A per-agent 0-100 score that is a deterministic,
replayable projection of the agent's Activity Registry (AR-001) event history
under the TG-001 §4 locked rubric.

Design (TG-001 §5):
  * Event-sourced: the score stores no independent truth; it folds AR-001 events.
  * Deterministic / replayable: same events + same `as_of` -> same score.
  * Asymmetric: positives attenuate near the ceiling; negatives apply in full.
  * Decaying: -2/week of inactivity, eroding only the above-tier-floor surplus.
  * Behavioral, NOT financial (TG-001 §8): pays no reward, never "staked".

Phase 1 (PILOT-001): single-node, reads events from the registry `RegistryStore`.
The pure core (`compute_score`) takes a plain list of event dicts so it is
testable without a database and identical across implementations.
"""

from __future__ import annotations

import calendar
import math
import time
from typing import Optional

from storage import ActivityType, RegistryStore


# --------------------------------------------------------------- constants

# CAC-005 §4 per-tier TrustGraph floors. New verified agents seed here (TG-001 §2).
TIER_FLOORS: dict[str, int] = {
    "explorer": 20,
    "developer": 30,
    "studio": 40,
    "enterprise": 55,
    "anchor": 70,
}
DEFAULT_TIER = "developer"

DECAY_PER_WEEK = 2.0          # TG-001 §2
WEEK_SECONDS = 7 * 24 * 3600
ASYMMETRY_CEIL = 90.0         # above this, positive deltas attenuate (TG-001 §2/§5)
ASYMMETRY_FACTOR = 0.5        # positive deltas are halved above the ceiling
MICRO_DAILY_CAP = 10.0        # cap on micro-positive accrual per UTC day (TG-001 §4)

# TG-001 §4 LOCKED rubric — base deltas keyed to AR-001 ActivityType.
_RUBRIC: dict[str, float] = {
    ActivityType.VALIDATION_COMPLETED.value: 3.0,
    ActivityType.VALIDATION_PEER_REVIEWED.value: 2.0,
    ActivityType.ATTESTATION_ISSUED.value: 2.0,        # +1..+3 by attestor standing; mid in Phase 1
    ActivityType.GOVERNANCE_VOTE.value: 1.0,
    ActivityType.GOVERNANCE_PROPOSAL_AUTHORED.value: 5.0,
    ActivityType.INFERENCE_CONSUMPTION.value: 0.05,
    ActivityType.KYA_RENEWAL.value: 2.0,
}

# Micro-positive signals subject to the daily cap (TG-001 §4 anti-farming).
_MICRO_POSITIVE = {
    ActivityType.GOVERNANCE_VOTE.value,
    ActivityType.INFERENCE_CONSUMPTION.value,
}

# Negative signals arrive as SLASH_APPLIED (and a few explicit types). The
# severity tag is carried in work_unit.unit for Phase 1 (no dedicated field yet).
_SLASH_SEVERITY: dict[str, float] = {
    "injection": -50.0,            # prompt-injection attempt (largest penalty)
    "fabrication": -25.0,          # ceph-v3 fabrication detector (BSR-001)
    "violation_major": -30.0,
    "violation_minor": -15.0,
    "abuse_pattern": -15.0,        # e.g. >20 transfers/hr
    "suspended_counterparty": -10.0,
}
_DEFAULT_SLASH = -15.0            # unspecified violation == minor


# ------------------------------------------------------------- time helpers


def _parse_ts(ts: str) -> int:
    """Parse the registry ISO-UTC timestamp ('%Y-%m-%dT%H:%M:%SZ') to epoch secs."""
    return calendar.timegm(time.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))


def _utc_day(ts: str) -> str:
    return ts[:10]  # YYYY-MM-DD


# --------------------------------------------------------------- rubric


def delta_for(event: dict) -> float:
    """Return the TG-001 §4 delta for a single AR-001 event (before caps/asymmetry)."""
    atype = event.get("activity_type")
    if atype == ActivityType.SLASH_APPLIED.value:
        tag = str((event.get("work_unit") or {}).get("unit", "")).lower()
        return _SLASH_SEVERITY.get(tag, _DEFAULT_SLASH)
    return _RUBRIC.get(atype, 0.0)


def is_positive_signal(event: dict) -> bool:
    return delta_for(event) > 0.0


# --------------------------------------------------------------- bands


def band_and_status(score: float) -> tuple[str, str]:
    """TG-001 §3 bands and the lifecycle status they drive."""
    if score >= 90:
        return "Trusted", "ACTIVE"
    if score >= 70:
        return "Standard", "ACTIVE"
    if score >= 50:
        return "Monitored", "ACTIVE"
    if score >= 20:
        return "Cautious", "ACTIVE"
    if score >= 10:
        return "Suspended", "SUSPENDED"
    return "Revoked", "REVOKED"


# --------------------------------------------------------------- pure core


def compute_score(
    events: list[dict],
    tier: str = DEFAULT_TIER,
    as_of: Optional[int] = None,
) -> dict:
    """Deterministic TG-001 §5 projection.

    `events`   : AR-001 event dicts (any order); each needs activity_type, timestamp,
                 and optionally work_unit.
    `tier`     : CAC tier -> seed/floor (TIER_FLOORS).
    `as_of`    : epoch seconds for decay evaluation (defaults to now). Pass an
                 explicit value for deterministic replay/tests.

    Returns: { score, band, status, tier, tier_floor, below_floor, last_positive_at }.
    """
    tier = tier.lower()
    floor = float(TIER_FLOORS.get(tier, TIER_FLOORS[DEFAULT_TIER]))
    if as_of is None:
        as_of = int(time.time())

    ordered = sorted(events, key=lambda e: e["timestamp"])

    score = floor
    last_positive_ts: Optional[int] = None
    micro_by_day: dict[str, float] = {}

    for e in ordered:
        d = delta_for(e)
        if d == 0.0:
            continue
        if d > 0:
            # daily cap on micro-positives (anti-farming)
            if e.get("activity_type") in _MICRO_POSITIVE:
                day = _utc_day(e["timestamp"])
                used = micro_by_day.get(day, 0.0)
                allowed = max(0.0, MICRO_DAILY_CAP - used)
                d = min(d, allowed)
                micro_by_day[day] = used + d
                if d == 0.0:
                    continue
            # asymmetry: positives attenuate near the ceiling (slow up)
            if score >= ASYMMETRY_CEIL:
                d *= ASYMMETRY_FACTOR
            score = min(100.0, score + d)
            last_positive_ts = _parse_ts(e["timestamp"])
        else:
            # negatives apply in full at any level (fast down)
            score = max(0.0, score + d)

    # inactivity decay erodes only the above-floor surplus (TG-001 §2)
    if last_positive_ts is not None and score > floor:
        weeks = max(0.0, (as_of - last_positive_ts) / WEEK_SECONDS)
        decay = DECAY_PER_WEEK * weeks
        score = max(floor, score - decay)
    elif last_positive_ts is None and score > floor:
        # never had a positive signal but somehow above floor: no decay reference
        pass

    score = round(max(0.0, min(100.0, score)), 2)
    band, status = band_and_status(score)
    return {
        "score": score,
        "band": band,
        "status": status,
        "tier": tier,
        "tier_floor": floor,
        "below_floor": score < floor,
        "last_positive_at": (
            time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(last_positive_ts))
            if last_positive_ts is not None
            else None
        ),
    }


# --------------------------------------------------------------- engine


class TrustGraphEngine:
    """Reads AR-001 events from the registry store and projects the TG-001 score.

    The engine is a *consumer + projector* (TG-001 §7): there is no write path.
    Scores change only because AR-001 events exist. `recompute` is a full replay.
    """

    def __init__(self, store: RegistryStore) -> None:
        self._store = store

    def score(
        self,
        actor_id: str,
        tier: str = DEFAULT_TIER,
        as_of: Optional[int] = None,
        scan_limit: int = 10000,
    ) -> dict:
        events = self._store.list_events(actor_id=actor_id, limit=scan_limit)
        result = compute_score(events, tier=tier, as_of=as_of)
        result["agent"] = actor_id
        result["event_count"] = len(events)
        return result

    def history(self, actor_id: str, limit: int = 100) -> list[dict]:
        """Score-affecting events, newest first, with the delta each contributed."""
        events = self._store.list_events(actor_id=actor_id, limit=limit)
        out = []
        for e in events:
            d = delta_for(e)
            if d == 0.0:
                continue
            out.append(
                {
                    "event_id": e.get("event_id"),
                    "activity_type": e.get("activity_type"),
                    "delta": d,
                    "at": e.get("timestamp"),
                }
            )
        return out
