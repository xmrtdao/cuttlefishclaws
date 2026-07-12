"""EVS-001 evidence storage tests (Sprint 10)."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

import evs
import main


@pytest.fixture
def client():
    main.store = evs.EvidenceService()
    return TestClient(main.app)


def _put(client, payload="validation report v1", **kw):
    body = {"payload": payload, "owner_kya_id": "kya:agent:owner"}
    body.update(kw)
    return client.post("/evidence/v1", json=body)


# --------------------------------------------------------------- content addressing (§3.2)


def test_put_is_content_addressed(client):
    r = _put(client, payload="hello evidence")
    assert r.status_code == 201
    body = r.json()
    assert body["evidence_hash"] == hashlib.sha256(b"hello evidence").hexdigest()
    assert body["evidence_uri"].endswith(body["evidence_hash"])
    assert body["storage_class"] == "s3"          # default warm tier


def test_verify_against_hash(client):
    h = _put(client, payload="same bytes").json()["evidence_hash"]
    assert client.post(f"/evidence/v1/{h}/verify", json={"payload": "same bytes"}).json()["matches"] is True
    assert client.post(f"/evidence/v1/{h}/verify", json={"payload": "tampered"}).json()["matches"] is False


# --------------------------------------------------------------- PII gate (§5.1.1, §6)


def test_pii_object_cannot_use_ipfs(client):
    r = _put(client, contains_pii=True, storage_class="ipfs")
    assert r.status_code == 400 and "not permitted" in r.json()["detail"]


def test_cleared_non_pii_can_use_ipfs(client):
    r = _put(client, contains_pii=False, cleared_pii=True, storage_class="ipfs", visibility="public")
    assert r.status_code == 201 and r.json()["storage_class"] == "ipfs"


def test_public_visibility_rejected_for_pii(client):
    r = _put(client, contains_pii=True, visibility="public")
    assert r.status_code == 400


# --------------------------------------------------------------- access control (§6)


def test_actor_visibility_owner_reads_other_forbidden(client):
    h = _put(client, visibility="actor").json()["evidence_hash"]
    assert client.get(f"/evidence/v1/{h}?as=kya:agent:owner").status_code == 200
    assert client.get(f"/evidence/v1/{h}?as=kya:someone-else").status_code == 403


def test_public_visibility_anyone_reads(client):
    h = _put(client, contains_pii=False, cleared_pii=True, visibility="public").json()["evidence_hash"]
    assert client.get(f"/evidence/v1/{h}").status_code == 200


def test_sponsor_visibility(client):
    h = _put(client, visibility="sponsor", sponsor_kya_id="kya:sponsor").json()["evidence_hash"]
    assert client.get(f"/evidence/v1/{h}?as=kya:sponsor").status_code == 200
    assert client.get(f"/evidence/v1/{h}?as=kya:random").status_code == 403


def test_auditor_grant_time_boxed(client):
    h = _put(client, visibility="auditor").json()["evidence_hash"]
    # before grant: forbidden
    assert client.get(f"/evidence/v1/{h}?as=kya:auditor&now=1000").status_code == 403
    client.post(f"/evidence/v1/{h}/grant", json={"auditor_kya_id": "kya:auditor", "ttl_seconds": 100, "now": 1000})
    assert client.get(f"/evidence/v1/{h}?as=kya:auditor&now=1050").status_code == 200   # within ttl
    assert client.get(f"/evidence/v1/{h}?as=kya:auditor&now=2000").status_code == 403   # expired


# --------------------------------------------------------------- erasure (§7)


def test_erase_leaves_tombstone_410(client):
    h = _put(client).json()["evidence_hash"]
    assert client.post(f"/evidence/v1/{h}/erase", json={"requester": "kya:owner", "reason": "gdpr"}).json()["redacted"]
    r = client.get(f"/evidence/v1/{h}?as=kya:agent:owner")
    assert r.status_code == 410                    # gone, not a gap
    assert client.get(f"/evidence/v1/{h}/meta").json()["redacted"] is True   # hash/tombstone remains


def test_legal_hold_blocks_erase_423(client):
    h = _put(client, retention_class="legal_hold").json()["evidence_hash"]
    assert client.post(f"/evidence/v1/{h}/erase", json={"requester": "x", "reason": "y"}).status_code == 423


# --------------------------------------------------------------- misc


def test_get_unknown_404(client):
    assert client.get("/evidence/v1/deadbeef?as=x").status_code == 404
