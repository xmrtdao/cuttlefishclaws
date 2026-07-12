"""RATECARD-001 — the governed, versioned rate card RRC-001 reads (and never invents).

Structure is LOCKED (RATECARD-001 §2). The VALUES below are PLACEHOLDER — Appendix A of
the spec is entirely `TBD`. Real Phase-1 values are ratified by Council under CC-001 §3-§4.
TODO(NAVIGATOR/COUNCIL): replace the placeholder card with ratified values + decision_ref.

Pinning (RATECARD-001 §2 / RRC-001 §8): an event is priced against the card version live at
the event's `timestamp`, never at processing time. There are deliberately NO balance or time
fields in this schema — nothing can accrue on a held amount (§404(a)).
"""

from __future__ import annotations

import calendar
import time
from dataclasses import asdict, dataclass, field
from typing import Optional


@dataclass(frozen=True)
class Tier1Rate:
    base: float
    unit: str
    min: float = 0.0
    per_event_cap: float = 0.0


@dataclass
class RateCard:
    version: str
    effective_from: str                 # ISO-8601 UTC
    ratified_by: dict                   # {body: navigator|council|dao, decision_ref}
    currency: str
    tier_1_usdc: dict                   # {rates: {ActivityType: Tier1Rate}, quality_multiplier, default}
    tier_2_cac: dict                    # {credits: {ActivityType: {credit_units, per_event_cap}}, default_credit_units}
    tier_3_governance: dict             # {thresholds: {target_tier: {qualifying_events, min_standing}}}
    tier_4_e2r: dict                    # {accrual: {ActivityType: {credit_points}}}
    anti_evasion: dict

    def epoch(self) -> int:
        return calendar.timegm(time.strptime(self.effective_from, "%Y-%m-%dT%H:%M:%SZ"))

    def tier1_rate(self, activity_type: str) -> Tier1Rate:
        return self.tier_1_usdc["rates"].get(activity_type, self.tier_1_usdc["default"])

    def tier2_credit_units(self, activity_type: str) -> float:
        entry = self.tier_2_cac["credits"].get(activity_type)
        return float(entry["credit_units"]) if entry else float(self.tier_2_cac["default_credit_units"])

    def quality_multiplier(self, quality_score: Optional[float]) -> float:
        qm = self.tier_1_usdc["quality_multiplier"]
        if quality_score is None:
            return 1.0
        lo = qm["params"].get("min", 0.5)
        hi = qm["params"].get("max", 1.5)
        return max(lo, min(hi, float(quality_score)))

    def as_dict(self) -> dict:
        d = asdict(self)
        # Tier1Rate dataclasses are flattened by asdict already
        return d


# --- PLACEHOLDER Phase-1 pilot card. NOT canonical values (RATECARD-001 Appendix A = TBD). ---
_PILOT_PLACEHOLDER = RateCard(
    version="ratecard-001-pilot-PLACEHOLDER-v0",
    effective_from="2026-01-01T00:00:00Z",
    ratified_by={"body": "navigator", "decision_ref": "PLACEHOLDER-not-ratified"},
    currency="USDC",
    tier_1_usdc={
        "rates": {
            "VALIDATION_COMPLETED": Tier1Rate(5.0, "per review", 0.0, 100.0),
            "VALIDATION_PEER_REVIEWED": Tier1Rate(2.0, "per review", 0.0, 50.0),
            "ATTESTATION_ISSUED": Tier1Rate(2.0, "per attestation", 0.0, 50.0),
            "DISPUTE_RESOLUTION": Tier1Rate(8.0, "per case", 0.0, 100.0),
            "GOVERNANCE_VOTE": Tier1Rate(0.5, "per vote", 0.0, 5.0),
        },
        "quality_multiplier": {"type": "linear", "params": {"min": 0.5, "max": 1.5}},
        "default": Tier1Rate(1.0, "per event", 0.0, 100.0),
    },
    tier_2_cac={
        "credits": {
            "VALIDATION_COMPLETED": {"credit_units": 1000, "per_event_cap": 1000},
            "INFERENCE_CONSUMPTION": {"credit_units": 0, "per_event_cap": 0},
        },
        "default_credit_units": 100,
    },
    tier_3_governance={"thresholds": {}},   # see CAC-005 §4 / SGQ-001 /thresholds — TODO(NAVIGATOR)
    tier_4_e2r={"accrual": {}},             # contribution-credit accrual only (Rail B)
    anti_evasion={"split_work_window_seconds": 3600, "dedup_key": "activity_subject+actor"},
)


class RateCardRegistry:
    """Holds rate-card versions; resolves the one live at an event timestamp (pinning)."""

    def __init__(self, cards: Optional[list[RateCard]] = None) -> None:
        self._cards = sorted(cards or [_PILOT_PLACEHOLDER], key=lambda c: c.epoch())

    def for_timestamp(self, timestamp_iso: Optional[str]) -> RateCard:
        if not timestamp_iso:
            return self._cards[-1]
        try:
            t = calendar.timegm(time.strptime(timestamp_iso, "%Y-%m-%dT%H:%M:%SZ"))
        except (ValueError, TypeError):
            return self._cards[-1]
        live = [c for c in self._cards if c.epoch() <= t]
        return live[-1] if live else self._cards[0]

    def active(self) -> RateCard:
        return self._cards[-1]


DEFAULT_REGISTRY = RateCardRegistry()
