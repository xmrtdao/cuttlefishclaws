# Reward Rate Card Specification v1.0

**Cuttlefish Labs — CAC Protocol**
**The governed, versioned config that prices activity rewards**

---

**Document ID:** CFL-SPEC-RATECARD-001
**Version:** 1.0 (draft — structure locked, values TBD)
**Date:** 2026-06-27
**Status:** Architectural spec + config schema, pre-implementation
**Companion to:** CFL-SPEC-RRC-001 (§5 consumes this), CFL-SPEC-PRP-001 (§8 four-tier menu), CFL-SPEC-SGQ-001 (thresholds), CFL-SPEC-CC-001 (governs changes)
**Classification:** Internal + AI Ethics Group deliverable
**Conforms to:** CFL-DECISION-001 (§404 activity rewards, no balance accrual; POS-001 vocabulary)

---

## 1. Why this is its own doc (not an RRC-001 appendix)

`RRC-001` §5 prices each reward as a function of `activity_type`, `work_unit`, and a **rate card**. Rate cards change frequently (campaign by campaign, governance vote by governance vote); embedding them in the Router spec would force a spec revision on every price change. So the rate card is a **separate, versioned config artifact** with its own change-governance, referenced by RRC-001 and CAC-005 §5. The *structure* is locked here; the *values* are governed config.

> The rate card is the only place reward magnitudes live. RRC-001 reads it; it never invents amounts. A regulator/auditor can read one versioned artifact to see exactly what every activity paid, when.

---

## 2. Structure (locked)

```
RateCard {
    version:        string              // semver; pinned per event by its timestamp
    effective_from: ISO-8601 UTC
    ratified_by:    { body: enum[navigator, council, dao], decision_ref: string }   // CC-001
    currency:       "USDC"

    tier_1_usdc: {                       // §404(i)/(ii)/(iii) activity payments
        // per activity_type: base rate × work_unit.quantity × quality_multiplier, clamped
        rates: Map<ActivityType, { base: decimal, unit: string, min: decimal, per_event_cap: decimal }>
        quality_multiplier: { type: enum[linear, threshold, rubric], params: {...} }
    }
    tier_2_cac: {                        // §404(iii) compute-credit top-ups
        credits: Map<ActivityType, { credit_units: decimal, per_event_cap: decimal }>
    }
    tier_3_governance: {                 // earned tier upgrades (discrete, not priced)
        thresholds: Map<target_tier, { qualifying_events: int, min_standing: int }>
    }
    tier_4_e2r: {                        // contribution-credit accrual ONLY (Rail B)
        accrual: Map<ActivityType, { credit_points: decimal }>
        // conversion to $E2R is NOT priced here — see RRC-001 §5.4 / E2R stack
        conversion_governed_by: "E2R offering process (Reg A+ Tier 2)"
    }
    anti_evasion: { split_work_window: duration, dedup_key: "activity_subject+actor" }
}
```

- **Pinning:** an event is priced against the rate-card version live at the event's `timestamp` (RRC-001 §8), never at processing time.
- **No balance/time fields exist in this schema** — by construction there is nothing to accrue on a held balance (CLARITY §404(a); RRC-001 §2).

---

## 3. Change governance

- Rate-card changes are **proposed** by the Council (CC-001 §2.4) and **ratified** under the CC-001 §4 supermajority + timelock, within the Navigator-veto window; economic-parameter changes that touch the cooperative may also require the DAO ($E2R) axis (CC-001 §5).
- Every change emits an AR-001 governance event; the new `RateCard.version` and `ratified_by.decision_ref` are recorded. Nothing changes silently.

---

## 4. Vocabulary

Amounts are **activity rewards**, **compute-credit top-ups**, and **contribution credits** — never "yield," "return," "APY," or "interest" (POS-001 §3.2). Tier-4 is **accrual of contribution credit**, explicitly not issuance of the $E2R security.

---

## Appendix A — Phase-1 pilot rate card (PLACEHOLDER — values TBD)

Structure locked; figures to be set before code (RRC-001 §12 step 1) and ratified per §3. `TBD` = pending Navigator/Council.

| activity_type | Tier 1 base (USDC) | unit | per-event cap | Tier 2 credits | Tier 4 accrual |
|---|---|---|---|---|---|
| VALIDATION_COMPLETED | TBD | per hour | TBD | TBD | TBD |
| VALIDATION_PEER_REVIEWED | TBD | per review | TBD | TBD | TBD |
| GOVERNANCE_VOTE | n/a | — | — | TBD | TBD |
| GOVERNANCE_PROPOSAL_AUTHORED | TBD | per accepted proposal | TBD | TBD | TBD |
| ATTESTATION_ISSUED | TBD | per attestation | TBD | TBD | TBD |
| DISPUTE_RESOLUTION | TBD | per resolved case | TBD | TBD | TBD |

`quality_multiplier`: Phase 1 = **rubric-defined per domain** (recommended; RRC-001 §11 Q4). Tier-3 thresholds: see CAC-005 §4 + SGQ-001 `/thresholds`.

---

## 5. Open questions

1. **Pilot values** — the `TBD`s above; set with the pilot campaign budget (PILOT-001).
2. **Per-campaign overrides** — may a sponsor fund a higher rate for their campaign (RRC-001 Phase 4)? If so, scoping + disclosure rules.
3. **Currency** — USDC only at launch; multi-stable later? Recommend USDC-only through pilot.

---

**Maintainer:** Cuttlefish Labs (Navigator) + collaborating Builder Stewards
**Companion documents:** RRC-001 (consumer), PRP-001 §8 (menu), SGQ-001 (thresholds), CC-001 (change governance), PILOT-001 (pilot budget), POS-001 (vocabulary).
