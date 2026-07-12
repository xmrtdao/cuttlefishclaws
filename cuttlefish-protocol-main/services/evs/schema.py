"""EVS-001 request/response models."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PutRequest(BaseModel):
    payload: str                         # text payload (SDK would send bytes; text for the pilot API)
    owner_kya_id: str
    contains_pii: bool = True            # §5.1.1 default true
    cleared_pii: bool = False
    retention_class: str = "standard"
    visibility: str = "actor"
    storage_class: Optional[str] = None
    sponsor_kya_id: Optional[str] = None


class PutResponse(BaseModel):
    evidence_hash: str
    evidence_uri: str
    storage_class: str
    contains_pii: bool
    retention_class: str
    visibility: str


class GrantRequest(BaseModel):
    auditor_kya_id: str
    ttl_seconds: int = 3600
    now: Optional[int] = None


class EraseRequest(BaseModel):
    requester: str
    reason: str


class VerifyRequest(BaseModel):
    payload: str
