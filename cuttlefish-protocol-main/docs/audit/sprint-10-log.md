# Sprint 10 — EVS-001 Evidence Storage service

**Branch:** `feat/sprint-10-evs-evidence` (stacked on `feat/sprint-09-srp-review-lifecycle`)
**Spec:** `canon/EVS-001_EVIDENCE_STORAGE_SPEC.md`
**Status:** complete

## What was done
- New service `services/evs/` (port 8084): `main.py`, `schema.py`, `evs.py`, `tests/`, `README.md`, `requirements.txt`.
- `evs.EvidenceService` + endpoints implementing:
  - **Content-addressing (§3.2):** `evidence_hash = SHA-256(payload)`; `verify` confirms a payload against the anchored hash trustlessly.
  - **PII fail-safe gate (§5.1.1, §6):** `contains_pii` defaults true → storage limited to `local`/`s3`; `ipfs`/`ar` require explicit `cleared_pii`; public visibility refused for PII.
  - **Least-authority access (§6):** public / actor(owner) / sponsor / auditor (time-boxed grant); resolved on every read; reads logged.
  - **Erasure-safe append-only (§7):** `erase` → tombstone (payload gone, hash remains) → `GET` returns `410`; `legal_hold` blocks erase (`423`).
- `ops/docker-compose.yml` extended with `evs` (8084).

## Tests
`services/evs/tests/test_evs.py` — **12 vectors**: content-addressed put; verify match/mismatch; PII can't use ipfs; cleared non-PII can; public refused for PII; actor owner-only access; public open; sponsor access; auditor time-boxed grant (within/after TTL); erase→410 tombstone (+meta remains); legal_hold→423; unknown→404.
- `services/evs` → **12 passed**. registry 107 / pvp 13 / rrc 13 unchanged. **145 total.**

## Placeholders & open decisions
- `TODO(PROGRAMMER)`: real backends (s3/r2, ipfs pinning, arweave), encryption (aes-256-gcm / age wrapped per KYA_ID), durable store, retention-disposition jobs, AR-001 §6 HOT→WARM→COLD tiering.
- `TODO(PROGRAMMER)`: resolve access against **KYA-001 §6** identities (simple owner/sponsor/grant model here).
- `TODO(NAVIGATOR)`: the PII-clearance review workflow (§5.1.1) gating any public/permanent write.
