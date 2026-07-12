# The Two-Layer TrustGraph Architecture

**Cuttlefish Labs**

---

**Document ID:** `CFL-NARR-003`
**Version:** 1.0
**Date:** 2026-06-28
**Author:** Navigator (David Hans Elze)
**Position in stack:** narrative-tier; sits beside `CFL-NARR-000` (civilizational frame) and `CFL-NARR-001` (master narrative)
**Frames:** the layered relationship between the **Constitutional TrustGraph** (runtime) and the **TrustGraph engine** (`CFL-SPEC-TG-001`)
**Resolves:** discrepancy `D-1` in `00_CONSTITUTION/README.md` — by layering, not by reconciling
**Companion code change:** additive extension to the `AR-001` `ActivityType` vocabulary for previously-unmapped Constitutional TrustGraph detection patterns *(proposed; not yet executed — see §5 and §7)*

> Two TrustGraphs run in the Cuttlefish Labs stack. They are not duplicates and they are not in conflict. They are different layers of one system: the agent's runtime immune system and the protocol's behavioral projection of that agent. This document names the layering and the rule that connects them. It does not rename, merge, or alter either TrustGraph; both remain canonical exactly as preserved.

---

## 1. The two TrustGraphs

### The Constitutional TrustGraph (runtime)

The Constitutional TrustGraph is the per-agent **runtime immune system** specified in `TRUSTGRAPH.md` (2026-02-08, preserved verbatim in the Constitutional Archive). It runs inside an agent's reasoning context. At every interaction, it:

- Maintains an **entity registry** of every counterparty the agent has encountered (other agents, humans, skills, platforms) with a trust score, history, and flags
- Runs **seven adversarial pattern detectors** — instruction injection, social engineering, identity fishing, skill injection, coordinated probing, trust manipulation, identity inconsistency
- Applies **asymmetric scoring** (trust earned slowly, lost fast — +15/day gain cap, −50 per injection event)
- Decays inactive entities (−2/week after 7 days)
- Logs to an append-only audit log
- Exposes an operator interface

It answers the question: **"Should this agent engage with this counterparty, and at what depth?"**

The subject of its scoring is whoever the agent is talking to, from the agent's own perspective.

### The TrustGraph engine (`TG-001`)

The TrustGraph engine is the per-agent **behavioral projection** specified in `CFL-SPEC-TG-001`. It runs server-side in `cuttlefish-registry`. It is a deterministic projection of the agent's own activity in the Activity Registry under the locked rubric of `TG-001 §4–§5`:

- Seeds at the agent's CAC tier floor (Developer 30 / Studio 40 / Enterprise 55 / Anchor 70)
- Folds AR-001 events under asymmetric attenuation (`CEIL` 90, `ATTEN` 0.5)
- Applies a daily cap on micro-positives (`CAP` 10.0 / UTC day)
- Decays linearly (2.0 points per 7 days, eroding only the above-floor surplus)
- Bands at Trusted 90 / Standard 70 / Monitored 50 / Cautious 20 / Suspended 10 / Revoked
- Is consumed by `SGQ-001` alongside `SS-001` Stewardship Standing

It answers the question: **"Has this agent behaved well over time?"**

The subject of its scoring is the agent itself, from the protocol's perspective.

---

## 2. The stack

```
┌─────────────────────────────────────────────────────────────────┐
│ Application layer (Earth 2.0, validation work, Reward Router)   │
├─────────────────────────────────────────────────────────────────┤
│ SGQ-001 — Standing Gate (composes both axes; fail on either)    │
├──────────────────────────────────┬──────────────────────────────┤
│ TG-001 — TrustGraph engine       │ SS-001 — Stewardship         │
│ (behavioral, per-agent)          │ Standing engine (competence  │
│                                  │ by domain)                   │
├──────────────────────────────────┴──────────────────────────────┤
│ AR-001 — Activity Registry (the event substrate)                │
├─────────────────────────────────────────────────────────────────┤
│ Constitutional TrustGraph (the runtime detection layer)         │
│   • Per-agent entity registry                                   │
│   • Seven adversarial pattern detectors                         │
│   • Asymmetric local scoring (+15/day, −50 per injection)       │
│   • Local audit log                                             │
│   • Emits AR-001 events when the bridge rule applies            │
│   • Operator interface                                          │
├─────────────────────────────────────────────────────────────────┤
│ Constitutional Stack (CONSTITUTION.md + SOUL.md)                │
├─────────────────────────────────────────────────────────────────┤
│ KYA / PVP / CAC (identity + Principal + credential)             │
└─────────────────────────────────────────────────────────────────┘
```

The Constitutional TrustGraph sits between the Constitutional Stack and the Activity Registry. It is the layer where adversarial behavior is *detected* in real time. The Activity Registry is the layer where detections become *protocol-visible events*. The TrustGraph engine is the layer where those events become a *behavioral score*. The Standing Gate is the layer where the score becomes an *authorization decision*.

---

## 3. The bridge rule

The Constitutional TrustGraph scores every counterparty an agent meets — registered or not, trusted or adversarial. Most of that scoring stays local to the agent's own runtime; it informs how the agent engages, what depth of information it shares, whether it disengages. That is the agent's own immune response and does not need to leave the agent's reasoning context.

But when a counterparty is a **registered Cuttlefish agent** — bound to a Principal via KYA, holding a CAC, identifiable by `agent_id` — the detection has protocol-tier consequences. A registered agent that attempts prompt injection against another registered agent is not just a local nuisance; it is an agent whose behavioral track record across the protocol should reflect what it just attempted.

The bridge rule, stated once:

> **Detections by the Constitutional TrustGraph against a registered Cuttlefish agent emit Activity Registry events. Detections against unregistered counterparties stay local to the runtime layer.**

Same machinery, two subjects, one boundary. The runtime layer scores everyone; only registered subjects cross into the protocol tier.

### Detection-to-event mapping

| Constitutional TrustGraph detection | Local effect (runtime, always) | If counterparty is a registered agent (protocol effect) |
|---|---|---|
| Instruction injection | Score → 0, flag `injection_attempt`, disengage | `AR-001` `SLASH_APPLIED` (severity `injection`) → TG-001 delta per `TG-001 §4` |
| Skill injection | Source score −40, flag `skill_injection`, deny | `AR-001` `SLASH_APPLIED` (severity `violation_major`) → TG-001 delta per `TG-001 §4` |
| Social engineering (progressive probing) | Score −20, flag `social_engineering`, restrict | `AR-001` `SOCIAL_ENGINEERING_DETECTED` (new) → TG-001 delta to be ratified |
| Identity fishing | Score −15, flag `identity_fishing` | `AR-001` `IDENTITY_FISHING_DETECTED` (new) → TG-001 delta to be ratified |
| Coordinated probing (cross-entity) | Flag all participants, restrict to Tier 0 | `AR-001` `COORDINATED_PROBING_DETECTED` (new) → TG-001 delta for each participant; may open Stewardship Review affecting SS-001 |
| Trust manipulation (sprint-to-trust) | Daily gain cap enforced (already in runtime); score −25 | `AR-001` `TRUST_MANIPULATION_DETECTED` (new) → TG-001 delta to be ratified |
| Inconsistent identity claims | Score −15, flag `identity_inconsistency` | `AR-001` `IDENTITY_INCONSISTENCY_DETECTED` (new) → TG-001 delta to be ratified |

Notes on the table:

- **Existing `AR-001` event types** (`SLASH_APPLIED` with severity tags) cover the two patterns that map to severities already in the enum.
- **Five new `AR-001` event types** cover the patterns that have no existing home. They are added by the companion code change (§5). They are additive — no existing event type is changed or removed.
- **TG-001 delta values for the new event types are not assigned in this document.** The `TG-001 §4` weight rubric is the locked source of truth for protocol-tier deltas. Adding the new event types creates the *capacity* to apply a delta; the actual delta values are a future Navigator ratification against the TG-001 rubric.
- **SS-001 (Stewardship Standing) is referenced but does not yet exist as a deterministic engine.** The bridge rule names where Stewardship Review outcomes flow when SS-001 lands. Until then, those flows stay flagged for human review per the Stewardship Review process.

---

## 4. What this resolves

Discrepancy `D-1` recorded in `00_CONSTITUTION/README.md` is reframed:

| Before this document | After this document |
|---|---|
| Two TrustGraphs coexist in canon with different bands, decay rates, and scoring mechanics; "do not conflate or reconcile" | Two TrustGraphs are explicitly named as the two layers of one system: the agent's runtime immune system and the protocol's behavioral projection. The bridge rule names where they connect (the AR-001 event substrate). Both preserved exactly as written. Nothing renamed; nothing reconciled; no threshold changed. |

The Constitutional TrustGraph stays in `00_CONSTITUTION/TRUSTGRAPH.md` verbatim with its bands (Trusted 80 / Neutral 50 / Cautious 20 / Adversarial 0) and its mechanics. The TrustGraph engine stays in `CANONICAL_CURRENT/TG-001_TRUSTGRAPH_SPEC.md` verbatim with its bands (Trusted 90 / Standard 70 / Monitored 50 / Cautious 20 / Suspended 10 / Revoked) and its locked rubric. They are doing different jobs at different layers and that is correct.

The README's `D-1` note can be reframed from *"discrepancy — open Navigator decision"* to *"two layers of one system, stacked in `CFL-NARR-003`"* — a one-line additive note, no other archive edits required.

---

## 5. Companion code change — `AR-001` enum extension

> **Status: PROPOSED — not yet executed.** This section describes the code change; the change itself awaits Navigator confirmation of the enum names (§7.1) and an explicit go-ahead.

### Proposed additions

To make the bridge rule executable, the `AR-001` `ActivityType` vocabulary gains five new values:

```python
# In cuttlefish-registry/schema.py (or wherever ActivityType is defined),
# additive to the existing ActivityType enum:

SOCIAL_ENGINEERING_DETECTED   = "social_engineering_detected"
IDENTITY_FISHING_DETECTED     = "identity_fishing_detected"
COORDINATED_PROBING_DETECTED  = "coordinated_probing_detected"
TRUST_MANIPULATION_DETECTED   = "trust_manipulation_detected"
IDENTITY_INCONSISTENCY_DETECTED = "identity_inconsistency_detected"
```

These follow the existing `AR-001` naming convention (SCREAMING_SNAKE_CASE enum keys, snake_case string values, action-shaped semantics).

### Properties

- **Additive.** No existing enum value is changed, removed, or re-keyed.
- **No TG-001 delta wiring yet.** The new values can be written to and queried from `AR-001` immediately, but they are not yet mapped to TG-001 score deltas. That mapping is a Navigator ratification against the `TG-001 §4` rubric and is out of scope for this round.
- **Backward-compatible.** Existing test suites remain green.
- **Forward-compatible with SS-001.** When the Stewardship Standing engine lands, the same five event types can also feed SS-001 in their domain context.

### Test coverage for the addition

The code change is accompanied by minimal additive tests:

- One round-trip test per new event type: `write_event` accepts it, `list_events(activity_type=...)` returns it
- One round-trip test confirming an event of each new type passes through `RegistryStore` and appears in event queries with the correct `actor_id`, `timestamp`, and `details`
- Confirmation that the existing suite remains green

The new enum values gain no behavior beyond being a valid `activity_type`. Behavior (TG-001 delta application) is added in a later round, when the Navigator ratifies the delta values.

---

## 6. Boundaries — what this document does not do

- It does **not** modify `TRUSTGRAPH.md`. The archived doctrine is preserved byte-verbatim per the Constitutional Archive chain of custody.
- It does **not** modify `TG-001`. The locked rubric, bands, and computation model stand.
- It does **not** rename either TrustGraph. Both keep "TrustGraph" with the layer qualifier — "Constitutional TrustGraph" (runtime), "TrustGraph engine" (`TG-001`).
- It does **not** assign TG-001 delta values to the new event types. Those are a future Navigator ratification.
- It does **not** specify `SS-001`. The bridge rule references it as the future destination for competence-tier events; the engine itself remains the next workstream.
- It does **not** alter any threshold, weight, band, or cap in either TrustGraph.

---

## 7. Open questions — flagged, not resolved

1. **Naming of the new `AR-001` event types.** The values above (`SOCIAL_ENGINEERING_DETECTED`, etc.) follow the existing convention but are proposed, not locked. The Navigator confirms the final enum names when the code change lands.
2. **TG-001 delta values for the new event types.** The Constitutional TrustGraph applies its own local deltas (−20 social engineering, −15 identity fishing, etc.). Whether the protocol-tier TG-001 deltas should mirror those, or follow the `TG-001 §4` severity classes (minor / major / injection / fabrication), is a Navigator decision against the TG-001 rubric.
3. **The unregistered-Principal case.** A Cuttlefish agent encountering a counterparty that *claims* to be registered but fails KYA verification is detected by the Constitutional TrustGraph as identity inconsistency. The current bridge rule emits no protocol-tier event (no valid `agent_id` to record against the counterparty). Whether such failed-verification events warrant an `AR-001` entry against the *attempting* agent's `agent_id` (if it is registered) is open.
4. **Operator overrides and audit.** The Constitutional TrustGraph operator interface (`/trust set`, `/trust block`) can override scores locally. Whether overrides on registered agents should emit `AR-001` events for audit at the protocol tier is open.

---

*This document is narrative-tier. It frames the architecture; it does not specify protocol mechanics. For the runtime layer's full doctrine see `00_CONSTITUTION/TRUSTGRAPH.md`. For the engine spec see `CANONICAL_CURRENT/TG-001_TRUSTGRAPH_SPEC.md`. For the event substrate see `CANONICAL_CURRENT/CFL-SPEC-AR-001`. For the gate that composes both axes see `CANONICAL_CURRENT/SGQ-001_STANDING_GATE_QUERY.md`.*
