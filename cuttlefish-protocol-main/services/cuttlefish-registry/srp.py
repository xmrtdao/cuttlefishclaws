"""SRP-001 — Stewardship Review Procedure: the review-proceeding state machine.

Implements the operational lifecycle of `CAC_Frameworks/STEWARDSHIP_REVIEW_PROCEDURE.md`
(fills AIL-001 §7), emitting the AR-001 `STEWARDSHIP_REVIEW_*` / `STANDING_ADJUSTED` events:

    filed → (intake check §3) → initiated → panel_formed (CC-001 random draw) →
    deliberation_open → deliberation_closed → concluded (finding + standing adjustment)
                      └→ dismissed_at_intake (frivolous/incomplete filing)

Posture (AIL-001 §1): professional peer review, NOT slashing or litigation. Vocabulary:
"Finding" not "verdict"; "Proceeding" not "case"; standard of proof = preponderance (default),
heightened for alleged fraud. Standing adjustments take effect on issuance (SRP-001 §10.2).

Panel composition reuses CC-001 `council.compose_panel` (verifiable random draw, conflict-excluded).
Emission of registry events is via a mockable hook. TODO(PROGRAMMER): wire to the signed AR-001 write path.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Optional

import council


class SRPError(Exception):
    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


@dataclass
class Proceeding:
    proceeding_id: str
    respondent_id: str
    domain: str
    filing: dict
    status: str = "filed"
    panel: list[str] = field(default_factory=list)
    finding: Optional[dict] = None
    history: list[str] = field(default_factory=list)


# SRP-001 §3 — a valid filing must identify these. Missing any -> intake dismissal.
_REQUIRED_FILING = {
    "attestation_event_ids": "no_attestation_events_named",
    "alleged_defect": "no_alleged_defect",
    "evidence": "no_evidence",
    "harm": "no_identified_harm",
}


class StewardshipReview:
    def __init__(self, emit_hook: Optional[Callable[[dict], dict]] = None) -> None:
        self._proceedings: dict[str, Proceeding] = {}
        self._emitted: list[dict] = []
        self._emit = emit_hook or (lambda payload: self._emitted.append(payload))

    # ----------- helpers

    def _event(self, activity_type: str, p: Proceeding, detail: Optional[dict] = None) -> dict:
        payload = {
            "activity_type": activity_type,
            "primary_actor_id": p.respondent_id,
            "activity_subject": {"type": "stewardship_review", "id": p.proceeding_id},
            "work_unit": {"quantity": 1, "unit": "review"},
            "evidence_payload": detail or {},
            "reward_eligibility": {},
        }
        self._emit(payload)
        p.history.append(activity_type)
        return payload

    def _require(self, proceeding_id: str, expected_status: str) -> Proceeding:
        p = self._proceedings.get(proceeding_id)
        if p is None:
            raise SRPError("unknown_proceeding")
        if p.status != expected_status:
            raise SRPError(f"invalid_transition:{p.status}->needs:{expected_status}")
        return p

    @staticmethod
    def _intake_check(filing: dict) -> tuple[bool, str]:
        for field_name, reason in _REQUIRED_FILING.items():
            if not filing.get(field_name):
                return False, reason
        return True, "ok"

    # ----------- lifecycle

    def initiate(self, proceeding_id: str, respondent_id: str, domain: str, filing: dict) -> Proceeding:
        """SRP-001 §3 — file + intake check. Frivolous/incomplete -> intake dismissal."""
        p = Proceeding(proceeding_id, respondent_id, domain, filing)
        self._proceedings[proceeding_id] = p
        valid, reason = self._intake_check(filing)
        self._event("STEWARDSHIP_REVIEW_INITIATED", p, {"intake_valid": valid})
        if not valid:
            p.status = "dismissed_at_intake"
            p.finding = {"outcome": "intake_dismissal", "reason": reason}
            self._event("STEWARDSHIP_REVIEW_OUTCOME", p, p.finding)
        else:
            p.status = "initiated"
        return p

    def form_panel(self, proceeding_id: str, candidates, anchor_seed: str, size: int = 3) -> council.PanelResult:
        """SRP-001 §5 / AIL-001 §7.2 — staff the panel by CC-001 verifiable random draw.
        The respondent is a matter party, so any candidate conflicted with them recuses."""
        p = self._require(proceeding_id, "initiated")
        result = council.compose_panel(
            proceeding_id, p.domain, size, candidates, anchor_seed, matter_parties=[p.respondent_id]
        )
        if not result.complete:
            raise SRPError("insufficient_panel_pool")
        p.panel = result.members
        p.status = "panel_formed"
        self._event("STEWARDSHIP_REVIEW_PANEL_FORMED", p,
                    {"members": result.members, "composition_hash": result.composition_hash})
        return result

    def open_deliberation(self, proceeding_id: str) -> None:
        p = self._require(proceeding_id, "panel_formed")
        p.status = "deliberation_open"
        self._event("STEWARDSHIP_REVIEW_DELIBERATION_OPENED", p)

    def close_with_finding(
        self,
        proceeding_id: str,
        yes_votes: int,
        voting_members: int,
        standard: str = "preponderance",
        standing_action: Optional[str] = None,
    ) -> dict:
        """SRP-001 §9-§10 — deliberation closes, the panel issues a Finding, and (if defect is
        found) a standing adjustment takes effect on issuance (AIL-001 §6 cascade)."""
        p = self._require(proceeding_id, "deliberation_open")
        self._event("STEWARDSHIP_REVIEW_DELIBERATION_CLOSED", p)

        if standard == "heightened":
            # clear-and-convincing: each voting member affirms (skeleton: unanimous)
            defect = voting_members > 0 and yes_votes == voting_members
        else:
            defect = yes_votes * 2 > voting_members        # simple majority

        p.finding = {
            "outcome": "finding_of_defect" if defect else "no_defect",
            "standard": standard, "yes_votes": yes_votes, "voting_members": voting_members,
        }
        p.status = "concluded"
        self._event("STEWARDSHIP_REVIEW_OUTCOME", p, p.finding)
        if defect and standing_action:
            self._event("STANDING_ADJUSTED", p, {"standing_action": standing_action})
        return p.finding

    def get(self, proceeding_id: str) -> Optional[Proceeding]:
        return self._proceedings.get(proceeding_id)

    @property
    def emitted(self) -> list[dict]:
        return self._emitted
