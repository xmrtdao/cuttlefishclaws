# cuttlefish-rrc — Reward Router (CFL-SPEC-RRC-001)

Turns a **reward_eligible Activity Registry event into a reward**. Port **8083**.

> A reward is produced **only** as a pure function of a discrete, signed, classified activity event.
> No balance read, no elapsed-time, no scheduled job — structurally incapable of §404(a) yield (RRC-001 §2/§9).

## Phase-1 scope (this skeleton)

- **Tier 1 — USDC activity reward** and **Tier 2 — CAC compute-credit top-up**: computed from the rate card and **recorded only** (no funds move), each with a registry **write-back** (`PAYMENT_SETTLEMENT` / `CAC_TOPUP`) via a mockable hook.
- **Tier 3 (governance upgrade)** and **Tier 4 ($E2R contribution credit)**: **stubbed**, record-intent only. Tier 4 is flagged `rail=securities` and **never** reaches the utility payment path (RRC-001 §5.4 — rail separation).
- **Idempotency** keyed on `event_id` (re-delivery never double-pays).
- **§404-bound:** Tier 1 refuses events whose `section_404_category` is `null`.

## Endpoints

```
POST /router/v1/events                 InboundEvent -> {event_id, status, distributions[]}
GET  /router/v1/distributions?event_id -> recorded distributions for an event
GET  /router/v1/ratecard               -> active (mock) rate card + version
GET  /router/v1/health                 -> dedup table size, ratecard version
```

## Run

```
python -m pytest -q          # 12 tests
uvicorn main:app --port 8083
```

## TODO

- `TODO(NAVIGATOR)`: replace the mock `RATE_CARD` with real **RATECARD-001** Appendix A values (governed config).
- `TODO(PROGRAMMER)`: real settlement rails (USDC / CAC card service / membership / securities authority); call the **Standing Gate (SGQ-001)** before any tier pays (RRC-001 §6); sign the registry write-backs (Sprint 3 requires it); durable idempotency table; CI anti-accrual static check (RRC-001 §6).
