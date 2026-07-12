# cuttlefish-evs — Evidence Storage (CFL-SPEC-EVS-001)

Off-registry evidence custody. The registry anchors only the **hash**; the payload lives here,
content-addressed, access-controlled, retention-classed, and erasure-safe. Port **8084**.

## Guarantees

- **Content-addressed (§3.2):** `evidence_hash = SHA-256(payload)`; anyone can `verify` a payload against the anchored hash, trustlessly.
- **PII fail-safe (§5.1.1, §6):** `contains_pii` defaults **true** → storage limited to `local`/`s3`. A public/permanent store (`ipfs`/`ar`) requires an explicit `cleared_pii`. Public visibility is refused for PII.
- **Least authority (§6):** `public` / `actor` (owner) / `sponsor` / `auditor` (time-boxed grant). Access resolved on every read; reads are logged.
- **Erasure-safe (§7):** `erase` removes the payload and leaves a **tombstone** — `GET` then returns `410`, the hash/meta remain. `legal_hold` blocks erase (`423`).

## Endpoints

```
POST /evidence/v1                         -> {evidence_hash, evidence_uri, storage_class, ...}
GET  /evidence/v1/{hash}?as=kya&now=      -> {payload} | 403 | 410(redacted) | 404
POST /evidence/v1/{hash}/verify  {payload} -> {matches}
POST /evidence/v1/{hash}/erase   {requester, reason} -> tombstone | 423(legal_hold)
POST /evidence/v1/{hash}/grant   {auditor_kya_id, ttl_seconds, now} -> {expires_at}
GET  /evidence/v1/{hash}/meta             -> metadata (no payload)
```

## Run

```
python -m pytest -q          # 13 tests
uvicorn main:app --port 8084
```

## TODO

- `TODO(PROGRAMMER)`: real backends (`s3`/`r2`, `ipfs` pinning, `ar`), encryption (aes-256-gcm / age, wrapped per KYA_ID), durable store, retention disposition jobs, AR-001 §6 HOT→WARM→COLD tiering.
- `TODO(PROGRAMMER)`: resolve access against **KYA-001 §6** identities (here it is a simple owner/sponsor/grant model).
- `TODO(NAVIGATOR)`: PII-clearance review workflow (§5.1.1) before any `ipfs`/`ar` write.
