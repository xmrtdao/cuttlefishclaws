# Sprint 11 — End-to-end protocol spine (integration)

**Branch:** `feat/sprint-11-integration-spine` (stacked on `feat/sprint-10-evs-evidence`)
**Spec:** integration across KYA-001 / AR-001 / TG-001 / SS-001 / SGQ-001
**Status:** complete

## What was done
- `services/cuttlefish-registry/tests/test_integration_spine.py` — proves the registry-internal pipeline composes as one system:
  1. A **KYA-signed** `VALIDATION_COMPLETED` event is accepted by the AR-001 write path (Sprint 3 enforcement).
  2. **TrustGraph** reflects it: score = 33 (developer floor 30 + validation +3), ACTIVE.
  3. **Stewardship Standing** reflects it in `engineering_review`: 100.0 (matured `as_of`).
  4. **SGQ Standing Gate** composes both axes and returns `allowed=true` (fail-on-either AND), with `trustgraph` + `standing` blocks.
  5. The event carries the `tier_1_usdc` / `tier_2_cac` flags **RRC-001** routes on.
- Second test: an **unsigned** event is rejected (400) before any reward path — the economy never sees work the identity layer didn't authorize.

## Tests
`tests/test_integration_spine.py` — **2 vectors** (the full spine + the unauthorized-path guard).
- `services/cuttlefish-registry` → **109 passed** (was 107; +2). pvp 13 / rrc 13 / evs 12 unchanged. **147 total.**

## Significance
This is the "new protocol for civilization" working as a chain, not parts: *identity → attributable event → behavioral & competence scoring → gated authorization → reward eligibility.* Every link is a deterministic, tested module from the canon.

## Placeholders
- The reward leg (RRC) and principal-verification leg (PVP) are proven in their own suites; a **cross-service** (multi-process, over HTTP) integration awaits the `/shared/` extraction so pvp/rrc/registry can import common crypto without module-name collisions. `TODO(PROGRAMMER)`.
