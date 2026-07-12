# cuttlefish-pvp — Principal Verification Protocol (CFL-SPEC-PVP-001)

Verifies the accountable **principal** behind an agent before a KYA binding / CAC issues.
**Protocol-internal — no third-party KYC vendor.** Port **8082**.

## What it does (Sprint 4 scope = structural)

`POST /pvp/v1/verify` runs the PVP-001 §5 flow over an AIL-001 §3.4 `PrincipalChain`:

1. **Shape** — chain terminates at `natural_person | legal_entity` within `max_delegation_depth` (≤ 3), contiguous levels.
2. **Per-level** — each level's `attestor_signature` verifies over its attestation payload (via `kya.py`, Sprint 2). Legal entities / DAOs must assert `authority`; DAOs must carry a `governance_address`.
3. **Accountability** — the terminal principal's `binding_proof` verifies (KYA-001 §3.2 acceptance).
4. **Reachability** — a `point_of_contact` is recorded.
5. **verification_hash** — deterministic over the chain (idempotent).
6. **Emit** — a `KYA_REGISTRATION` event to the registry (mockable HTTP; `REGISTRY_ENDPOINT`, default `http://localhost:8081`).

## Endpoints

```
POST /pvp/v1/verify                         {principal_chain} -> {verification_hash, principal_id, ial_level, attested_at}
GET  /pvp/v1/principals/{principal_id}       -> {principal_chain, verification_hash, ial_level, attested_at, jurisdiction, status}
POST /pvp/v1/principals/{principal_id}/revoke -> marks lapsed; emits a revocation
```

## Run

```
python -m pytest -q          # 13 tests
uvicorn main:app --port 8082
```

## Known limitations / TODO

- **Shared crypto:** `pvp.py` imports `kya.py` from `../cuttlefish-registry` via `sys.path`. `TODO(PROGRAMMER)`: extract shared crypto/canonicalization into `/shared/` so each service (and Docker container) is self-contained.
- **Verification is structural**, not real proofing. `TODO(PROGRAMMER)`: integrate document/liveness and entity-registry / good-standing checks (PVP-001 §4) and EVS-001 evidence custody.
- **`KYA_REGISTRATION`** must be added to the registry `ActivityType` enum, and the emission must itself be KYA-signed (Sprint 3 made the write path require signatures). `TODO(NAVIGATOR/PROGRAMMER)`.
- `authority` and DAO `governance_address` are structurally required but their contents are placeholders (`TODO(NAVIGATOR)`: define the authority assertion shape).
