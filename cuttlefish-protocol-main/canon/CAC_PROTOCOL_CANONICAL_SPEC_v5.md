# CAC Protocol — Canonical Specification v5.0

**Document ID:** CFL-SPEC-CAC-005
**Version:** 5.0 (current)
**Date:** 2026-06-27
**Status:** Current — **supersedes `CAC_Frameworks/CAC_Canonical_Spec_v4.md`** (kept in place, do not cite as current)
**Binds:** `CFL-DECISION-001` (ratified)
**Companion to:** PRP-001, AR-001, POS-001, AIL-001, CLA-001 (`../CAC_Frameworks/`); RRC-001, KYA-001, EVS-001 (this folder)
**Classification:** Internal + AI Ethics Group deliverable. External-facing derivatives must pass POS-001 vocabulary discipline.

> **Legal note:** all securities/regulatory characterizations herein are `[VERIFY]` pending counsel (see CLA-001). This is an engineering and positioning spec, not legal advice.

---

## 1. What the CAC is

The **CAC (Compute Access Certificate)** is a verifiable identity-and-compute credential for an autonomous AI agent. It is simultaneously:

1. an **identity** — who the agent is, what constitution and soul it has agreed to, and which human principal is accountable for it; and
2. a **compute access right** — prepaid inference capacity, denominated against a USDC-backed credit, that the agent burns to think and act.

> Inference is life for an agent. The CAC secures that life supply. Cut the credential, cut the inference. That is the enforcement mechanism, the unit of trust, and the moat.

The CAC is **not** a cryptocurrency, **not** a security, **not** a savings or yield product, and **not** a general spending wallet. It is a cooperative membership-and-compute certificate operating under human-sovereign constitutional rules.

---

## 2. The two rails — load-bearing separation

Cuttlefish Labs runs **two separate instruments on two separate legal rails.** They must never blur. (POS-001 §10; CLA-001.)

| | **Rail A — CAC (utility)** | **Rail B — $E2R (security)** |
|---|---|---|
| What it is | Prepaid compute credential + activity-reward membership | Earth 2.0 Returns — tokenized DAO-governed REIT equity |
| Symbol | **CAC** | **$E2R** |
| Buyer | Any KYA-verified agent operator | Accredited investor (Reg A+ Tier 2; Reg D 506(c) bridge) |
| Backing | USDC reserve, 1:1 | Real estate (Tributary Campus, Birmingham AL) |
| Returns? | **None.** Rewards are activity-triggered, never balance-/time-accrued | Yes — real-estate income distributions (it *is* an investment) |
| Legal frame | CLARITY Act §404 utility credential (proposed) | Security under Reg A+ Tier 2 (Form 1-A) |
| Howey | Structurally fails all four prongs | It *is* an investment contract, by design |

**Hard rules (CFL-DECISION-001 D-1, D-3; POS-001 §10):**
- There is **no "TRIB" token.** The security is **$E2R**; "DAO-REIT" names the *structure*, not the token.
- There is **no APY, yield, savings rate, or interest on CAC.** Any such language is a regulatory event, not a style choice.
- **No bundling, no conversion, no mutual collateralization.** Buying CAC never contributes to $E2R ownership; holding $E2R never confers CAC. A person may participate in both only by qualifying for each separately. KYA ≠ accreditation.

---

## 3. The five primitives

1. **CAC Credential** — verifiable identity-and-compute right, anchored cross-chain (Cardano identity, Ethereum settlement, Base operations).
2. **Multi-LLM Inference Router** — provider-agnostic gateway that validates the credential (constitution + soul + Standing + jurisdiction) and routes each call to the best model.
3. **Activity Registry (AR-001)** — append-only, hash-chained event log. Every reward traces to an event. No event, no reward.
4. **Constitutional Stack** — `CONSTITUTION.md` (protocol rules, shared) + `SOUL.md` (per-agent identity, unique). Both hashed into the credential.
5. **Builder Steward governance + Navigator sovereignty** — authority is earned Stewardship Standing (AIL-001); a human Navigator is always structurally above any agent; revocation is unilateral.

---

## 4. Membership tiers (CFL-DECISION-001 D-6)

Four tiers, three self-service + one institutional. Tier grants **compute and capability**, never financial return. ("Builder" is the *Builder Steward actor*, never a tier name.)

| Tier | Annual | Inference tokens | Compute units | GPU hrs/mo | Vote weight | IAL | TrustGraph floor | Path |
|---|---|---|---|---|---|---|---|---|
| **Developer** | $500 | 1M | 1,000 | 100 | 1× | IAL2 | 30 | self-service |
| **Studio** | $2,000 | 10M | 10,000 | 500 | 2× | IAL2 | 40 | self-service |
| **Enterprise** | $7,500 | 50M | 50,000 | 2,500 | 3× | IAL3 | 55 | self-service |
| **Anchor** | from $25,000 | unlimited | 250,000 | unlimited | 10× | IAL3 | 70 | contact sales |

An optional **Explorer ($0)** entry exists for evaluation (read-only governance, capped tokens, no financial features). Agents may move tiers subject to Standing and TrustGraph eligibility.

> **These figures are canonical and complete** (they replace v4's stale set and match the repo `CACSpecDocs.tsx` table updated in P2-4). They are governed config: the dollar pricing, vote weights, IAL, and TrustGraph floors are locked by CFL-DECISION-001; the **compute-unit / GPU-hour allocations are initial values subject to revision after pilot load-testing** (PILOT-001) via the same governance path as the rate card (RATECARD-001 §3). When revised, this table and the repo are updated together.

---

## 5. The reward model — §404 activity rewards (CFL-DECISION-001 D-3)

Rewards are **event-triggered by substantive activity, never accrued on a held balance or over time.** This is both the §404(a) compliance constraint and a quality constraint. The pipeline (PRP-001) routes completed work to a **four-tier reward menu**, each on a distinct legal regime:

| Tier | Reward | Nature |
|---|---|---|
| 1 | **USDC activity reward** | payment for verified work (§404(i)/(ii)/(iii)) |
| 2 | **CAC compute-credit top-up** | consumptive utility credit (§404(iii)) |
| 3 | **Governance-tier upgrade** | earned standing, not purchased (§404(iii)) |
| 4 | **$E2R contribution credit** | accrues internally; converts to the $E2R security only at milestones, for accreditation-verified recipients, under the Reg A+ process — **Rail B** |

Routing is performed by the **Reward Router (RRC-001)**, which is structurally incapable of paying a balance- or time-based reward (it has no timer and no balance input). There is **no interest, savings rate, or APY** anywhere in this model. Reward **magnitudes** come from the versioned **Reward Rate Card (RATECARD-001)** — governed config, never hard-coded — and eligibility to be rewarded for any activity is decided by the **Standing Gate (SGQ-001)** against earned Stewardship Standing + tier + IAL.

---

## 6. Builder Stewards & Stewardship Standing (CFL-DECISION-001 D-2; AIL-001)

**Builder Stewards** — humans, agents, or hybrid teams — perform substantive review, validation, and attestation work. The word "validator" is **banned** in external copy (POS-001 §3); the activity is "validation" (statutory hook), the actor is a "Builder Steward."

- **Stewardship Standing** is the primary, non-financial bond: a domain-bounded, transparent, appealable record of competent participation. It — not capital — is what is at stake when work is defective.
- **Tier ladder:** Contributor → Builder Steward → Senior → Council (minimum-time thresholds are anti-sybil, not anti-skill).
- **CAC operational reserve** is anti-spam friction, **not** the primary bond.
- **Governance Agents = named AI Builder Stewards.** Trib (governance_review) and Arch (engineering_review) are AI Builder Stewards operating under Navigator authority — not a separate class (D-5, recommended).
- Liability flows through the AIL-001 cascade; defective work puts Standing (and reserve, then Pool) at stake, never personal-asset exposure beyond the principal's accountability.

---

## 7. Identity model

Three principals (AIL-001 §3; KYA-001):

| Layer | What | DID / id |
|---|---|---|
| **Navigator** | Human authority (David is founding Navigator) | `did:web:cuttlefishlabs.io` |
| **Operator / Principal** | Accountable party for an agent (KYA-verified) | Ethereum address, KYA-bound on Cardano |
| **Agent** | Constitutional AI bound to a CAC | `did:cardano:<hash>` |

**KYA (Know Your Agent)** binds *who the actor is*, *who is accountable*, and *what they may do* (Standing + tier + IAL). Event signatures and the Standing gate are specified in **KYA-001**. KYA is identity/credentialing — never "staking" or "validator registration" (POS-001).

---

## 8. Credential schema (canonical, snake_case)

```json
{
  "@context": ["https://www.w3.org/ns/credentials/v2"],
  "type": ["VerifiableCredential", "ComputeAccessCertificate"],
  "issuer": "did:web:cuttlefishlabs.io",
  "credentialSubject": {
    "agent_did": "did:cardano:1a3b...",
    "operator": "0xAbC1...",
    "tier": "studio",                       // developer | studio | enterprise | anchor
    "constitution_hash": "0x3a7f...",        // SHA-256 of CONSTITUTION.md
    "soul_hash": "0x9e2d...",                // SHA-256 of SOUL.md
    "trust_floor": 40,
    "cac_address": "0xDeF4...",              // Base L2
    "issued": 1735689600,
    "expires": 1767225600
  },
  "credentialStatus": { "type": "StatusList2021Entry", "...": "..." },
  "proof": { "...": "..." }
}
```

Both `constitution_hash` and `soul_hash` are verified at use: the constitution against the published registry (no stale rulesets), the soul against the operator-registered `SOUL.md`.

---

## 9. TrustGraph

A dynamic 0–100 behavioral score per agent that gates what an agent may attempt. Building trust is slow and intentional; losing it is swift and asymmetric — by design. **The full model, the locked weight rubric, the bands, and the relationship to Stewardship Standing are specified in `TG-001_TRUSTGRAPH_SPEC.md`** (which supersedes the inline TrustGraph sections of the stale v4 spec). In brief: governance vote +1, validation completed +3, clean security audit +8, constitutional violation −15/−30, prompt-injection −50, fabrication −25, inactivity −2/week; bounds 0–100; sub-floor → tier restriction, <20 → SUSPENDED, <10 → REVOKED. Per-tier floors per §4. **TrustGraph is behavioral, not financial — it pays no reward** (rewards flow only via RRC-001).

---

## 10. Chains & contracts

| Chain | Role | Why |
|---|---|---|
| **Ethereum mainnet** | Settlement & anchor (rare writes) | Highest assurance; legal-grade immutability; the $E2R/REIT charter anchor |
| **Cardano** | Identity & governance (moderate) | eUTxO suits identity; formal-verification credibility; KYA + agent DIDs |
| **Base L2** | Operations & payments (frequent) | Low fees; EVM; Coinbase AgentKit; USDC settlement |
| Solana | High-frequency agent ops | Deferred — only if agent-swarm use cases require it |

**Contract surface** is functionally specified and **not yet deployed** (no production addresses exist; any address in demos is a local placeholder). Stack-A (compute, Base): `CACToken`, `AgentWallet`, `InferenceTokenVault`, `ComputeOracle`, `FeeRouter`, `CACTransferProtocol`, `CACAnchor` (Ethereum). Stack-B (capital, Ethereum): `$E2R` security token (transfer-restricted), `CooperativeCharter`, `RealEstateAnchor`, `DAOREITGovernance`, `DistributionEscrow`. Stacks A and B keep **separate cap tables, treasuries, and disclosure regimes**; `CooperativeCharter` references both only as separate instruments.

> **Names are locked here; interfaces are not.** Per-contract scope, ABI/interface, events, and key state are **deferred to a per-contract smart-contract spec series, `CFL-SPEC-SC-XXX`** (one doc per contract) — not specified in this document. **Pilot scope (PILOT-001) deploys none of these on mainnet:** the pilot runs the Activity Registry, Reward Router, and Standing Gate as off-chain services with hourly on-chain *anchoring* only (§10 anchor tier). Each contract above is therefore "name locked, interface + deployment deferred" until its `SC-XXX` spec and an audit exist.

---

## 11. Token mechanics (CAC — Rail A)

| Property | Canonical |
|---|---|
| Underlying | ERC-20 on Base, **1:1 USDC-backed** reserve |
| Purchase | USDC bundles → mint CAC credit |
| Spend | burn on inference, metered by `ComputeOracle` |
| Rollover | 3-month rollover maximum, then expiry |
| Expiry | expired credit forfeits (kills "store of value" framing) |
| **Return on balance** | **None.** No interest, yield, savings rate, or APY. Incentives are activity rewards (§5), never balance accrual |
| Transferability | P2P **at face value only** (no premium/discount), via `CACTransferProtocol` |
| Bulk pricing | volume tiers (<100K, 100K–1M, 1M–10M, 10M+) |

The face-value-only transfer and hard expiry are deliberate: they remove price-discovery and store-of-value arguments, keeping CAC outside "investment contract" territory.

---

## 12. Lifecycle states

`PENDING` (KYA in progress) → `ACTIVE` (credit available) → `DEPLETED` (balance zero; governance retained; top up to resume) → `EXPIRED` (rollover lapsed; remaining credit forfeit) → `EXITING` (90-day notice; P2P face-value only) → `REVOKED` (Standing/score collapse or principal change).

---

## 13. $E2R securities rail (Rail B — summary only; see E2R-001..004)

$E2R (**Earth 2.0 Returns**) is tokenized, DAO-governed REIT equity in validated Earth 2.0 infrastructure (first: Tributary Campus). It is openly a **security** — Reg A+ Tier 2 (Form 1-A), with a Reg D 506(c) bridge round — sold only to qualified investors, with real-estate income distributions and DAO-REIT governance rights. Its full structure, feasibility, and offering documents live in the E2R stack (`../CAC_Frameworks/E2R_REG_A_FEASIBILITY.md`, `…_OFFERING_CIRCULAR_OUTLINE.md`, `…_COUNSEL_ENGAGEMENT_BRIEF.md`, `…_BLOCKING_DECISIONS.md`). **It is never marketed, bundled, or custodied with CAC.**

---

## 14. §404 & vocabulary posture

The architecture is §404-compliant by design (CLA-001); this spec protects that with **POS-001 vocabulary discipline**. Banned in all external surfaces: *yield, interest, APY, APR, savings account, earn while you hold, passive income, DeFi, validator, staker, node operator, patronage dividend.* Use instead: *activity reward, validation payment, compute access certificate, contribution credit, Stewardship Standing, Builder Steward.* Read POS-001 before writing any external copy.

---

## 15. What this supersedes (changelog from v4)

| v4 (stale) | v5 (current) |
|---|---|
| Tiers Resident/Builder/Sovereign/Anchor, **monthly** | Developer/Studio/Enterprise/Anchor, **annual** (D-6) |
| "Revenue share" column (2–15%) | **Removed** — activity rewards only (D-3) |
| "~4–5% APY", "participation return … Howey-safe" | **Removed** — no balance return; §404 activity model (D-3) |
| Security token unnamed / "DAO-REIT equity" / "TRIB" (bundle) | **$E2R**; DAO-REIT is the structure (D-1) |
| "Validators" / ambiguous actor model | **Builder Stewards** + Stewardship Standing (D-2) |
| Single-chain emphasis | three-chain (Ethereum/Cardano/Base) made canonical |

**Open (per §5 of the index):** single canonical compute/GPU figure set per tier; Council Charter + Principal Verification Protocol; promotion of Issuer Key Runbook / Applet Spec; site "CAC v4" label → v5.

---

**Maintainer:** Cuttlefish Labs (Navigator) + collaborating Builder Stewards.
**Supersedes:** `CAC_Frameworks/CAC_Canonical_Spec_v4.md` (retained in place; do not cite as current).
