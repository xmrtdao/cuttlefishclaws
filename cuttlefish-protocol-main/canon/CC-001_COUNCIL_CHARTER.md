# Council Charter Specification v1.0

**Cuttlefish Labs — CAC Protocol**
**Anti-Faction Governance for Council Stewards**

---

**Document ID:** CFL-SPEC-CC-001
**Version:** 1.0 (draft)
**Date:** 2026-06-27
**Status:** Architectural spec, pre-implementation
**Companion to:** CFL-SPEC-AIL-001 (§11 governance roles; §559 anti-faction; §626 Council election), CFL-SPEC-SRP-001 (Stewardship Review)
**Classification:** Internal + AI Ethics Group deliverable
**Conforms to:** CFL-DECISION-001 (Builder Stewards retained; §404 activity model; POS-001 vocabulary)

---

## 1. Purpose

AIL-001 defines a Stewardship ladder — **Contributor → Builder Steward → Senior → Council** — but defers the Council's composition, election, and anti-faction rules to "a separate Council Charter spec" (AIL-001 §559, §626, §674). This document is that spec.

The Council is the apex of earned Stewardship authority. Because apex bodies are where capture happens, this Charter's first job is **anti-faction design**: ensuring no individual, principal, organization, or coalition can control the Council and use it to disadvantage others. Council authority is **earned Stewardship Standing exercised under structural constraints** — never capital, never tenure alone, never a closed clique.

> The Council does not own the protocol. The Navigator holds ultimate human sovereignty (AIL-001; FounderShare veto). The Council is a constrained body of the most-proven Builder Stewards, doing the work that requires the highest Standing — and structurally prevented from becoming a faction.

---

## 2. What the Council is and does

Council Stewards are Builder Stewards who have reached the top of the ladder in at least one domain and been seated under §3. The Council's authority is bounded to:

1. **High-tier attestation** — final-tier review and attestation weighting on the most consequential validation work (per AR-001 / SRP-001).
2. **Stewardship Review panels** — convening and staffing review panels for serious defect/misconduct cases (SRP-001), under the random-composition rule (§4).
3. **Standing-rubric stewardship** — proposing and ratifying changes to domain rubrics and Standing thresholds (subject to §5 limits and DAO/Navigator checks).
4. **Reward-parameter recommendations** — proposing Reward Router rate-card and tier-threshold changes (RRC-001 §11) for ratification.
5. **Domain creation/retirement** — chartering new validation domains and sunsetting obsolete ones.

The Council **does not**: issue or convert $E2R (Rail B; securities authority); set securities terms; override the Constitution; bypass the Navigator veto; or act in any single member's economic interest (§6).

---

## 3. Composition and selection (hybrid, anti-capture)

Per AIL-001 §626's recommended **hybrid** model (peer eligibility + random selection):

- **Eligibility pool.** For each domain, the eligible pool is all Stewards at **Senior** Standing or above in that domain, in good standing, with no active Stewardship Review against them.
- **Selection = random draw from the eligible pool**, not election. Random selection (verifiable, seeded by a public anchor hash from AR-001 §5.3) removes campaigning, patronage, and slate-building — the mechanics of faction. Peer eligibility ensures only the genuinely proven are in the draw.
- **Seats and diversity quotas.** The Council seats a fixed number per cohort (recommend 9–15), with **domain-diversity quotas** so no single domain holds a majority, and **principal-diversity caps** so no single principal/organization holds more than one seat (and no coalition of related principals exceeds a defined fraction).
- **Staggered terms.** Terms are fixed (recommend 12 months) and **staggered** (e.g., thirds rotate each cycle), so the Council never turns over — or entrenches — all at once.
- **Term limits.** No member serves more than two consecutive terms; a cooling-off period applies before re-eligibility. Standing is retained; only the *seat* rotates.

---

## 4. Anti-faction provisions (the core)

These are non-negotiable structural constraints (AIL-001 §559):

1. **Random panel composition.** Every Stewardship Review panel and high-tier attestation panel is composed by **random draw** from eligible Council/Senior Stewards, excluding any with a conflict (§6). No member chooses their panel; no member is permanently paired.
2. **Staggered terms + term limits** (§3) — prevent entrenchment.
3. **Domain and principal diversity caps** (§3) — prevent single-domain or single-principal control.
4. **Mandatory recusal.** A member must recuse from any matter touching their own principal, organization, domain rival, or any party with whom they have a disclosed relationship. Recusal is logged as an AR-001 event.
5. **No self-dealing.** A Council member may not vote on, sponsor, or attest to any matter that adjusts their own Standing, reward eligibility, or that of their principal.
6. **Supermajority + timelock for sensitive actions.** Rubric/threshold changes, domain charters, and removals require a supermajority (recommend ≥ 2/3 of seated, non-recused members) and a mandatory timelock (recommend 14–30 days) before effect, during which the Navigator veto window is open.
7. **Transparency by default.** Council decisions, rationales, vote tallies (by seat, not secret ballot for governance acts), and recusals are written to AR-001 and publicly auditable. Stewardship Review deliberations follow SRP-001 confidentiality, but outcomes and reasoning are recorded.
8. **No proxy capture.** Votes are cast by seated members personally (or their bound agent under KYA-001); no transferable proxies, no vote delegation that could aggregate into a bloc.

---

## 5. Powers, limits, and the sovereignty checks

| Council may | Council may not |
|---|---|
| Weight high-tier attestations | Override the Constitution or a published `constitution_hash` |
| Convene/staff random review panels | Choose its own panels (random only) |
| Propose rubric/threshold/reward-parameter changes | Enact them without supermajority + timelock + (no) Navigator veto |
| Charter/retire validation domains | Issue, price, or convert $E2R (Rail B) |
| Recommend Standing restorations | Self-deal or adjust its own members' Standing |

Two checks sit above the Council:
- **Navigator veto** — the FounderShare 6-trigger constitutional veto (AIL-001 §11.3) can halt any Council action within the timelock window.
- **DAO governance ($E2R holders)** — votes on *protocol economic parameters* that affect the cooperative; this is a **separate axis** from Council Steward governance (which concerns validation quality and Standing). The two do not merge: $E2R holders do not gain Stewardship authority by holding equity, and Council Stewards do not gain securities authority by holding Standing (CFL-DECISION-001 rail separation).

---

## 6. Conflicts, removal, and vacancies

- **Conflict disclosure** is continuous; undisclosed conflicts are themselves a Stewardship Review matter (SRP-001).
- **Removal** of a Council member (for misconduct, capture behavior, or sustained low-quality attestation) requires a supermajority of the *remaining* members plus Navigator confirmation, or a Stewardship Review finding. Removal reverts the seat to a fresh random draw.
- **Vacancies** are filled by random draw from the current eligible pool for the remainder of the term (staggering preserved).

---

## 7. Vocabulary & §404 posture

Council Stewards are **Builder Stewards**, never "validators," "stakers," "node operators," or "governors-for-hire" (POS-001 §3). Council service is earned ecosystem participation, not a staked or purchased office. No Council role carries interest, yield, or a balance-based reward; any compensation for Council work is an **activity reward** routed through the Activity Registry (RRC-001), recorded per event.

---

## 8. Failure modes

| Failure | Mitigation |
|---|---|
| Coalition tries to pack the Council | Random selection + principal-diversity caps + term limits |
| A captured panel buries a defect | Random panel composition + transparency + appeal to Navigator/DAO |
| Member self-deals on Standing/rewards | Recusal + no-self-dealing rule + audit trail |
| Council drifts from canon | Supermajority + timelock + Navigator veto window |
| Random seed manipulation | Seed from public AR-001 anchor hash (Ethereum L2/Solana), verifiable |
| Council overreaches into securities (Rail B) | Hard powers boundary (§5); $E2R actions route to securities authority only |

---

## 9. Phased implementation

| Phase | Scope |
|---|---|
| **Phase 1 (pilot)** | No formal Council; Navigator + a small advisory group of the highest-Standing pilot Stewards perform Council functions manually, recording decisions to AR-001 under these anti-faction principles. |
| **Phase 2** | Seat a first Council by random draw from the Senior+ pool; staggered terms begin; recusal + transparency + timelock enforced; Navigator veto live. |
| **Phase 3** | Full domain-diversity/principal-diversity caps; automated random panel composition from AR-001 anchors; supermajority tooling; DAO-axis integration kept strictly separate. |

---

## 10. Open questions

1. **Seat count and quotas** — 9 vs 12 vs 15; exact domain-majority and principal-coalition thresholds.
2. **Random-draw weighting** — pure uniform among eligible, or lightly Standing-weighted? Recommend uniform among the *qualified* pool to maximize anti-faction strength.
3. **Cross-domain Council members** — a Steward at Senior in multiple domains: one seat or eligibility in each draw? Recommend one seat, principal-cap binding.
4. **Emergency Council action** — is there an expedited path for time-critical safety matters that compresses the timelock, and what guardrails apply? (Coordinate with SRP-001.)
5. **Relationship to DAO supermajority** — where a parameter is both a Standing-rubric matter (Council) and an economic matter ($E2R DAO), who has precedence? Recommend dual-ratification with Navigator tiebreak.

---

## 11. Next concrete implementation steps

1. Fix the Phase-1 advisory-group composition and record its decisions to AR-001 under §4 principles.
2. Implement verifiable random selection seeded from AR-001 anchor hashes.
3. Encode recusal, diversity caps, and term-staggering as registry-enforced rules.
4. Wire the supermajority + timelock + Navigator-veto window into Council decision execution.
5. Specify the Council ↔ DAO ($E2R) interface so the two governance axes stay separate.

---

**Maintainer:** Cuttlefish Labs (Navigator) + collaborating Builder Stewards

**Companion documents:**
- `AGENT_IDENTITY_AND_LIABILITY_FRAMEWORK.md` (AIL-001 §11) — parent (governance roles)
- `STEWARDSHIP_REVIEW_PROCEDURE.md` (SRP-001) — review panels the Council staffs
- `RRC-001_REWARD_ROUTER_CONTRACT.md` — activity rewards for Council work
- `KYA-001_KYA_SIGNATURE_SPEC.md` — Council members vote/attest under KYA identity
- `CAC_SECTION_404_POSITIONING.md` (POS-001) — vocabulary discipline
