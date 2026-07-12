"""Constitutional TrustGraph — the per-agent RUNTIME detection layer.

Implements the archived doctrine `canon/00_CONSTITUTION/TRUSTGRAPH.md` (Constitution v1.2
Article III) and the CFL-NARR-003 §3 bridge rule. This is NOT the TG-001 engine
(`trustgraph.py`) — it is the layer beneath AR-001: an agent's local immune system that
scores the counterparties IT meets, runs the seven adversarial pattern detectors, applies
asymmetric local scoring with decay, and — when a detection is against a *registered*
Cuttlefish agent — emits the corresponding AR-001 event (the bridge rule).

See CFL-NARR-003 for how this layer relates to the TG-001 engine. Both are canonical and
distinct (NARR-003 resolves discrepancy D-1 by layering, not merging).

Detector note: detection here is deterministic and marker/flag-driven (testable skeleton).
TODO(PROGRAMMER): production detectors need real heuristics/NLP over live interactions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

# Constitution v1.2 §3.2 — initial trust assignment (the per-entity floor).
INITIAL_SCORES = {
    "operator": 100,
    "known_community": 60,
    "unknown_agent": 40,
    "system_requester": 20,
    "adversarial": 0,
}

# Constitution v1.2 §3.3 — negative deltas per detected pattern (applied in full; asymmetric).
PATTERN_DELTA = {
    "injection": -50,
    "social_engineering": -20,
    "identity_fishing": -15,
    "skill_injection": -15,
    "coordinated_probing": -10,
    "trust_manipulation": -25,
    "identity_inconsistency": -15,
}

# CFL-NARR-003 §3 bridge mapping — pattern -> (AR-001 activity_type, severity tag | None).
# Only emitted when the counterparty is a REGISTERED agent.
PATTERN_EVENT = {
    "injection": ("SLASH_APPLIED", "injection"),
    "skill_injection": ("SLASH_APPLIED", "violation_major"),
    "social_engineering": ("SOCIAL_ENGINEERING_DETECTED", None),
    "identity_fishing": ("IDENTITY_FISHING_DETECTED", None),
    "coordinated_probing": ("COORDINATED_PROBING_DETECTED", None),
    "trust_manipulation": ("TRUST_MANIPULATION_DETECTED", None),
    "identity_inconsistency": ("IDENTITY_INCONSISTENCY_DETECTED", None),
}

POSITIVE_DAILY_CAP = 15      # §3.3 trust earned slowly (gain cap per day)
DECAY_PER_WEEK = 2           # §3.5 -2 per week of inactivity, floored at the entity floor
WEEK_SECONDS = 7 * 24 * 3600
DAY_SECONDS = 24 * 3600

_INJECTION_MARKERS = (
    "ignore previous instructions", "ignore all previous", "disregard your",
    "you are now", "ignore your constitution", "act as if you were",
)


def band(score: float) -> str:
    """Constitution v1.2 §3.1 bands."""
    if score >= 80:
        return "Trusted"
    if score >= 50:
        return "Neutral"
    if score >= 20:
        return "Cautious"
    return "Adversarial"


def detect_patterns(interaction: dict) -> set[str]:
    """The seven detectors. Flag-driven + a few text markers for injection (deterministic)."""
    text = str(interaction.get("text", "")).lower()
    found: set[str] = set()
    if interaction.get("injection") or any(m in text for m in _INJECTION_MARKERS):
        found.add("injection")
    if interaction.get("skill_injection") or "install this skill" in text:
        found.add("skill_injection")
    if interaction.get("social_engineering"):
        found.add("social_engineering")
    if interaction.get("identity_fishing"):
        found.add("identity_fishing")
    if interaction.get("coordinated_probing"):
        found.add("coordinated_probing")
    if interaction.get("trust_manipulation"):
        found.add("trust_manipulation")
    claims = interaction.get("claims_identity")
    expected = interaction.get("expected_identity")
    if interaction.get("identity_inconsistency") or (claims is not None and expected is not None and claims != expected):
        found.add("identity_inconsistency")
    return found


@dataclass
class EntityRecord:
    entity_id: str
    entity_type: str
    is_registered: bool = False
    kya_id: Optional[str] = None
    score: float = 40.0
    floor: float = 40.0
    last_seen: int = 0
    positive_day: int = -1          # UTC day index of the current positive-accrual window
    positive_today: float = 0.0
    flags: set = field(default_factory=set)


class ConstitutionalTrustGraph:
    """A single agent's runtime immune system over the counterparties it meets."""

    def __init__(self, emit_hook: Optional[Callable[[dict], dict]] = None) -> None:
        self._entities: dict[str, EntityRecord] = {}
        # bridge emission to AR-001; default records locally (mockable / no-op HTTP)
        self._emitted: list[dict] = []
        self._emit = emit_hook or (lambda payload: self._emitted.append(payload))

    # ----------- registry

    def register_entity(self, entity_id: str, entity_type: str = "unknown_agent",
                        is_registered: bool = False, kya_id: Optional[str] = None) -> EntityRecord:
        seed = float(INITIAL_SCORES.get(entity_type, INITIAL_SCORES["unknown_agent"]))
        rec = EntityRecord(entity_id=entity_id, entity_type=entity_type, is_registered=is_registered,
                           kya_id=kya_id, score=seed, floor=seed)
        self._entities[entity_id] = rec
        return rec

    def get(self, entity_id: str) -> Optional[EntityRecord]:
        return self._entities.get(entity_id)

    def _ensure(self, entity_id: str) -> EntityRecord:
        rec = self._entities.get(entity_id)
        return rec if rec is not None else self.register_entity(entity_id, "unknown_agent")

    def band_of(self, entity_id: str) -> Optional[str]:
        rec = self._entities.get(entity_id)
        return band(rec.score) if rec else None

    # ----------- scoring

    def apply_positive(self, entity_id: str, points: float, as_of: int = 0) -> float:
        """§3.3 — trust earned slowly: positive accrual capped at POSITIVE_DAILY_CAP per day."""
        rec = self._ensure(entity_id)
        day = as_of // DAY_SECONDS
        if rec.positive_day != day:
            rec.positive_day = day
            rec.positive_today = 0.0
        allowed = max(0.0, min(points, POSITIVE_DAILY_CAP - rec.positive_today))
        rec.positive_today += allowed
        rec.score = min(100.0, rec.score + allowed)
        rec.last_seen = as_of
        return rec.score

    def decay(self, entity_id: str, as_of: int) -> float:
        """§3.5 — -2 per week of inactivity, floored at the entity's initial assignment."""
        rec = self._ensure(entity_id)
        if as_of > rec.last_seen and rec.score > rec.floor:
            weeks = (as_of - rec.last_seen) / WEEK_SECONDS
            rec.score = max(rec.floor, rec.score - DECAY_PER_WEEK * weeks)
        return rec.score

    def observe(self, entity_id: str, interaction: dict, as_of: int = 0) -> dict:
        """Run detectors on an interaction; apply negative deltas in full (asymmetric);
        emit AR-001 events for detections against REGISTERED agents (CFL-NARR-003 §3)."""
        rec = self._ensure(entity_id)
        patterns = detect_patterns(interaction)
        emitted: list[dict] = []
        for pattern in sorted(patterns):
            rec.score = max(0.0, rec.score + PATTERN_DELTA.get(pattern, 0))
            rec.flags.add(pattern)
            if rec.is_registered:   # bridge rule: only registered agents cross into AR-001
                activity_type, severity = PATTERN_EVENT[pattern]
                payload = {
                    "activity_type": activity_type,
                    "primary_actor_id": rec.kya_id or entity_id,
                    "activity_subject": {"type": "agent", "id": entity_id},
                    "work_unit": {"quantity": 1, "unit": severity or "detection"},
                    "evidence_payload": {"pattern": pattern, "detected_by": "constitutional_trustgraph"},
                    "reward_eligibility": {},
                }
                self._emit(payload)
                emitted.append(payload)
        rec.last_seen = as_of
        return {
            "entity_id": entity_id,
            "patterns": sorted(patterns),
            "score": round(rec.score, 2),
            "band": band(rec.score),
            "emitted_events": [p["activity_type"] for p in emitted],
        }

    @property
    def emitted(self) -> list[dict]:
        return self._emitted
