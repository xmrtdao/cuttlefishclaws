# Pilot Scope Specification v1.0

**Cuttlefish Labs — CAC Protocol**
**One coordinated definition of "Phase 1" across the whole stack**

---

**Document ID:** CFL-SPEC-PILOT-001
**Version:** 1.0 (draft)
**Date:** 2026-06-27
**Status:** Coordinating spec — the single source for pilot scope
**Companion to:** PRP-001 (§12.2 Pilot Campaign), AR-001, RRC-001, KYA-001, EVS-001, SGQ-001, PVP-001, RATECARD-001, CAC-005
**Classification:** Internal + AI Ethics Group deliverable
**Conforms to:** CFL-DECISION-001

---

## 1. Why this exists

Each new spec defines its own "Phase 1," and those definitions did not reference each other (a drift risk). This doc is the **one** pilot scope; every spec's Phase 1 is a *view* of this, not an independent decision. PRP-001 §12.2 ("Pilot Campaign, Weeks 3-8") is the campaign context; this fixes the technical scope that supports it.

> If a spec's "Phase 1" disagrees with this doc, this doc wins. Update the spec.

---

## 2. Pilot goals

1. Run **one** end-to-end validation campaign (PRP-001 §10.1 candidate) through all five pipeline layers.
2. Pay **real** Tier-1 (USDC) and Tier-2 (CAC credit) activity rewards, event-triggered, with full audit trail.
3. Prove the §404 posture to counsel: every reward traces to a signed, classified, principal-bound event.
4. Operate under single-operator trust (Cuttlefish Labs) — multi-node consensus is explicitly **out of scope** for the pilot.

---

## 3. The single Phase-1 scope (binds all specs)

| Component | Pilot scope | Out of pilot (later phase) |
|---|---|---|
| **Activity Registry (AR-001)** | single sqlite (WAL), append-only, hourly on-chain anchor, local evidence | multi-node consensus |
| **Standing Gate (SGQ-001)** | single-node read service, `evaluate` + `thresholds`, fail-closed | signed decisions, HA, audit replay |
| **Reward Router (RRC-001)** | **Tiers 1–2 only**; Tiers 3–4 record-intent only | Tier 3 wired, Tier 4 accrual ledger |
| **Rate Card (RATECARD-001)** | one ratified Phase-1 card (Appendix A values set) | per-campaign overrides |
| **KYA (KYA-001)** | `agent` + `human` namespaces; ed25519 + secp256k1; software keys OK for human Stewards; HSM registry key | CAC on-card keys, IAL3, hybrid teams, MPC |
| **Principal Verification (PVP-001)** | **PVP-1 / IAL2**; one KYC provider; manual entity-authority review | PVP-2 / IAL3, DAO wrappers, BO checks |
| **Evidence (EVS-001)** | `local` + `s3`; `contains_pii` = **actor-flagged only**; standard + compliance retention | ipfs/ar cold tier, automated PII detection, encryption-at-rest wrapping |
| **Tiers (CAC-005 §4)** | Developer / Studio / Enterprise live; Anchor by contact; figures per CAC-005 §4 | Anchor bespoke automation |
| **$E2R (Rail B)** | **not in the compute pilot** — securities rail runs on its own Reg A+ track | — |

---

## 4. Pilot exit criteria

The pilot is complete when: one campaign has produced ≥ N validated work products; Tier-1/Tier-2 rewards have been paid and written back to AR-001; a §404 compliance report (AR-001 §8.1) has been generated and reviewed by counsel; and the Standing Gate has gated at least one ineligible attempt. (Set N with the campaign.)

---

## 5. Open questions

1. **Which campaign** — the first-wave candidate (PRP-001 §10.1) to run as the pilot. Navigator to select.
2. **KYC vendor** — PVP-001 Phase 1 needs one provider chosen (Persona / Jumio / Onfido / …). Pending selection.
3. **Pilot reward budget** — funds the RATECARD-001 Appendix-A values. Pending.

---

**Maintainer:** Cuttlefish Labs (Navigator) + collaborating Builder Stewards
**Companion documents:** PRP-001 §12, and the Phase-1 sections of AR-001 / SGQ-001 / RRC-001 / RATECARD-001 / KYA-001 / PVP-001 / EVS-001 / CAC-005 — all of which defer to this doc.
