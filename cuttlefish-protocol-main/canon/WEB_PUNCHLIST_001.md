# Website Propagation Punch-List (CFL-DECISION-001 → WEB-001)

**Document ID:** CFL-WEB-PUNCH-001
**Date:** 2026-06-27
**Target:** `../WEBSITE_REBUILD_SPEC.md` (CFL-SPEC-WEB-001) and the deployed sites (cuttlefishlabs.io / cuttlefishclaws.com)
**Source of truth:** `CFL-DECISION-001`, `CAC_PROTOCOL_CANONICAL_SPEC_v5.md`
**Analogue:** this is for the website what `REVIEW_REPORT.md` §L is for the repo.

---

## 0. Headline finding

**The website *spec* (WEB-001) is already canon-aligned.** It was written in May 2026 from the real CFL-SPEC corpus, *before* the June-26 bundle drift — so it never adopted "TRIB," APY, or the "buy CAC + buy REIT" framing. Unlike the repo, there is almost nothing to *correct* in the spec; the work is (a) a few precision tightenings, and (b) **execution** — the deployed site still lags both the spec and the canon.

---

## 1. Verification matrix (WEB-001 vs the ratified decisions)

| Decision | WEB-001 status | Evidence |
|---|---|---|
| **D-1 $E2R (not TRIB)** | ✅ aligned | `$E2R` throughout; dedicated `/e2r` page (§3.8) as a registered security; "TRIB" absent |
| **D-2 Builder Stewards retained** | ✅ aligned | nav item, dedicated `/builder-stewards` page (§3.7), Stewardship Standing, AI Stewards under AIL-001 |
| **D-3 no APY/§404 rewards** | ✅ aligned | hard-bans APY/yield/savings (§§28,83,176,182,259); "activity reward"/"validation payment" vocabulary; §404 framing |
| **D-4 lead with the engine** | ✅ aligned | home leads with Earth 2.0 platform / AI-native planning / distributed validation; the Proposal-to-Reward Pipeline is the CAC-page centerpiece — **not** "buy CAC + buy REIT" |
| **D-5 Governance Agents = Builder Stewards** | ✅ aligned | treats AI Stewards as holding Stewardship Standing under AIL-001; no "Governance Agent" as a separate class |
| **D-6 Developer/Studio/Enterprise/Anchor** | ⚠️ **tighten** | §3.7 item 3 says "Steward tiers — (Based on **CAC Canonical Spec v4** — confirm current tier structure before publishing)" — the one stale reference |
| **Two-rail separation** | ✅ aligned | §3.8 item 3 calls the CAC↔$E2R separation "the most legally sensitive content"; CAC pages forbid $E2R references |

---

## 2. Tightening items (small, do before publishing the affected pages)

**P1 — fix the stale tier reference**
- **`WEBSITE_REBUILD_SPEC.md` §3.7 item 3** — replace "Based on CAC Canonical Spec v4 — confirm current tier structure" with: *"CAC membership tiers per `CAC-005` §4 — Developer $500 / Studio $2,000 / Enterprise $7,500 / Anchor from $25,000 (annual)."* v4 is stale; v5 (CAC-005) is canon.

**P1 — distinguish the two "tier" axes (a real precision bug)**
- The spec uses "Steward tiers" (§3.7 item 3) and "what the tiers are" (§3.6 item 3) loosely. There are **two different axes** and the site must not blur them:
  - **CAC membership tiers** = Developer / Studio / Enterprise / Anchor (compute + capability; CAC-005 §4).
  - **Stewardship ladder** = Contributor → Builder Steward → Senior → Council (earned Standing; AIL-001).
- Action: on `/cac-protocol` use "membership tiers"; on `/builder-stewards` use "Stewardship ladder / Standing levels." Never present the dollar-priced CAC tiers as if they were earned Steward rank.

**P2 — "Validator Pool" display term**
- The Proposal-to-Reward Pipeline diagram (§3.6 item 5) shows "Validator Pool" — the canonical PRP-001 *layer* name. But POS-001 (and the spec's own §252) **bans "validator" for the actor**. Action: keep the internal layer name, but **display it as "Builder Steward Pool"** (or "Steward Pool") on the public diagram to avoid the banned actor term.

**P2 — contribution-credit → $E2R wording**
- §3.6 item 5 / §185 already correctly gate "conversion to $E2R" behind counsel review. Confirm the live copy uses "non-transferable validation credits" and never implies automatic conversion (matches RRC-001 §5.4 / CAC-005 §5 Tier-4: accrual only, gated conversion).

**P2 — cross-reference the canon**
- Add (internal build note, not public copy) that `/cac-protocol`, `/builder-stewards`, and `/e2r` derive from CAC-005, AIL-001, and the E2R stack respectively, so future edits trace to canon.

---

## 3. The real gap: execution, not the spec

- **The deployed `cuttlefishclaws.com` lags.** Its source (the `cuttlefishclaws-main` repo) carried the TRIB/APY/old-tier problems; the **repo is now corrected** (P0/P1/P2 sessions, `REVIEW_REPORT.md` §A–§L) but **not deployed** (gated by the README "ROTATE BEFORE DEPLOY" checklist).
- **`cuttlefishlabs.io`** (the umbrella corporate root WEB-001 targets) is **not yet built**.
- So website propagation = **build WEB-001's Phase-1 pages** (home, Earth 2.0, Projects, BQE, Brooklyn, CAC Protocol, Builder Stewards, About — §287, all securities-content-free and launchable now), with the §2 tightenings folded in. The `/e2r` page stays unbuilt-or-unpublished until securities counsel clears it (§288-289).

---

## 4. Next actions (ordered)

1. Apply the four §2 P1/P2 tightenings into `WEBSITE_REBUILD_SPEC.md` (a 10-minute spec edit) so the build target is unambiguous.
2. Build WEB-001 Phase-1 pages (no securities content → no counsel gate).
3. Decide cuttlefishclaws.com's fate: rebuild from the corrected repo, or 301 → cuttlefishlabs.io (Domain strategy, WEB-001 / corpus).
4. Hold `/e2r` for counsel; everything else can ship.

---

*Read-only analysis. The website spec and the repo were not modified by this punch-list.*
