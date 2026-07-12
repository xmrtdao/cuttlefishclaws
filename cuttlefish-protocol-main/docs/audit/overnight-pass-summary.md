# Cuttlefish Protocol — Build Pass Summary

Recursive build of the protocol from the canon. **Sprints 0 → 11 complete.** Each sprint is a
stacked feature branch → real module → tests → PR (never merged — Navigator merges). No canon
edits, no renames, no deleted/weakened tests, no new canonical vocabulary. Every assumption is
flagged as a `TODO(NAVIGATOR)` / `TODO(PROGRAMMER)` placeholder in its `sprint-NN-log.md`.

## At a glance

- **5 services · 147 tests · 0 failures · 0 skips · 12 stacked PRs (none merged).**
- The end-to-end **spine is proven** (Sprint 11): identity → signed event → behavioral + competence scoring → gated authorization → reward eligibility.

## Services

| Service | Port | Canon implemented | Tests |
|---|---|---|---|
| **cuttlefish-registry** | 8081 | AR-001 registry · TG-001 (`trustgraph.py`) · SS-001 (`standing.py`) · SGQ-001 (`sgq.py`) · KYA-001 (`kya.py`, signature-enforced write path) · Constitutional TrustGraph runtime (`constitutional_tg.py`) · CC-001 Council (`council.py`) · SRP-001 Review (`srp.py`) | 109 |
| **pvp** | 8082 | PVP-001 — principal verification (protocol-internal) | 13 |
| **rrc** | 8083 | RRC-001 — reward router · RATECARD-001 (`ratecard.py`) | 13 |
| **evs** | 8084 | EVS-001 — evidence storage | 12 |

## Sprints

| # | What | PR | Tests Δ |
|---|---|---|---|
| 0 / 0.5 | monorepo + workflow docs | (main) / #1 | 46 |
| 1 | AR-001 enum extension (CFL-NARR-003 §5) | #2 | +5 |
| 2 | KYA-001 service module | #3 | +11 |
| 3 | wire KYA into AR-001 write path | #4 | +6 |
| 4 | PVP-001 service skeleton | #5 | +13 (pvp) |
| 5 | RRC-001 reward router | #6 | +12 (rrc) |
| 6 | Constitutional TrustGraph runtime | #7 | +13 |
| 7 | RATECARD-001 (wired into RRC) | #8 | +1 (rrc) |
| 8 | CC-001 Council anti-faction panels | #9 | +12 |
| 9 | SRP-001 Stewardship Review lifecycle | #10 | +14 |
| 10 | EVS-001 Evidence Storage | #11 | +12 (evs) |
| 11 | end-to-end protocol spine | #12 | +2 |

## Navigator decisions queued (priority)

1. Enum value casing (S1) + TG-001 deltas for the 5 detection types; whether the actor signature must cover `evidence_hash` (S3).
2. Add `KYA_REGISTRATION` to the AR-001 enum; the canonical principal-lapse event type; signed PVP/RRC→registry emissions.
3. **RATECARD-001 real values** + Council ratification (S7); Tier-3 thresholds; Tier-4 accrual.
4. CC-001 §8 open questions (draw weighting, principal-cap default, cross-domain seats); SRP-001 exact panel composition + heightened-standard mechanics.
5. EVS-001 PII-clearance workflow; multibase code + rotation-as-renewal for KYA_ID.

## Programmer review priority

1. **`/shared/` extraction** of `kya.py` crypto/canonicalization — unblocks Docker and a real cross-service (multi-process) integration; pvp/rrc currently import via sys.path.
2. **Persistence** for the in-memory stores (KYA registry, PVP, RRC dedup, EVS, council/SRP state).
3. **Real external legs:** PVP proofing (§4) + EVS backends/encryption; RRC settlement rails + SGQ-gate call before pay; signed write-backs.
4. **Branch protection** on `main`; CI running all suites + the RRC anti-accrual static check.

## How to run

```
cd services/cuttlefish-registry && python -m pytest -q   # 109
cd services/pvp && python -m pytest -q                   # 13
cd services/rrc && python -m pytest -q                   # 13
cd services/evs && python -m pytest -q                   # 12
```

Per-sprint detail: `docs/audit/sprint-NN-log.md`. Stacked branches merge in order (`0.5 → 1 → … → 11`).
