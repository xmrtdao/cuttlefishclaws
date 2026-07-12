"""cuttlefish-evs — Evidence Storage service (CFL-SPEC-EVS-001). Port 8084.

    uvicorn main:app --reload --port 8084
"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

import evs
from schema import EraseRequest, GrantRequest, PutRequest, PutResponse, VerifyRequest

app = FastAPI(title="cuttlefish-evs", version="0.1.0-stub",
              description="Evidence Storage pilot service (CFL-SPEC-EVS-001).")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

store = evs.EvidenceService()


def _guard(fn):
    try:
        return fn()
    except evs.EvidenceError as exc:
        raise HTTPException(status_code=exc.code, detail=exc.reason)


@app.get("/", include_in_schema=False)
def root():
    return {"service": "cuttlefish-evs", "spec": "CFL-SPEC-EVS-001", "phase": "1-stub", "port": 8084}


@app.post("/evidence/v1", response_model=PutResponse, status_code=201)
def put_evidence(req: PutRequest) -> PutResponse:
    obj = _guard(lambda: store.put(
        payload=req.payload.encode("utf-8"), owner_kya_id=req.owner_kya_id,
        contains_pii=req.contains_pii, cleared_pii=req.cleared_pii,
        retention_class=req.retention_class, visibility=req.visibility,
        storage_class=req.storage_class, sponsor_kya_id=req.sponsor_kya_id,
    ))
    return PutResponse(
        evidence_hash=obj.evidence_hash, evidence_uri=obj.evidence_uri(),
        storage_class=obj.storage_class, contains_pii=obj.contains_pii,
        retention_class=obj.retention_class, visibility=obj.visibility,
    )


@app.get("/evidence/v1/{evidence_hash}")
def get_evidence(evidence_hash: str, as_kya: Optional[str] = Query(None, alias="as"),
                 now: Optional[int] = Query(None)):
    payload = _guard(lambda: store.get(evidence_hash, as_kya_id=as_kya, now=now))
    return {"evidence_hash": evidence_hash, "payload": payload.decode("utf-8")}


@app.post("/evidence/v1/{evidence_hash}/verify")
def verify_evidence(evidence_hash: str, req: VerifyRequest):
    return {"evidence_hash": evidence_hash, "matches": store.verify(evidence_hash, req.payload.encode("utf-8"))}


@app.post("/evidence/v1/{evidence_hash}/erase")
def erase_evidence(evidence_hash: str, req: EraseRequest):
    obj = _guard(lambda: store.erase(evidence_hash, req.requester, req.reason))
    return {"evidence_hash": evidence_hash, "redacted": obj.redacted}


@app.post("/evidence/v1/{evidence_hash}/grant")
def grant_evidence(evidence_hash: str, req: GrantRequest):
    expires_at = _guard(lambda: store.grant(evidence_hash, req.auditor_kya_id, req.ttl_seconds, now=req.now))
    return {"evidence_hash": evidence_hash, "auditor_kya_id": req.auditor_kya_id, "expires_at": expires_at}


@app.get("/evidence/v1/{evidence_hash}/meta")
def meta_evidence(evidence_hash: str):
    obj = store.meta(evidence_hash)
    if obj is None:
        raise HTTPException(status_code=404, detail="unknown evidence")
    return {
        "evidence_hash": obj.evidence_hash, "storage_class": obj.storage_class,
        "contains_pii": obj.contains_pii, "visibility": obj.visibility,
        "retention_class": obj.retention_class, "redacted": obj.redacted,
    }
