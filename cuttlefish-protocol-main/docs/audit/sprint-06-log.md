# Sprint 6 (optional) — Constitutional TrustGraph runtime layer

**Branch:** `feat/sprint-06-constitutional-tg` (stacked on `feat/sprint-05-rrc-skeleton`)
**Spec:** `canon/00_CONSTITUTION/TRUSTGRAPH.md` (Constitution v1.2 Art III) + `canon/CFL-NARR-003` §3
**Status:** complete

## What was done
- `services/cuttlefish-registry/constitutional_tg.py` — the **runtime detection layer** (distinct from the TG-001 engine; the two are layered per CFL-NARR-003, not merged).
- `ConstitutionalTrustGraph` — a single agent's immune system over the counterparties it meets:
  - **Local entity registry** seeded by type (operator 100 / known_community 60 / unknown_agent 40 / system_requester 20 / adversarial 0 — Constitution §3.2); unknown entities auto-seed on first observe.
  - **Seven pattern detectors** (`detect_patterns`): injection, social engineering, identity fishing, skill injection, coordinated probing, trust manipulation, identity inconsistency — marker/flag-driven (deterministic skeleton).
  - **Asymmetric scoring** (§3.3): negative deltas applied in full (injection −50, … identity_inconsistency −15); positive accrual capped at +15/day; score clamped `[0, 100]`.
  - **Decay** (§3.5): −2 per week of inactivity, floored at the entity's initial assignment.
  - **Bands** (§3.1): Trusted 80 / Neutral 50 / Cautious 20 / Adversarial.
  - **Bridge rule (CFL-NARR-003 §3):** a detection against a **registered** agent emits the mapped AR-001 event (injection→`SLASH_APPLIED(injection)`, skill_injection→`SLASH_APPLIED(violation_major)`, the other five → the Sprint 1 `*_DETECTED` types). Detections against **unregistered** counterparties stay local. Emission is via a mockable hook (records locally by default).

## Tests
`tests/test_constitutional_tg.py` — **13 vectors**: seed-by-type; bands; injection scores+floors; injection text-marker; each pattern's delta; multi-pattern sum; bridge registered-emits/unregistered-not; bridge event types match NARR-003; identity-inconsistency from claim mismatch; positive daily cap; decay −2/wk floored; unknown auto-seed; score never < 0.
- `services/cuttlefish-registry` → **81 passed** (was 68; +13). pvp 13 / rrc 12 unchanged. **106 total.**

## Fixes during the sprint
- Decay guard used a truthiness check on `last_seen` that treated epoch 0 as "never seen"; changed to `as_of > last_seen` (caught by the decay test). Logged here per the soft-failure policy.

## Placeholders & open decisions
- `TODO(PROGRAMMER)`: production detectors need real heuristics/NLP over live interactions; the skeleton is marker/flag-driven.
- `TODO(NAVIGATOR)`: positive-signal catalogue (which interactions earn +points and how much) is from the doctrine's "+5..+15" band but not itemized here.
- `TODO(NAVIGATOR/PROGRAMMER)`: wire `_emit` to the real (KYA-signed) AR-001 write path; the bridge currently records emission payloads for audit/tests.
- The constitutional TrustGraph's bands/floors are the **doctrine** values (Trusted 80 / Neutral 50 / Cautious 20 / Adversarial), deliberately distinct from TG-001's bands (CFL-NARR-003 D-1, preserved — not reconciled).
