# Sprint 7 — RATECARD-001 governed rate card (wired into RRC)

**Branch:** `feat/sprint-07-ratecard` (stacked on `feat/sprint-06-constitutional-tg`)
**Spec:** `canon/RATECARD-001_REWARD_RATE_CARD.md`
**Status:** complete

## What was done
- `services/rrc/ratecard.py` — the **RATECARD-001 §2 locked structure** as code: `RateCard` (version, effective_from, ratified_by, currency, tier_1_usdc/tier_2_cac/tier_3_governance/tier_4_e2r, anti_evasion) + `Tier1Rate`, and a `RateCardRegistry` that **pins the card live at an event's timestamp** (RATECARD-001 §2 / RRC-001 §8). No balance/time fields exist in the schema (by construction, §404(a)).
- Wired RRC to **read** the card instead of its inline dict (RRC-001 §5.1 — "reads it; never invents amounts"): `compute_usdc_amount`/`compute_cac_units` take the pinned `RateCard`; `route()` pins by `event.timestamp` and stamps `ratecard_version`; `/router/v1/ratecard` and `/health` report the active card.
- **Values are PLACEHOLDER** (RATECARD-001 Appendix A is all `TBD`). The pilot card carries the same figures RRC already used, now structured/versioned; version = `ratecard-001-pilot-PLACEHOLDER-v0`, `ratified_by.decision_ref = PLACEHOLDER-not-ratified`.

## Tests
`services/rrc` → **13 passed** (was 12; +1 timestamp-pinning test). registry 81 / pvp 13 unchanged. **107 total.**
- Updated **one existing assertion** (`test_ratecard_and_health_endpoints`) from the old mock version string to the new card version — the rate card legitimately gained a real version/structure; the assertion still verifies the endpoint returns a version (not weakened).

## Placeholders & open decisions
- `TODO(NAVIGATOR/COUNCIL)`: replace the placeholder pilot card with **ratified** Phase-1 values (RATECARD-001 Appendix A + §3 governance; PILOT-001 budget). Set `ratified_by.decision_ref`.
- `TODO(NAVIGATOR)`: Tier-3 thresholds (from CAC-005 §4 / SGQ-001 `/thresholds`) and Tier-4 accrual values are empty placeholders.
- `quality_multiplier` implemented as `linear` (RATECARD-001 §4 recommends rubric-defined per domain) — TODO once rubrics exist.
