"""cuttlefish-pvp — Principal Verification Protocol service (CFL-SPEC-PVP-001).

Phase-0, single-node, protocol-internal verification (no third-party KYC vendor). Run:

    uvicorn main:app --reload --port 8082
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import pvp
import storage
from schema import PrincipalChain, PrincipalRecordResponse, VerifyResponse

app = FastAPI(
    title="cuttlefish-pvp",
    version="0.1.0-stub",
    description="Principal Verification Protocol pilot service (CFL-SPEC-PVP-001).",
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

store = storage.PrincipalStore()


@app.get("/", include_in_schema=False)
def root():
    return {"service": "cuttlefish-pvp", "spec": "CFL-SPEC-PVP-001", "phase": "0-stub", "port": 8082}


@app.post("/pvp/v1/verify", response_model=VerifyResponse)
def verify(chain: PrincipalChain) -> VerifyResponse:
    try:
        result = pvp.verify_chain(chain)
    except pvp.VerificationError as exc:
        raise HTTPException(status_code=422, detail=f"verification failed: {exc.reason}")

    # PVP-001 §5 step 6 — emit KYA_REGISTRATION (mockable). Then store.
    pvp.emit_kya_registration(result["verification_hash"], result["principal_id"], result["ial_level"])
    store.put(result["principal_id"], chain.model_dump(), result)   # idempotent on principal_id

    return VerifyResponse(
        verification_hash=result["verification_hash"],
        principal_id=result["principal_id"],
        ial_level=result["ial_level"],
        attested_at=result["attested_at"],
    )


@app.get("/pvp/v1/principals/{principal_id}", response_model=PrincipalRecordResponse)
def get_principal(principal_id: str) -> PrincipalRecordResponse:
    rec = store.get(principal_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="unknown principal")
    return PrincipalRecordResponse(principal_id=principal_id, **rec)


@app.post("/pvp/v1/principals/{principal_id}/revoke")
def revoke(principal_id: str):
    if not store.revoke(principal_id):
        raise HTTPException(status_code=404, detail="unknown principal")
    pvp.emit_revocation(principal_id)
    return {"principal_id": principal_id, "status": "lapsed"}
