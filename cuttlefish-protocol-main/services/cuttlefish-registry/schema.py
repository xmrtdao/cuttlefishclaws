"""Pydantic request/response models for the Activity Registry HTTP API.

These map directly to AR-001 §3.1 ActivityEvent and supporting types. Phase 0
omits signature fields, witness lists, and contributor weighting (single-actor
events only for the pilot).
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ------------------------------------------------------------- core types


class SubjectRef(BaseModel):
    type: str
    id: str
    parent_id: Optional[str] = None


class WorkUnit(BaseModel):
    quantity: float
    unit: str
    quality_score: Optional[float] = None
    rubric_id: Optional[str] = None


class RewardEligibility(BaseModel):
    tier_1_usdc: bool = False
    tier_2_cac: bool = False
    tier_3_governance: bool = False
    tier_4_e2r: bool = False
    constraints: list[str] = Field(default_factory=list)


# ---------------------------------------------------------- write request


class EventWriteRequest(BaseModel):
    activity_type: str
    primary_actor_id: str
    activity_subject: SubjectRef
    work_unit: WorkUnit
    reward_eligibility: RewardEligibility = Field(default_factory=RewardEligibility)
    evidence_hash: Optional[str] = None
    evidence_payload: Optional[dict] = None
    evidence_uri: Optional[str] = None
    evidence_storage: str = "external"
    registry_scope: str = "cfl-main"

    # KYA-001 §4.2 — write-path actor signature (Sprint 3). Optional at the schema
    # layer so the handler can return precise 400/401/404 codes rather than a 422.
    actor_kya_id: Optional[str] = None
    actor_signature: Optional[str] = None   # hex-encoded signature
    key_id: Optional[str] = None
    signed_at: Optional[int] = None          # epoch seconds


class EventWriteResponse(BaseModel):
    event_id: str
    self_hash: str
    written_at: str
    section_404_category: str
    statutory_anchor: str


# ---------------------------------------------------------- read response


class ActivityEventOut(BaseModel):
    event_id: str
    schema_version: str
    registry_scope: str
    prev_event_hash: str
    self_hash: str
    timestamp: str
    primary_actor_id: str
    activity_type: str
    activity_subject: dict
    work_unit: dict
    evidence_hash: str
    evidence_uri: Optional[str] = None
    evidence_storage: str
    section_404_category: str
    statutory_anchor: str
    reward_eligibility: dict


class EventListResponse(BaseModel):
    events: list[ActivityEventOut]
    next_cursor: Optional[str] = None


class ChainHeadResponse(BaseModel):
    scope: str
    head_hash: str


class ComplianceReportResponse(BaseModel):
    period: dict
    actor_scope: str
    event_counts_by_category: dict
    phase: str
