# CFL-DECISION-001 — Canon Reconciliation (Ratified)

**Document ID:** CFL-DECISION-001
**Status:** **FULLY RATIFIED — D-1 through D-7** by Navigator (David Elze) 2026-06-27. This is the binding decision record.
**Date:** 2026-06-27
**Binds:** the entire `CANONICAL_CURRENT/` stack and all downstream artifacts (repo, website, decks, specs).
**Origin:** corpus review (`/repo_review/CORPUS_INDEX.md`) — reconciles the foundational May-2026 CFL-SPEC corpus against the Claude-generated June-26 `_review_context/` bundle.

> **Rule of precedence:** where any spec, site copy, deck, contract, or doc disagrees with this record, **this record wins**.

---

## Why this exists

The repo-fix sessions used a June-26 bundle as "canonical." That bundle was Claude reconciling its *own* earlier generation against the marketing website — it never consulted PRP-001, AR-001, POS-001, AIL-001, CLA-001, or the maintained `DOCUMENT_INDEX.md`. Two of its load-bearing claims contradicted the real canon and were never ratified. This record resolves them.

---

## The ratified decisions

### D-1 — Security token is **$E2R**, not "TRIB"  ✅ RATIFIED
The registered security is **$E2R (Earth 2.0 Returns)**, offered via **Reg A+ Tier 2 (Form 1-A)** (canon also pairs a Reg D 506(c) *bridge* round). Evidence: `DOCUMENT_INDEX` Tier 1 "$E2R Securities Stack" (E2R-001..004); `PRP-001` §8 Tier 4 "$E2R Token Issuance." "TRIB" appears nowhere in the foundational corpus; the bundle's `Two_Stack` §6 itself flagged "confirm TRIB" as undecided. **"DAO-REIT" remains the structure; the security is $E2R.**

### D-2 — Builder Stewards are **retained**, not retired  ✅ RATIFIED
Builder Stewards are the central actor type (`AIL-001` §2.1 "Builder Stewards, **not** Validators"), bonded by **Stewardship Standing** (earned, domain-bounded, non-transferable), with a tier ladder (Contributor → Builder Steward → Senior → Council), `SRP-001` review procedure, and `BSR-001` runtime. `POS-001` §3 **bans** calling them "validators/stakers/node operators." The bundle's "Builder Steward retired → Governance Agent" was an unratified `DECISION NEEDED` flag justified only by the marketing site. **Site "Governance Agents" (Trib/Arch) = named AI Builder Stewards** (see D-5).

### D-3 — **No** balance-accrued APY/savings; §404 activity rewards only  ✅ RATIFIED
Rewards are **event-triggered by substantive activity, never time- or balance-accrued** (`PRP-001` §2.2-2.3; `AR-001` "no event, no reward"). CLARITY Act **§404(a)** prohibits paying interest/yield on a stablecoin balance; `POS-001` §3.2 hard-bans "yield/savings/APY/interest." The bundle/repo's **"4.5% APY savings rate on prepaid balance" is the prohibited construct** and is **removed**, not relabeled. Compute-credit incentives are expressed as **activity rewards** routed through the Activity Registry.

### D-4 — Product is the validation→reward engine, not "buy CAC + buy REIT"  ✅ RATIFIED
Lead with the five-layer Proposal-to-Reward pipeline and the four-tier reward menu (USDC activity reward / CAC compute-credit top-up / governance-tier upgrade / $E2R issuance); CAC is the compute-credit rail, $E2R the separate securities rail. **This is now the canonical product framing and gates the website IA** — the site must lead with the engine, not "buy CAC + buy REIT."

### D-5 — Governance Agents = named AI Builder Stewards  ✅ RATIFIED
Trib/Arch are AI Builder Stewards with public personas, not a separate class. **Propagation pending:** add a one-paragraph clarification to AIL-001 (a note, not a retirement). CAC-005 §6 and the repo P2-2 work already reflect this.

### D-6 — Tier names = **Developer / Studio / Enterprise / Anchor**  ✅ RATIFIED
Annual pricing $500 / $2,000 / $7,500 / from $25,000. "Builder" is reserved for the **Builder Steward actor**, never a tier. (Resident/Builder/Sovereign/Anchor is retired.)

### D-7 — Disposition of the June-26 bundle  ✅ RATIFIED
Archive the Reconciliation + Two-Stack docs (contradict canon); fold the Legislation Tracker into CLA-001 and the Product Thesis one-liner into NARR-001; **keep** the Issuer Key Runbook (→ `CFL-SPEC-KEY-001`) and Applet Spec (→ `CFL-SPEC-APP-001`, fix tier names); regenerate the agent-readability artifacts (`llms.txt` etc.) against ratified canon. **Promotion of KEY-001/APP-001 is now unblocked.**

---

## Propagation status (as of 2026-06-27)

| Surface | Status | What it entails / where the contradictions live |
|---|---|---|
| Repo `cuttlefishclaws-main` | **Done** | P2 session applied D-1/D-2/D-3/D-6 — full per-file detail in `D:\CuttlefishLabs_Dev\repo_review\REVIEW_REPORT.md` §L. Not deployed (gated by README "ROTATE BEFORE DEPLOY"). |
| `CAC_PROTOCOL_CANONICAL_SPEC_v5.md` | **Done** | This stack; supersedes stale v4. |
| `CAC_Canonical_Spec_v4.md` | Stale (kept in place) | Still Resident/Builder/Sovereign/Anchor + monthly + Revenue-share column + ~4–5% APY. Do not cite; use v5. |
| Website (`WEBSITE_REBUILD_SPEC.md` / cuttlefishlabs.io / cuttlefishclaws.com) | **Pending — D-4 now locked, work unblocked** | Same D-1/D-2/D-3 corrections as the repo (TRIB→$E2R, restore Builder Stewards, remove APY/savings, tiers→Developer/Studio/Enterprise/Anchor). **D-4 is ratified: the site IA must lead with the validation→reward engine, not "buy CAC + buy REIT."** First website task: produce a §L-equivalent punch-list against `WEBSITE_REBUILD_SPEC.md`. |
| Counsel / E2R Form 1-A | Unaffected | $E2R already canonical in the E2R stack; naming change does not touch securities filings. |

---

*All seven decisions (D-1 through D-7) are ratified as of 2026-06-27. Propagation now pending: website rebuild (D-4), the AIL-001 clarification note (D-5), and promotion of KEY-001/APP-001 (D-7).*
