# Cuttlefish Labs — Canonical Stack (Current Version)

**Status:** CURRENT — this folder is the authoritative source of truth.
**Version:** v_current (2026-06-27)
**Maintainer:** David Elze, Navigator
**Supersedes for the protocol layer:** `CAC_Frameworks/CAC_Canonical_Spec_v4.md` (stale — see §4)
**Binds:** `CFL-DECISION-001` (this folder) — the ratified reconciliation that governs every doc here.

---

## 0. What this folder is

This is a clean, internally-consistent rewrite of the Cuttlefish Labs canonical stack, built **on top of** the existing foundation in `../CAC_Frameworks/`. It exists because a June-2026 reconciliation pass (`CFL-DECISION-001`) corrected several drift points, and the protocol spec (`CAC_Canonical_Spec_v4.md`) had gone stale relative to those corrections.

**Nothing in the old foundation was deleted.** Docs that were already canon-aligned remain authoritative *in place* (`../CAC_Frameworks/`); this folder rewrites only what needed rewriting and adds what was missing, then indexes the whole set so there is one front door.

> **Rule of precedence:** Where any document anywhere disagrees with `CFL-DECISION-001`, the decision record wins. Where the protocol model is concerned, `CAC_PROTOCOL_CANONICAL_SPEC_v5.md` (this folder) wins over `CAC_Canonical_Spec_v4.md` (archived-in-place).

---

## 1. The ratified canon (decisions that bind everything)

| ID | Doc | What it locks |
|---|---|---|
| **CFL-DECISION-001** | `CFL-DECISION-001_RECONCILIATION.md` | $E2R (not "TRIB"); Builder Stewards retained (not retired); **no** balance-accrued APY/savings (§404 activity rewards only); tiers = **Developer / Studio / Enterprise / Anchor**; rail separation CAC (utility) ⟂ $E2R (security) |

Ratified by Navigator 2026-06-27 (D-1, D-2, D-3, D-6). D-4/D-5/D-7 recommended; see the record.

---

## 2. Rewritten / new in this folder (current version)

| ID | Doc | Status | Canonical for |
|---|---|---|---|
| — | `00_CANON_INDEX.md` | current | This index — the front door to the current stack |
| CFL-DECISION-001 | `CFL-DECISION-001_RECONCILIATION.md` | ratified | The binding reconciliation decisions |
| **CFL-SPEC-CAC-005** | `CAC_PROTOCOL_CANONICAL_SPEC_v5.md` | **current (supersedes v4)** | The CAC Protocol: $E2R/CAC rail separation, the four-tier reward menu, Developer/Studio/Enterprise/Anchor tiers, chains/contracts, TrustGraph, KYA, Builder Steward governance, §404 posture — **no APY** |
| CFL-SPEC-RRC-001 | `RRC-001_REWARD_ROUTER_CONTRACT.md` | draft | Registry-event → tiered reward; §404 enforcement point |
| CFL-SPEC-KYA-001 | `KYA-001_KYA_SIGNATURE_SPEC.md` | draft | KYA_ID + event signatures + Standing gate |
| CFL-SPEC-EVS-001 | `EVS-001_EVIDENCE_STORAGE_SPEC.md` | draft | Off-registry evidence custody, addressing, retention/erasure |
| CFL-SPEC-CC-001 | `CC-001_COUNCIL_CHARTER.md` | draft | Anti-faction Council-Steward governance (fills AIL-001 §11/§626) |
| CFL-SPEC-PVP-001 | `PVP-001_PRINCIPAL_VERIFICATION_PROTOCOL.md` | draft | Verifying the accountable principal before a CAC issues (fills AIL-001 §3/§676) |
| CFL-SPEC-SGQ-001 | `SGQ-001_STANDING_GATE_QUERY.md` | draft | The single "may this actor be rewarded for this activity, now?" service (referenced by CAC-005/AR-001/KYA-001/RRC-001) |
| CFL-SPEC-RATECARD-001 | `RATECARD-001_REWARD_RATE_CARD.md` | draft (structure locked, values TBD) | The governed, versioned config that prices activity rewards (home for the RRC-001 rate card) |
| CFL-SPEC-PILOT-001 | `PILOT-001_PILOT_SCOPE.md` | draft | The one coordinated "Phase 1" scope all specs defer to |
| CFL-SPEC-KEY-001 | `KEY-001_ISSUER_KEY_RUNBOOK.md` | draft (promoted, D-7) | Issuer master/operational key ceremonies, custody, rotation, compromise response (incl. the EVS evidence recovery-key) |
| CFL-SPEC-APP-001 | `APP-001_CAC_APPLET_SPEC.md` | draft v1.1 (promoted, D-7) | Java Card applet contractor brief — canon-aligned: Developer/Studio/Enterprise/Anchor tiers, snake_case fields, `did:cardano`, `soul_hash` |
| CFL-SPEC-TG-001 | `TG-001_TRUSTGRAPH_SPEC.md` | draft | The behavioral trust layer: 0–100 per-agent score, locked weight rubric, bands/lifecycle, the TrustGraph⟂Standing two-axis clarification, AR-001/SGQ-001 integration (locks CAC-005 §9) |
| CFL-SPEC-SS-001 | `SS-001_STEWARDSHIP_STANDING_SPEC.md` | draft | The earned-competence axis: per-(agent, domain) 0–100 Standing, locked recency-weighted quality EWMA (AIL-001 §4.3), cross-domain isolation, the value+time maturation ladder, §4.5 off-protocol path. Closes TG-001 §12 Q6 (the second axis is now an engine) |

### Narrative-tier (architecture & frame docs)

| ID | Doc | Status | Canonical for |
|---|---|---|---|
| CFL-NARR-003 | `../CFL-NARR-003_TWO-LAYER_TRUSTGRAPH_ARCHITECTURE.md` | v1.0 | The two-layer TrustGraph architecture: Constitutional TrustGraph (runtime) + TrustGraph engine (TG-001). Names the bridge rule that connects the runtime detection layer to the AR-001 event substrate. Resolves D-1 by layering. |

---

## 3. Foundation we build on (authoritative in place — NOT rewritten, NOT deleted)

These existing specs in `../CAC_Frameworks/` are already canon-aligned and remain the source of truth for their domains. The current stack references them; it does not duplicate them.

| ID | Doc (`../CAC_Frameworks/`) | Canonical for |
|---|---|---|
| CFL-SPEC-PRP-001 | `PROPOSAL_TO_REWARD_PIPELINE_v1.md` | The 5-layer validation→reward pipeline; the four-tier reward menu |
| CFL-SPEC-AR-001 | `ACTIVITY_REGISTRY_V1.txt` | Append-only, hash-chained event log; "no event, no reward" |
| CFL-SPEC-POS-001 | `CAC_SECTION_404_POSITIONING.md` | Vocabulary discipline (the hard-bans) — **read before writing any external copy** |
| CFL-SPEC-AIL-001 | `AGENT_IDENTITY_AND_LIABILITY_FRAMEWORK.md` | Principal hierarchy; Builder Stewards; Stewardship Standing; liability cascade |
| CFL-SPEC-CLA-001 | `CAC_CLARITY_ACT_ALIGNMENT.md` | The §404 alignment argument (all legal claims `[VERIFY]` pending counsel) |
| CFL-SPEC-SRP-001 | `STEWARDSHIP_REVIEW_PROCEDURE.md` | Stewardship Review proceedings (fills AIL-001 §7) |
| CFL-SPEC-BSR-001 | `CEPH_V3_BUILDER_STEWARD_RUNTIME.md` | Ceph V3 ↔ CAC stack: the per-agent Builder Steward runtime |
| CFL-SPEC-CCSP-001 | `CAC_CARD_SPEND_PROTECTION.md` | CAC card two-layer anti-runaway compute caps |
| CFL-SPEC-E2R-001..004 | `E2R_*.md` | $E2R as a registered security: Reg A+ Tier 2 (Form 1-A), feasibility, circular outline, counsel brief, blocking decisions |
| CFL-SPEC-SOC2-001 | `CUTTLEFISH_SOC2_READINESS.md` | SOC 2 readiness tied to the Reg A+ window |
| CFL-NARR-000/001/002 | `NEW_PROTOCOL_FOR_CIVILIZATION.md`, `CUTTLEFISH_MASTER_NARRATIVE.md`, `CUTTLEFISH_LABS_DEEP_DIVE_v1.md` | The narrative spine: Brooklyn → Over-Under → Earth 2.0 → CAC → $E2R |

> The full historical index of everything (including project-adjacent and archive material) remains `../DOCUMENT_INDEX.md`. This folder is the **canon layer** only.

---

## 4. Known stale / superseded (kept in place, do not cite as current)

| Doc | Why stale | Use instead |
|---|---|---|
| `../CAC_Frameworks/CAC_Canonical_Spec_v4.md` | Old tiers (Resident/Builder/Sovereign/Anchor), monthly pricing, a "Revenue share" column, "~4–5% APY" Howey language — all pre-`CFL-DECISION-001` | `CAC_PROTOCOL_CANONICAL_SPEC_v5.md` (this folder) |
| The June-26 `_review_context/` bundle (`CAC_Canonical_Reconciliation_v1.0.md`, `CAC_Two_Stack_Architecture_v1.0.md`, etc.) | Claude-generated; introduced "TRIB" and "Builder Steward retired" — both rejected by `CFL-DECISION-001` | `CFL-DECISION-001` + this stack. Keepers (Issuer Key Runbook, Applet Spec) to be promoted separately per D-7. |

---

## 5. Open items carried forward (write next)

> **Decision status:** `CFL-DECISION-001` is **fully ratified (D-1 through D-7)** as of 2026-06-27. The next work is propagation, in order:
> 1. **Website propagation** (D-4 locked) — punch-list **DONE** → `WEB_PUNCHLIST_001.md` (key finding: WEB-001 spec is already canon-aligned). Remaining: apply its 4 small tightenings to `WEBSITE_REBUILD_SPEC.md`, then **build** the Phase-1 pages; the deployed `cuttlefishclaws.com` lags (repo fixed, not deployed).
> 2. ~~**Promote keeper bundle docs** (D-7)~~ — **DONE** → `KEY-001`, `APP-001` (tier names + credential fields aligned to canon).
> 3. **AIL-001 clarification note** (D-5) — add one paragraph: Governance Agents (Trib/Arch) = named AI Builder Stewards.
> 4. **`DISCLOSURE_STANDARD.md`** — promote AIL-001 §8 inline standard to a standalone spec.
> 5. **Smart-contract specs** — begin the `CFL-SPEC-SC-XXX` series for the CAC-005 §10 contracts (only when a contract is actually scheduled to deploy).

Status of the carried-forward items:
- ~~`COUNCIL_CHARTER.md` (AIL-001)~~ — **DONE** → `CC-001_COUNCIL_CHARTER.md`
- ~~`PRINCIPAL_VERIFICATION_PROTOCOL.md` (AIL-001)~~ — **DONE** → `PVP-001_PRINCIPAL_VERIFICATION_PROTOCOL.md`
- ~~Standing-gate query service~~ — **DONE** → `SGQ-001`; ~~rate-card home~~ — **DONE** → `RATECARD-001`; ~~unified pilot scope~~ — **DONE** → `PILOT-001`
- `DISCLOSURE_STANDARD.md` (AIL-001 §8) — exists only inline; standalone spec **pending**
- Promote keeper bundle docs: Issuer Key Runbook → `CFL-SPEC-KEY-001`; Applet Spec → `CFL-SPEC-APP-001` (fix tier names first; gated on D-7)
- Single canonical compute/GPU figure set per tier — **committed** in CAC-005 §4 (initial values, governed-config revisable)
- Migrate the published site "CAC v4" label → v5; reconcile investor-persona names and the accredited-vs-Reg-A+ framing (repo `REVIEW_REPORT.md` §L)

*Reference: the corpus inventory was at `D:\CuttlefishLabs_Dev\repo_review\CORPUS_INDEX.md` at the time of writing (absolute path — relative paths break if this folder is relocated).*

---

*This folder is additive. No prior file or folder was deleted in its creation.*
