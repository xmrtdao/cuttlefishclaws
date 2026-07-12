"""RRC-001 Reward Router — request/response models."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class WorkUnit(BaseModel):
    quantity: float = 1
    unit: str = "unit"
    quality_score: Optional[float] = None


class RewardEligibility(BaseModel):
    tier_1_usdc: bool = False
    tier_2_cac: bool = False
    tier_3_governance: bool = False
    tier_4_e2r: bool = False


class InboundEvent(BaseModel):
    """The reward_eligible ActivityEvent the Router consumes (AR-001 §7.2)."""
    event_id: str
    activity_type: str
    section_404_category: str = "null"        # i | ii | iii | null
    primary_actor_id: str
    work_unit: WorkUnit = Field(default_factory=WorkUnit)
    reward_eligibility: RewardEligibility = Field(default_factory=RewardEligibility)
    timestamp: Optional[str] = None


class DistributionRecord(BaseModel):
    tier: str                                  # tier_1_usdc | tier_2_cac | tier_3_governance | tier_4_e2r
    kind: str                                  # usdc_activity_reward | cac_topup | governance_upgrade_intent | e2r_contribution_credit_intent
    rail: str                                  # utility | securities | none
    status: str                                # recorded | stubbed
    amount_usdc: Optional[float] = None        # tier 1
    credit_units: Optional[float] = None       # tier 2
    writeback_event_type: Optional[str] = None # PAYMENT_SETTLEMENT | CAC_TOPUP | ...
    ratecard_version: Optional[str] = None


class RouteResponse(BaseModel):
    event_id: str
    status: str                                # routed | duplicate | no_reward
    distributions: List[DistributionRecord]
