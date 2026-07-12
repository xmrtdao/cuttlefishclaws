"""cuttlefish-rrc — Reward Router service (CFL-SPEC-RRC-001).

Phase-1 skeleton: Tiers 1-2 mocked (record-only + write-back), Tiers 3-4 stubbed. Run:

    uvicorn main:app --reload --port 8083
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

import rrc
import storage
from schema import InboundEvent, RouteResponse

app = FastAPI(
    title="cuttlefish-rrc",
    version="0.1.0-stub",
    description="Reward Router pilot service (CFL-SPEC-RRC-001).",
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

store = storage.RouterStore()


@app.get("/", include_in_schema=False)
def root():
    return {"service": "cuttlefish-rrc", "spec": "CFL-SPEC-RRC-001", "phase": "1-stub", "port": 8083}


@app.post("/router/v1/events", response_model=RouteResponse)
def on_event(event: InboundEvent) -> RouteResponse:
    """Intake a reward_eligible event and route it (RRC-001 §4-§5).

    TODO(PROGRAMMER): before paying, the Router must call the Standing Gate (SGQ-001, RRC-001 §6)
    to confirm the actor held the required Standing/tier/IAL at the event timestamp. Not wired here.
    """
    return rrc.route(event, store)


@app.get("/router/v1/distributions")
def distributions(event_id: str = Query(...)):
    recs = store.distributions(event_id)
    if recs is None:
        raise HTTPException(status_code=404, detail="event_id not processed")
    return {"event_id": event_id, "distributions": recs}


@app.get("/router/v1/ratecard")
def ratecard():
    return rrc.RATE_CARD_REGISTRY.active().as_dict()


@app.get("/router/v1/health")
def health():
    return {
        "status": "ok",
        "dedup_table_size": store.size(),
        "ratecard_version": rrc.RATE_CARD_REGISTRY.active().version,
    }
