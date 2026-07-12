# Sprint 5 (optional) — RRC-001 Reward Router skeleton

**Branch:** `feat/sprint-05-rrc-skeleton` (stacked on `feat/sprint-04-pvp-service-skeleton`)
**Spec:** `canon/RRC-001_REWARD_ROUTER_CONTRACT.md`
**Status:** complete

## What was done
- New service `services/rrc/` (port 8083): `main.py`, `schema.py`, `storage.py`, `rrc.py`, `requirements.txt`, `README.md`, `tests/`.
- **Phase-1 routing (RRC-001 §10):**
  - **Tier 1 (USDC activity reward)** + **Tier 2 (CAC top-up)** — computed from a mock rate card, **record-only** (no funds move), each with a registry **write-back** (`PAYMENT_SETTLEMENT` / `CAC_TOPUP`) via a mockable emit hook.
  - **Tier 3 / Tier 4** — **stubbed** (record-intent). Tier 4 carries `rail=securities` and **never** reaches the utility payment path (§5.4 rail separation, load-bearing).
- **Idempotency** on `event_id` (§4): re-delivery returns `duplicate`, no double-pay.
- **§404-bound:** Tier 1 refuses `section_404_category == null` (§5.1).
- **No accrual surfaces:** the module has no balance read, no elapsed-time, no scheduled job (§2/§6/§9).
- `ops/docker-compose.yml` extended with the `rrc` service (8083).

## Tests
`services/rrc/tests/test_rrc.py` — **12 vectors**: tier1 recorded+writeback; tier2 recorded+writeback; tier1+tier2; idempotency (no double-pay); tier1 refused on null §404; no-eligibility→no_reward; tier3 stubbed; tier4 stubbed on securities rail (never payment); USDC clamped to cap; quality multiplier; distributions endpoint (+404); ratecard/health endpoints.
- `services/rrc` → **12 passed**. (registry 68 / pvp 13 unchanged.)

## Placeholders & open decisions
- `TODO(NAVIGATOR)`: replace mock `RATE_CARD` with real **RATECARD-001** Appendix A values (governed config).
- `TODO(PROGRAMMER)`: real settlement rails (USDC / CAC card / membership / securities authority); **SGQ-001 Standing-gate call before any tier pays** (§6, not wired); **sign the write-backs** (Sprint 3 requires it); durable idempotency table; CI anti-accrual static check (§6).
- Tiers 3-4 execution, clawback/void on `CORRECTION_ISSUED` (§6), and split-work anti-evasion (§6) are out of Phase-1 scope.
