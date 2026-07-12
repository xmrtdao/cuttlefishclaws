# Architecture — Cuttlefish Protocol

The protocol stack, per `canon/CFL-NARR-003_TWO-LAYER_TRUSTGRAPH_ARCHITECTURE.md`.

## The stack

```
┌─────────────────────────────────────────────────────────────────┐
│ Application layer (Earth 2.0, validation work, Reward Router)   │
├─────────────────────────────────────────────────────────────────┤
│ SGQ-001 — Standing Gate (composes both axes; fail on either)    │
├──────────────────────────────────┬──────────────────────────────┤
│ TG-001 — TrustGraph engine       │ SS-001 — Stewardship         │
│ (behavioral, per-agent)          │ Standing engine (by domain)  │
├──────────────────────────────────┴──────────────────────────────┤
│ AR-001 — Activity Registry (the event substrate)                │
├─────────────────────────────────────────────────────────────────┤
│ Constitutional TrustGraph (the runtime detection layer)         │
│   • per-agent entity registry · 7 pattern detectors             │
│   • asymmetric local scoring · emits AR-001 events (bridge rule) │
├─────────────────────────────────────────────────────────────────┤
│ Constitutional Stack (CONSTITUTION.md + SOUL.md)                │
├─────────────────────────────────────────────────────────────────┤
│ KYA / PVP / CAC (identity + Principal + credential)             │
└─────────────────────────────────────────────────────────────────┘
```

Detection (runtime, Constitutional TrustGraph) → events (AR-001) → projection (TG-001 behavioral, SS-001 competence) → decision (SGQ-001 gate) → action.

## Services

| Folder | Spec | What it is | Port |
|---|---|---|---|
| `services/cuttlefish-registry/` | AR-001, TG-001, SS-001, SGQ-001 | The Activity Registry (append-only event log) + the deterministic engines projected from it: `trustgraph.py` (behavioral), `standing.py` (competence by domain), `sgq.py` (the gate that ANDs both axes + CAC tier + IAL). Also hosts `kya.py` (KYA-001 identity/signatures). | 8081 |
| `services/pvp/` | PVP-001 | Principal Verification Protocol — verifies the accountable principal (natural person / legal entity / DAO / delegated chain) **protocol-internally** (no third-party KYC vendor) before a KYA binding / CAC issues. Emits `KYA_REGISTRATION` to the registry. | 8082 |
| `services/rrc/` *(optional sprint)* | RRC-001 | Reward Router — routes `reward_eligible` events to settlement rails (Tier 1 USDC, Tier 2 CAC top-up, …). Mocked/record-only until the programmer wires real settlement. | 8083 |

## Identity & gating flow

1. **PVP-001** verifies the Principal chain → issues a verified principal.
2. **KYA-001** binds actor ↔ principal ↔ entitlements into a content-addressed `KYA_ID`; every registry event is signed by an actor key in a current KYA binding.
3. **AR-001** records the signed, attributable event.
4. **TG-001 + SS-001** project behavioral and competence scores from the events.
5. **SGQ-001** composes them (+ CAC tier + IAL) into "may this actor be rewarded for this activity, now?" — fail on any axis.
6. **RRC-001** routes the reward only on a passing gate decision.

## Canon

`/canon/` is the source of truth. Start at `canon/00_CANON_INDEX.md`. Naming discipline: `canon/00_NAMING_CONVENTIONS_INDEX.md` + `canon/CFL-GLOSSARY-001_CANONICAL_GLOSSARY.md`.
