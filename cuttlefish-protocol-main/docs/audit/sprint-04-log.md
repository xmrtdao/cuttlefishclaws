# Sprint 4 — PVP-001 service skeleton (protocol-internal verification)

**Branch:** `feat/sprint-04-pvp-service-skeleton` (stacked on `feat/sprint-03-kya-wire-writepath`)
**Spec:** `canon/PVP-001_PRINCIPAL_VERIFICATION_PROTOCOL.md`
**Status:** complete

## What was done
- New service `services/pvp/` mirroring the registry layout: `main.py` (FastAPI, port 8082), `schema.py`, `storage.py`, `pvp.py`, `requirements.txt`, `README.md`, `tests/`.
- **Protocol-internal verification — no third-party KYC vendor.** §4 methods are signed self-attestations verified via registered keys (reusing Sprint 2 `kya.py`).
- `pvp.verify_chain` runs the PVP-001 §5 flow **structurally**:
  - shape: terminates at `natural_person|legal_entity`, contiguous levels, depth ≤ 3 (AIL-001 §3.1);
  - each level's `attestor_signature` verifies; legal entities/DAOs assert `authority`; DAOs carry `governance_address`;
  - terminal `binding_proof` verifies (KYA-001 §3.2 acceptance);
  - reachability (`point_of_contact`) present;
  - deterministic `verification_hash` (idempotent);
  - emits `KYA_REGISTRATION` to the registry (mockable HTTP; `REGISTRY_ENDPOINT` config var → `localhost:8081`).
- Endpoints (PVP-001 §5): `POST /pvp/v1/verify`, `GET /pvp/v1/principals/{id}`, `POST /pvp/v1/principals/{id}/revoke`.
- IAL: PVP-1→IAL2 default; `supervised_proofing`/`notarized_attestation` → PVP-2→IAL3.
- `ops/docker-compose.yml` — registry (8081) + pvp (8082) with `depends_on` (skeleton; see placeholders).

## Tests
`services/pvp/tests/test_pvp.py` — **13 vectors**: natural-person accepted; legal-entity w/ authority accepted; depth>3 rejected; non-terminating rejected; attestation-signature failure rejected; binding_proof invalid rejected; DAO without governance_address rejected; reachability missing rejected; IAL3 for supervised proofing; KYA_REGISTRATION emitted (mocked); idempotency (same chain → same hash); revocation marks lapsed; unknown principal 404.
- `services/pvp` → **13 passed**.
- `services/cuttlefish-registry` → **68 passed** (unchanged).

## Spec interpretations
- "depth ≤ 3" enforced as `len(chain) ≤ max_delegation_depth ≤ 3`.
- `verification_hash` is computed over `canonical_json(chain)` only (no wall-clock) so resubmission is idempotent.
- Cross-service code reuse: `pvp.py` **appends** the registry dir to `sys.path` to import only `kya` (pvp's own `schema`/`storage`/`main` keep precedence).

## Placeholders & open decisions
- `TODO(PROGRAMMER)`: extract shared crypto/canonicalization into `/shared/` (pvp currently imports `kya` from `../cuttlefish-registry` via sys.path — breaks across Docker containers; `docker-compose.yml` is a non-runnable skeleton until then + Dockerfiles exist).
- `TODO(PROGRAMMER)`: real §4 proofing (document/liveness, entity good-standing) + EVS-001 evidence custody. Current verification is structural.
- `TODO(NAVIGATOR)`: add `KYA_REGISTRATION` to the registry `ActivityType` enum; and the PVP→registry emission must be KYA-signed now that the write path requires signatures (Sprint 3). The canonical principal-lapse event type (revoke) is also undecided (used `STANDING_ADJUSTED` as a placeholder).
- `TODO(NAVIGATOR)`: define the `authority` assertion shape for entities/DAOs (placeholder dict today).
