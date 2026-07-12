# Reward Router Contract Specification v1.0

**Cuttlefish Labs — CAC Protocol**
**Section 404 Compliance Layer — Reward Distribution**

---

**Document ID:** CFL-SPEC-RRC-001
**Version:** 1.0 (draft)
**Date:** 2026-06-27
**Status:** Architectural spec, pre-implementation
**Companion to:** CFL-SPEC-PRP-001 (§8 Reward Distribution), CFL-SPEC-AR-001 (§7.2 Reward Router Subscription)
**Classification:** Internal + AI Ethics Group deliverable
**Conforms to:** CFL-DECISION-001 ($E2R not TRIB; §404 activity-triggered rewards, no balance accrual; Developer/Studio/Enterprise/Anchor tiers)

---

## 1. Purpose

The Reward Router is the component that turns an **Activity Registry event into a reward**. It is the named-but-unwritten dependency in PRP-001 §8.2 and AR-001 §7.2. Every reward distribution across the four tiers (USDC activity reward, CAC compute-credit top-up, governance-tier upgrade, $E2R contribution credit) originates here, and **only** here.

The Router exists to enforce one invariant above all others:

> **A reward is paid if and only if a qualifying, signed, registry-written ActivityEvent declares it eligible. No event, no reward. No balance, no reward. No time, no reward.**

This is the architectural guarantee that Section 404(a)'s prohibition on balance- or tenure-accrued yield is never violated, because the Router has no concept of a balance or a duration — it can only act on discrete activity events.

---

## 2. Design Principles

Non-negotiable. They govern every implementation choice.

1. **Event-triggered only.** The Router's sole input is a `reward_eligible` ActivityEvent (AR-001 §7.2). It has no timer, no cron, no balance scan. There is no code path that pays anything on a schedule or on a held amount.
2. **Deterministic.** Given an event and the ruleset version, the reward output is a pure function. Two independent Router instances processing the same event produce identical distributions.
3. **Idempotent / exactly-once-effective.** Re-delivery of the same `event_id` (AR-001 uses at-least-once delivery) never double-pays. Idempotency is keyed on `event_id`.
4. **§404-bound.** The Router refuses to act on any event whose `section_404_category` is `null` for a §404-scoped reward tier, or whose category/ActivityType pairing violates the AR-001 §3.4 canonical mapping.
5. **Write-back to the Registry.** Every distribution the Router performs is itself written back to AR-001 as a new event (`CAC_TOPUP`, `TIER_UPGRADE`, `CONTRIBUTION_CREDIT_ACCRUED`, or a Tier-1 settlement event), so the audit trail is closed-loop.
6. **POS-001 vocabulary.** Outputs and logs use *activity reward*, *compute-credit top-up*, *contribution credit*. Never *yield*, *interest*, *APY*, *savings*, *dividend*, *return*.
7. **Reversible on correction.** When AR-001 emits a `CORRECTION_ISSUED` voiding a prior event (AR-001 §4.3), the Router recomputes that event's eligibility to zero and issues a compensating event; already-distributed rewards are clawed back per §6.

---

## 3. Position in the stack

```
Builder Steward / agent does work
        ↓ (evidence off-registry)
Activity Registry (AR-001)  ── writes signed ActivityEvent, sets reward_eligibility
        ↓ SUBSCRIBE registry.events.reward_eligible   (AR-001 §7.2, at-least-once)
┌─────────────────────────────────────────────┐
│  REWARD ROUTER (this spec)                   │
│   1. intake + idempotency gate               │
│   2. eligibility re-verification             │
│   3. per-tier routing + amount computation   │
│   4. anti-evasion checks                      │
│   5. distribution (4 tier handlers)          │
│   6. write-back to Registry                  │
└─────────────────────────────────────────────┘
        ↓                ↓               ↓                 ↓
   Tier 1: USDC    Tier 2: CAC     Tier 3: governance   Tier 4: $E2R
   activity        compute-credit  tier upgrade         contribution
   reward          top-up          (Developer→…→Anchor) credit accrual
```

---

## 4. Intake and idempotency

```
on_event(e: ActivityEvent):
    if seen(e.event_id):                      # idempotency gate
        return ack()                          # already processed; no-op
    if not registry.verify_written(e):        # event must be canonically written
        return nack("event not in registry")
    if not any(e.reward_eligibility.*):       # nothing to do
        record_seen(e.event_id); return ack()
    route(e)
    record_seen(e.event_id)
    return ack()
```

- `seen()` is backed by a durable idempotency table keyed on `event_id` (UUID v7), retained indefinitely.
- The Router **never** trusts the inbound payload's `reward_eligibility` blindly; it re-derives eligibility from `activity_type`, `section_404_category`, `work_unit`, and the ruleset (§5), and intersects with the event's declared eligibility. The narrower of the two wins.

---

## 5. Per-tier routing logic

The Router evaluates each eligible tier independently. An event may trigger more than one tier (e.g., a completed validation both pays USDC and accrues $E2R contribution credit), but each tier is gated separately.

### 5.1 Tier 1 — USDC activity reward  (§404(i)/(ii)/(iii))
- **Trigger:** `reward_eligibility.tier_1_usdc` and a non-null `section_404_category`.
- **Amount:** `base_rate[activity_type] × work_unit.quantity × quality_multiplier(work_unit.quality_score)`, clamped to `[min, per_event_cap]` from the active rate card.
- **Constraint:** Tier-1 amounts are **activity-priced, not balance-priced.** The rate card is its own governed, versioned config — **RATECARD-001** (its Appendix A holds the Phase-1 values; the Router *reads* it and never invents amounts; changes are governance events, never silent).
- **Distribution:** instructs the payments rail to send USDC to the actor's settlement address (resolved via KYA-001). Writes back a `PAYMENT_SETTLEMENT` event.

### 5.2 Tier 2 — CAC compute-credit top-up  (§404(iii))
- **Trigger:** `tier_2_cac`.
- **Amount:** compute-credit units per the rate card. This is **prepaid inference credit**, denominated against ComputeOracle rates — a *consumptive utility credit*, not a monetary balance.
- **Constraint:** credits are non-withdrawable and burn on inference (paired `CAC_BURN_INFERENCE` / `INFERENCE_CONSUMPTION` events). No interest accrues on held credit — there is no accrual path in the Router.
- **Distribution:** calls the CAC card service to add credit; writes back `CAC_TOPUP`.

### 5.3 Tier 3 — governance-tier upgrade  (§404(iii))
- **Trigger:** `tier_3_governance` and the actor meets the threshold for the next tier (**Developer → Studio → Enterprise → Anchor**) per accumulated qualifying events and Stewardship Standing (AIL-001).
- **Amount:** a tier transition (discrete), not a quantity. Idempotent per (actor, target_tier).
- **Constraint:** tier is earned through verified activity + Standing, never purchased to obtain rewards. The Router only *grants* tiers that the rules already entitle; it never sells them.
- **Distribution:** updates the membership record; writes back `TIER_UPGRADE`.

### 5.4 Tier 4 — $E2R contribution credit  (securities rail — handled with care)
- **Trigger:** `tier_4_e2r`.
- **Mechanic:** the Router accrues **contribution credit** (`CONTRIBUTION_CREDIT_ACCRUED`), an internal ledger entry. It does **not** issue $E2R. Conversion of accrued credit into $E2R (`CONTRIBUTION_CREDIT_CONVERTED`) happens **only** at defined milestones, **only** for accreditation-verified recipients, and **only** under the live Reg A+ / counsel-approved issuance process. The Router emits a conversion *request*; an out-of-band, gated issuance authority executes it. **The three conversion gates — defined milestones, accreditation verification, and the Reg A+ issuance process — are specified in the $E2R stack (`../CAC_Frameworks/E2R_REG_A_FEASIBILITY.md`, `…_OFFERING_CIRCULAR_OUTLINE.md`), not in this spec.** RRC-001's responsibility ends at the request.
- **Constraint (load-bearing):** $E2R is a **registered security** (CFL-DECISION-001 D-1). The Router must keep the §404 utility rails (Tiers 1–3) and the securities rail (Tier 4) **operationally separate** — separate ledgers, no automatic conversion, no path where holding CAC or accruing credit auto-issues $E2R. Tier-4 events carry a hard flag that routes them through the securities-controls module, never the utility payment rail.

---

## 6. Anti-evasion and corrections

- **No accrual surfaces.** Static analysis / review gate: the Router codebase must contain no balance read, no elapsed-time computation, and no scheduled job that produces a distribution. (This is auditable and should be a CI check.)
- **De-duplication.** Beyond `event_id` idempotency, the Router detects split-work evasion (one work product fragmented into many events to inflate reward) via `activity_subject` + actor clustering; flagged clusters route to manual review.
- **Void/clawback.** On `CORRECTION_ISSUED` (action=void) for a previously-rewarded event: Tier-1 USDC → clawback invoice or offset against future rewards; Tier-2 CAC → debit unspent credit; Tier-3 → tier reversal if the upgrade depended on the voided event; Tier-4 → reverse accrued credit (and, if already converted, flag to securities authority). All clawbacks are themselves `SLASH_APPLIED` / compensating events.
- **Standing gate.** Before any tier pays, the Router calls the **Standing Gate Query Service (SGQ-001)** — the single service that confirms the actor held the required Stewardship Standing (+ tier + IAL) for that `activity_type` at the event timestamp (evaluated over AIL-001 Standing). Defective-work liability (AIL-001 §6 cascade) can suspend reward eligibility independently.

---

## 7. Interfaces

```
# Inbound (from AR-001 §7.2)
SUBSCRIBE registry.events.reward_eligible   → on_event(ActivityEvent)   # ack required

# Outbound distribution calls
payments.send_usdc(actor_settlement_addr, amount, memo=event_id)
cac_card.topup(actor_cac_id, credit_units, memo=event_id)
membership.upgrade_tier(actor_id, target_tier, memo=event_id)
securities.request_e2r_conversion(actor_id, credit_units, milestone_id)   # gated, async

# Write-back (to AR-001 §7.1)
POST /registry/v1/events   → PAYMENT_SETTLEMENT | CAC_TOPUP | TIER_UPGRADE
                              | CONTRIBUTION_CREDIT_ACCRUED | SLASH_APPLIED

# Operations
GET  /router/v1/distributions?event_id=…     → distribution record(s)
GET  /router/v1/ratecard                      → active rate card + version
GET  /router/v1/health                        → subscription lag, dedup table size
```

The rate card and tier-threshold tables are versioned config, changed only by governance events recorded in AR-001.

---

## 8. Failure modes

| Failure | Mitigation |
|---|---|
| Duplicate delivery | `event_id` idempotency gate (§4) |
| Distribution call succeeds, write-back fails | Two-phase: reserve → distribute → write-back; reconciler replays missing write-backs from distribution log |
| Distribution rail down (USDC/CAC) | Reward marked `pending`, retried with backoff; event remains eligible until settled; never silently dropped |
| Rate card mid-change | Each event pinned to the rate-card version live at its `timestamp`, not at processing time |
| Eligibility inflated by malformed event | Router re-derives eligibility; narrower-wins (§4) |
| Tier-4 routed through utility rail | Hard schema flag + separate module; CI test asserts no Tier-4 path reaches `payments.send_usdc` |
| Clawback on already-converted $E2R | Cannot reverse a security silently; escalate to securities authority + AIL-001 cascade |

---

## 9. Section 404 posture

The Router is the enforcement point for the §404 activity-reward thesis:
- It consumes only events that already carry a `section_404_category` and a verbatim `statutory_anchor` (AR-001 §3.4).
- It has **no** balance or duration inputs — structurally incapable of paying §404(a)-prohibited yield.
- Tier-4 ($E2R) is explicitly outside the §404 utility framing and is handled as a security, preserving rail separation (POS-001 §10).

A reviewer should be able to read the Router source and conclude, in one pass, that no reward can be produced except as a function of a discrete, signed, classified activity event.

---

## 10. Phased implementation

| Phase | Scope |
|---|---|
| **Phase 1 (pilot)** | Single-instance Router; Tiers 1–2 only (USDC + CAC top-up); webhook intake from sqlite registry; manual rate card; full write-back. Tiers 3–4 stubbed (record intent, no execution). |
| **Phase 2** | Add Tier 3 (governance upgrades) wired to membership service; idempotency table to Postgres; reconciler; CI anti-accrual check. |
| **Phase 3** | Add Tier 4 contribution-credit accrual ledger (accrual only; conversion stays manual/gated under counsel); securities-controls module; clawback automation. |
| **Phase 4** | Multi-instance Router with leader election; MPC-signed write-backs; sponsor-scoped rate cards per campaign. |

---

## 11. Open questions

1. **Rate-card governance.** Who ratifies base rates and per-event caps — Council Stewards, Navigator, or DAO vote? (Defer to `COUNCIL_CHARTER.md`.)
2. **Clawback enforceability.** Tier-1 USDC clawback is hard once settled; is offset-against-future-rewards sufficient, or is a small held remediation reserve needed (cf. AIL-001 §6 Pool layer)?
3. **$E2R conversion milestones.** What defines a conversion milestone, and how does accreditation verification interface here? (Belongs partly to the E2R / Reg A+ stack.)
4. **Quality multiplier curve.** Linear vs threshold vs rubric-defined. Recommend rubric-defined per domain.

---

## 12. Next concrete implementation steps

1. Define the Phase-1 rate card (Tier-1 USDC base rates per `activity_type`; Tier-2 credit units) as versioned config.
2. Implement `on_event` + idempotency gate + eligibility re-derivation against AR-001 schema.
3. Wire Tier-1 (payments) and Tier-2 (CAC card service) handlers + write-back.
4. Add the CI anti-accrual static check (no balance reads, no timers, no scheduled distributions).
5. Stub Tiers 3–4 with record-only behavior for the pilot.

---

**Maintainer:** Cuttlefish Labs (Navigator) + collaborating Builder Stewards

**Companion documents:**
- `PROPOSAL_TO_REWARD_PIPELINE_v1.md` (PRP-001 §8) — parent
- `ACTIVITY_REGISTRY_V1.txt` (AR-001 §7.2) — event source
- `KYA_SIGNATURE_SPEC.md` (KYA-001) — actor/settlement identity resolution (pending)
- `EVIDENCE_STORAGE_SPEC.md` (EVS-001) — evidence referenced by routed events (pending)
- `AGENT_IDENTITY_AND_LIABILITY_FRAMEWORK.md` (AIL-001 §6) — Standing gate + clawback cascade
- `CAC_SECTION_404_POSITIONING.md` (POS-001) — vocabulary discipline
