"""cuttlefish-registry — Phase 0 Activity Registry HTTP service.

Implements AR-001 §7.1 API surface against a sqlite-backed store.
Single-node, single-tenant, no authentication. Run via:

    uvicorn main:app --reload --port 8081
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from schema import (
    ChainHeadResponse,
    ComplianceReportResponse,
    EventListResponse,
    EventWriteRequest,
    EventWriteResponse,
    ActivityEventOut,
)
from storage import (
    DEFAULT_SCOPE,
    ActivityType,
    RegistryStore,
    classify_404,
    hash_evidence,
)
from trustgraph import TrustGraphEngine, TIER_FLOORS
from standing import StandingEngine
from sgq import StandingGate, required_for
import kya


_DEFAULT_DB = Path(os.environ.get("REGISTRY_DB", ".registry.sqlite"))

app = FastAPI(
    title="cuttlefish-registry",
    version="0.1.0-stub",
    description="Activity Registry pilot service (CFL-SPEC-AR-001 §10.1).",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

store = RegistryStore(_DEFAULT_DB)
trustgraph = TrustGraphEngine(store)
standing = StandingEngine(store)
gate = StandingGate(trustgraph, standing)
# KYA-001 §4.2 — in-memory binding registry the write path verifies against (Sprint 3).
# Phase-0: process-local. TODO(PROGRAMMER): back with persistent KYA storage.
kya_registry = kya.KYARegistry()


def event_request_signing_payload(req: EventWriteRequest) -> dict:
    """KYA-001 §4.1 — the canonical dict the actor signs. Client and server build this
    identically (excludes `actor_signature` and the registry-added fields). Evidence is
    intentionally out of the Sprint-3 signed scope — TODO(NAVIGATOR): decide whether
    evidence_hash must be covered by the actor signature."""
    return {
        "activity_type": req.activity_type,
        "primary_actor_id": req.primary_actor_id,
        "activity_subject": req.activity_subject.model_dump(),
        "work_unit": req.work_unit.model_dump(),
        "reward_eligibility": req.reward_eligibility.model_dump(),
        "registry_scope": req.registry_scope,
        "actor_kya_id": req.actor_kya_id,
        "key_id": req.key_id,
        "signed_at": req.signed_at,
    }


@app.get("/", include_in_schema=False)
def root():
    return {
        "service": "cuttlefish-registry",
        "spec": "CFL-SPEC-AR-001",
        "phase": "0-stub",
    }


# ------------------------------------------------------------- writes


@app.post(
    "/registry/v1/events",
    response_model=EventWriteResponse,
    status_code=201,
)
def write_event(req: EventWriteRequest) -> EventWriteResponse:
    # KYA-001 §4.2 — verify the actor signature before anything is written.
    if req.actor_kya_id is None:
        raise HTTPException(status_code=400, detail="actor_kya_id required")
    if kya_registry.get(req.actor_kya_id) is None:
        raise HTTPException(status_code=404, detail="unknown actor_kya_id")
    if not req.actor_signature or not req.key_id:
        raise HTTPException(status_code=401, detail="actor_signature and key_id required")
    try:
        signature = bytes.fromhex(req.actor_signature)
    except ValueError:
        raise HTTPException(status_code=401, detail="actor_signature must be hex")
    ok, reason = kya_registry.verify_event_signature(
        req.actor_kya_id,
        req.key_id,
        event_request_signing_payload(req),
        signature,
        req.signed_at,
    )
    if not ok:
        raise HTTPException(status_code=401, detail=f"signature verification failed: {reason}")

    try:
        atype = ActivityType(req.activity_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"unknown activity_type: {req.activity_type}",
        )

    # Evidence hash: caller may provide one, or supply a payload to hash here.
    evidence_hash = req.evidence_hash
    if not evidence_hash:
        if req.evidence_payload is None:
            raise HTTPException(
                status_code=400,
                detail="either evidence_hash or evidence_payload required",
            )
        evidence_hash = hash_evidence(req.evidence_payload)

    full_event = store.append_event(
        activity_type=atype,
        primary_actor_id=req.primary_actor_id,
        activity_subject=req.activity_subject.model_dump(),
        work_unit=req.work_unit.model_dump(),
        evidence_hash=evidence_hash,
        evidence_uri=req.evidence_uri,
        reward_eligibility=req.reward_eligibility.model_dump(),
        registry_scope=req.registry_scope,
        evidence_storage=req.evidence_storage,
    )

    return EventWriteResponse(
        event_id=full_event["event_id"],
        self_hash=full_event["self_hash"],
        written_at=full_event["timestamp"],
        section_404_category=full_event["section_404_category"],
        statutory_anchor=full_event["statutory_anchor"],
    )


# ------------------------------------------------------------- reads


@app.get(
    "/registry/v1/events/{event_id}",
    response_model=ActivityEventOut,
)
def get_event(event_id: str) -> ActivityEventOut:
    ev = store.get_event(event_id)
    if not ev:
        raise HTTPException(status_code=404, detail="event not found")
    return ActivityEventOut(**ev)


@app.get(
    "/registry/v1/events",
    response_model=EventListResponse,
)
def list_events(
    actor_id: Optional[str] = None,
    activity_type: Optional[str] = None,
    scope: Optional[str] = None,
    section_404: Optional[str] = Query(None, pattern="^(i|ii|iii|null)$"),
    limit: int = Query(100, ge=1, le=1000),
) -> EventListResponse:
    events = store.list_events(
        actor_id=actor_id,
        activity_type=activity_type,
        scope=scope,
        section_404=section_404,
        limit=limit,
    )
    return EventListResponse(
        events=[ActivityEventOut(**e) for e in events],
        next_cursor=None,
    )


@app.get(
    "/registry/v1/chain/{scope}/head",
    response_model=ChainHeadResponse,
)
def chain_head(scope: str = DEFAULT_SCOPE) -> ChainHeadResponse:
    return ChainHeadResponse(scope=scope, head_hash=store.get_chain_head(scope))


# ------------------------------------------------------------- compliance


@app.get(
    "/registry/v1/compliance/section-404",
    response_model=ComplianceReportResponse,
)
def compliance_section_404(
    frm: str = Query(..., alias="from", description="ISO-8601 UTC"),
    to: str = Query(..., description="ISO-8601 UTC"),
    actor_id: Optional[str] = None,
) -> ComplianceReportResponse:
    return ComplianceReportResponse(**store.compliance_report(actor_id, frm, to))


# ------------------------------------------------------------- trustgraph (TG-001)


@app.get("/trustgraph/v1/{actor_id}")
def trust_score(
    actor_id: str,
    tier: str = Query("developer", description="CAC tier for seed/floor (TG-001 §4)"),
    as_of: Optional[int] = Query(
        None, description="epoch seconds; omit for now (TG-001 §5 deterministic replay)"
    ),
):
    """Current TrustGraph score for an agent (TG-001 §7).

    Behavioral, not financial: this score earns no reward. It is a deterministic
    projection of the agent's AR-001 events under the TG-001 §4 rubric.
    """
    if tier.lower() not in TIER_FLOORS:
        raise HTTPException(status_code=400, detail=f"unknown tier: {tier}")
    return trustgraph.score(actor_id, tier=tier, as_of=as_of)


@app.get("/trustgraph/v1/{actor_id}/history")
def trust_history(actor_id: str, limit: int = Query(100, ge=1, le=1000)):
    """Score-affecting events with the delta each contributed (TG-001 §7)."""
    return {"agent": actor_id, "events": trustgraph.history(actor_id, limit=limit)}


# ------------------------------------------------------------- stewardship standing (SS-001)


@app.get("/standing/v1/{actor_id}")
def standing_all(actor_id: str, as_of: Optional[int] = Query(None)):
    """Per-domain Stewardship Standing for an agent + council-eligibility (SS-001 §9).

    Earned competence, not capital: domain-bounded, cross-domain isolated.
    """
    return standing.all_domains(actor_id, as_of=as_of)


@app.get("/standing/v1/{actor_id}/{domain}/history")
def standing_history(actor_id: str, domain: str, limit: int = Query(100, ge=1, le=1000)):
    """Standing-affecting events in one domain (SS-001 §9)."""
    return {"agent": actor_id, "domain": domain, "events": standing.history(actor_id, domain, limit=limit)}


@app.get("/standing/v1/{actor_id}/{domain}")
def standing_domain(actor_id: str, domain: str, as_of: Optional[int] = Query(None)):
    """Stewardship Standing in one domain: value, ladder tier, provisional flag (SS-001 §9)."""
    return standing.domain(actor_id, domain, as_of=as_of)


# ------------------------------------------------------------- standing gate (SGQ-001)


class GateQuery(BaseModel):
    actor_kya_id: str
    activity_type: str
    domain: str
    cac_tier: str = "developer"
    ial: str = "IAL2"
    as_of: Optional[int] = None
    purpose: str = "reward"


@app.post("/gate/v1/evaluate")
def gate_evaluate(q: GateQuery):
    """Two-axis gate decision (SGQ-001 §2): TrustGraph AND Standing AND tier AND IAL.

    'Fail on either axis' — allowed only if every axis passes; `reasons` lists all failures.
    The gate composes the TG-001 and SS-001 engines; it computes nothing of its own.
    """
    return gate.evaluate(
        actor_kya_id=q.actor_kya_id,
        activity_type=q.activity_type,
        domain=q.domain,
        cac_tier=q.cac_tier,
        ial=q.ial,
        as_of=q.as_of,
        purpose=q.purpose,
    )


@app.get("/gate/v1/thresholds")
def gate_thresholds(activity_type: str, domain: str = "", tier: str = "developer"):
    """The required.* thresholds the gate applies for an (activity_type, domain, tier) (SGQ-001 §4)."""
    return required_for(activity_type, domain, tier)
