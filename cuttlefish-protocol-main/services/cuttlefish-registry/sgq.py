"""Standing Gate — CFL-SPEC-SGQ-001.

The single service that answers "may this actor be rewarded for this activity, now?"
by composing the two governance axes and ANDing them:

  * TrustGraph (TG-001)  — behavioral: may the agent act AT ALL?
                           (SUSPENDED/REVOKED or below-tier-floor blocks)
  * Stewardship Standing (SS-001) — competence: is the agent entitled IN THIS DOMAIN
                           at the required ladder tier?

plus CAC-tier and IAL checks. The gate computes no trust/standing of its own — it reads
the two deterministic projections (trustgraph.py, standing.py) and decides. Read-only.

"fail on either axis": a failure on ANY axis sets allowed=false; `reasons` lists EVERY
failing condition (no silent denial — SGQ-001 §2).
"""

from __future__ import annotations

import time
from typing import Optional

from trustgraph import TIER_FLOORS, TrustGraphEngine
from standing import StandingEngine


# --------------------------------------------------------------- orderings

TIER_ORDER = ["explorer", "developer", "studio", "enterprise", "anchor"]
LADDER_ORDER = ["Participant", "Contributor", "Builder Steward", "Senior Steward"]
IAL_ORDER = ["IAL1", "IAL2", "IAL3"]


def _ge(order: list[str], a: str, b: str) -> bool:
    """a >= b in the given ordering (unknowns sort lowest -> fail-closed)."""
    ia = order.index(a) if a in order else -1
    ib = order.index(b) if b in order else len(order)
    return ia >= ib


def _gt(order: list[str], a: str, b: str) -> bool:
    ia = order.index(a) if a in order else -1
    ib = order.index(b) if b in order else len(order)
    return ia > ib


# --------------------------------------------------------------- thresholds (config — SGQ-001 §3.3)
#
# Phase-1 defaults; governed config (Council/CC-001) in Phase 2. Per-activity overrides
# raise the bar for higher-impact work (weighted attestation, arbitration).

_DEFAULT_REQ = {"min_standing": 30.0, "min_ladder_tier": "Contributor", "min_cac_tier": "developer"}
_ACTIVITY_REQ: dict[str, dict] = {
    "ATTESTATION_ISSUED": {"min_standing": 60.0, "min_ladder_tier": "Builder Steward"},
    "GOVERNANCE_PROPOSAL_AUTHORED": {"min_standing": 60.0, "min_ladder_tier": "Builder Steward"},
    "DISPUTE_RESOLUTION": {"min_standing": 80.0, "min_ladder_tier": "Senior Steward"},
    # VALIDATION_COMPLETED / VALIDATION_PEER_REVIEWED / GOVERNANCE_VOTE -> defaults
}


def required_for(activity_type: str, domain: str, tier: str) -> dict:
    """Resolve the required.* thresholds for an (activity_type, domain, tier)."""
    tier = tier.lower()
    req = {**_DEFAULT_REQ, **_ACTIVITY_REQ.get(activity_type, {})}
    req["min_cac_tier"] = req.get("min_cac_tier", "developer")
    req["min_ial"] = "IAL3" if tier in ("enterprise", "anchor") else "IAL2"
    req["min_trust_status"] = "ACTIVE"               # not SUSPENDED/REVOKED
    req["min_trust_score"] = float(TIER_FLOORS.get(tier, 30))  # below_floor fails
    return req


# --------------------------------------------------------------- the gate


class StandingGate:
    def __init__(self, trustgraph: TrustGraphEngine, standing: StandingEngine) -> None:
        self._tg = trustgraph
        self._ss = standing

    def evaluate(
        self,
        actor_kya_id: str,
        activity_type: str,
        domain: str,
        cac_tier: str = "developer",
        ial: str = "IAL2",
        as_of: Optional[int] = None,
        purpose: str = "reward",
    ) -> dict:
        tier = cac_tier.lower()
        tg = self._tg.score(actor_kya_id, tier=tier, as_of=as_of)
        ss = self._ss.domain(actor_kya_id, domain, as_of=as_of)
        req = required_for(activity_type, domain, tier)

        reasons: list[str] = []

        # 1. TrustGraph axis (behavioral)
        if tg["status"] != req["min_trust_status"]:
            reasons.append(f"trustgraph_status:{tg['status']}")
        if tg["below_floor"]:
            reasons.append(f"trustgraph_below_tier_floor:{tg['score']}<{tg['tier_floor']}")

        # 2. Standing axis (competence, domain-bounded)
        if ss["standing"] < req["min_standing"]:
            reasons.append(f"standing_below_min:{ss['standing']}<{req['min_standing']}")
        if not _ge(LADDER_ORDER, ss["ladder_tier"], req["min_ladder_tier"]):
            reasons.append(f"ladder_below_min:{ss['ladder_tier']}<{req['min_ladder_tier']}")
        if ss["provisional"] and _gt(LADDER_ORDER, req["min_ladder_tier"], "Contributor"):
            reasons.append("standing_provisional")

        # 3. CAC tier
        if not _ge(TIER_ORDER, tier, req["min_cac_tier"]):
            reasons.append(f"cac_tier_below_min:{tier}<{req['min_cac_tier']}")

        # 4. Identity assurance
        if not _ge(IAL_ORDER, ial, req["min_ial"]):
            reasons.append(f"ial_below_min:{ial}<{req['min_ial']}")

        return {
            "allowed": len(reasons) == 0,
            "trustgraph": {
                "score": tg["score"], "band": tg["band"],
                "status": tg["status"], "below_floor": tg["below_floor"],
            },
            "standing": {
                "domain": domain, "value": ss["standing"],
                "ladder_tier": ss["ladder_tier"], "provisional": ss["provisional"],
            },
            "cac_tier": tier,
            "ial": ial,
            "required": req,
            "reasons": reasons,
            "purpose": purpose,
            "as_of": as_of,
            "evaluated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
