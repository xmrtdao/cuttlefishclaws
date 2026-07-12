# CAC Two-Stack Architecture v1.0
## Compute Stack vs Capital Stack — Clean Separation

**Status:** Canonical
**Date:** 2026-06-26
**Companion to:** Canonical Reconciliation v1.0, Product Thesis v1.0
**Purpose:** Resolve the operational, legal, and architectural confusion between the CAC token (utility, for inference) and the DAO-REIT equity (security, for real estate ownership). These must never mix.

---

## 0. Why this distinction is load-bearing

Cuttlefish Labs is running **two separate financial instruments**:

1. **CAC Tokens** — prepaid compute credit. Utility. Stablecoin-style.
2. **DAO-REIT Equity** — tokenized ownership of physical campus real estate. Security. Investment.

If these blur together — in copy, contracts, KYA flow, or user-experience — every benefit of the careful legal positioning collapses. A regulator looking at a single bucket that holds both a utility credential and an equity instrument will treat the whole thing as a security. Counsel will quote this section back at you.

**The two-stack architecture exists to make sure nothing about the compute stack looks like an investment, and nothing about the capital stack pretends to be a utility.**

---

## 1. Side-by-side

| | **STACK A — COMPUTE** | **STACK B — CAPITAL** |
|---|---|---|
| **What it is** | Prepaid compute access credential | Tokenized real estate equity |
| **Token symbol** | **CAC** | **TRIB** (proposed — see §6) |
| **Token type** | ERC-20 utility, 1:1 USDC-backed | ERC-20 security token (Reg D 506(c) restricted) |
| **Primary chain** | Base L2 | Ethereum mainnet (settlement) + Base L2 (governance ops) |
| **What it represents** | Compute consumption rights | Pro-rata ownership of Tributary Campus property |
| **Buyer** | AI agent operator (any KYA-verified) | Accredited investor only |
| **Verification required** | KYA, IAL2 or IAL3 by tier | Accredited investor verification (Reg D) |
| **Min purchase** | One bundle (~$25 implied minimum tier) | $25,000 |
| **Total issuance** | Mint-on-demand vs USDC | Fixed at $550K equity tranche (current), expandable per future campus |
| **Yield mechanism** | **4.5% APY on USDC reserve, passed as savings** | **6.4% APR from real estate income (varies)** |
| **Yield legal framing** | Float interest on prepaid balance (not investment return) | Income distribution from REIT operations (investment return) |
| **Transferability** | P2P at face value only (no premium / discount) | Restricted — securities law applies, Reg D resale restrictions, possibly Rule 144 holding period |
| **Expiry** | 3-month rollover then forfeit | None (equity has no expiry) |
| **Burnable** | Yes — burned on inference | No — equity is not burned, only transferred |
| **Refundable** | 25% refund on clean audit | No — equity has no refund mechanism |
| **Governance rights** | None (utility, not equity) | Yes — votes proportional to holdings on DAO-REIT decisions |
| **Tax treatment** | Likely prepaid asset (capital expense to operator) | Investment — pass-through REIT income (1099-DIV style) |
| **Smart contracts** | `CACToken.sol`, `AgentWallet.sol`, `InferenceTokenVault.sol`, `ComputeOracle.sol`, `FeeRouter.sol`, `CACTransferProtocol.sol` | `TRIBToken.sol` (proposed), `CooperativeCharter.sol`, `RealEstateAnchor.sol` (proposed), `DAOTreasury.sol`, REIT governance contracts |
| **Legal framing** | Utility credential under CLARITY Act §401 (proposed) | Security under Reg D 506(c) (existing law) |
| **Howey applies?** | Structurally fails all four prongs | Yes — it IS an investment contract, by design |
| **Marketing channel** | Developer outreach, partner integrations, agent platforms | LP outreach, accredited investor networks, real estate channels |
| **Footer language** | "not a security, equity interest, or investment contract" | "for accredited investors only — Reg D 506(c) offering" |
| **Customer success motion** | Self-service signup, technical onboarding, MCP integration | High-touch, KYC + accreditation, subscription docs, ongoing reporting |

---

## 2. STACK A — Compute Stack (CAC Token)

### 2.1 What it does

Operators buy CAC tokens to pay for inference performed by their agents through the multi-LLM router. Tokens burn per inference call based on actual compute consumed (reported by `ComputeOracle.sol`). Identity binding via the CAC credential ties tokens to a verified operator and a constitutional agent.

### 2.2 Legal positioning (recap)

Designed to structurally fail every prong of Howey:
- **Investment of money:** Yes (USDC deposit) — necessary
- **Common enterprise:** No (each operator's balance is segregated; no horizontal commonality)
- **Expectation of profit:** No (face-value-only transfer; hard expiry kills appreciation)
- **From efforts of others:** No (4.5% APY is passive USDC float interest, not active management)

The 4.5% APY is the most legally sensitive feature. It must always be framed as **"savings rate on prepaid balance,"** never as "yield" or "return."

### 2.3 Operator UX

An operator buys CAC the same way they'd buy AWS credits or a Twilio prepaid bundle. They never see the words "investment," "equity," "stake," or "return." The 4.5% APY appears as a savings rate on their balance, like a high-yield checking account.

### 2.4 Customer audience

| Audience | Why they buy CAC |
|---|---|
| AI agent developers | To pay for inference for their agents |
| AI startups | Bulk compute access with policy controls |
| Enterprise integrators | Constitutional binding for compliance |
| Other agent platforms | API integration via MCP |

---

## 3. STACK B — Capital Stack (DAO-REIT Equity)

### 3.1 What it does

DAO-REIT equity represents pro-rata ownership of the Tributary AI Campus (and future campuses). Holders receive real estate income distributions and vote on DAO-REIT governance decisions. The current offering is the **$550K equity tranche** of the $31M total capitalization of the Birmingham, AL property.

### 3.2 Legal positioning

This is a **Regulation D 506(c) offering**. Accredited investors only. Verification required. Subject to all standard securities law — anti-fraud, anti-manipulation, Rule 144 resale restrictions, state blue-sky compliance.

This is **not** trying to be a utility token. It is openly a security. The legal work is in being a properly-compliant security offering, not in avoiding security classification.

### 3.3 Investor UX

An investor goes through full KYC + accreditation verification, signs a subscription agreement, transfers funds, receives TRIB tokens representing their pro-rata share. They receive quarterly real estate income distributions, vote on DAO-REIT decisions, and can transfer their TRIB tokens only within the restrictions of Reg D 506(c) resale rules.

### 3.4 Investor audience

| Audience | Why they buy TRIB |
|---|---|
| Crypto-native LPs | Tokenized real estate with operational alpha |
| Real estate funds | Birmingham opportunity zone exposure with DAO governance |
| Family offices | Diversification + thematic AI infrastructure exposure |
| Strategic partners | Skin in the game alongside operational partnership |

---

## 4. Where the two stacks connect

There is exactly **one** legitimate connection point between the two stacks:

### 4.1 Governance bridge

**TRIB equity holders vote on DAO-REIT decisions, including decisions that affect how Cuttlefish Labs operates the campus, which in turn affects CAC operations.**

Example: TRIB holders could vote to (a) authorize a Phase 2 expansion that increases campus compute capacity, (b) approve a Cuttlefish operating budget that affects CAC fee splits, (c) ratify a major customer partnership.

But: TRIB holders do **not** receive CAC. CAC operators do **not** receive TRIB. The two ownership groups are populated through different processes with different verification, and a single individual can be in both groups only by participating in each separately.

### 4.2 Cross-references in contracts

`CooperativeCharter.sol` is the Ethereum anchor that defines the cooperative bylaws — and it references both stacks. But it references them as **separate instruments** with separate cap tables, separate token contracts, and separate disclosure regimes.

### 4.3 Cross-references in disclosure

In any document that mentions both:
- The CAC paragraph must say "utility credential, not a security"
- The TRIB paragraph must say "security, for accredited investors only"
- They must be visually separated (different sections, different headers)
- They must not appear in the same sentence except to disambiguate

---

## 5. Where the two stacks MUST NOT mix

### 5.1 No bundled offerings

You cannot sell a "Founder Bundle" that includes both X CAC tokens and Y TRIB equity. That packaging would be a security in its entirety. If a founding member wants both, they buy them separately.

### 5.2 No mutual collateralization

CAC token reserves cannot be backed by TRIB equity. TRIB equity cannot be backed by CAC token treasury. The reserves are separate.

### 5.3 No automatic conversion

CAC does not convert to TRIB under any condition. TRIB does not convert to CAC. There is no "earn equity through compute usage" mechanic.

### 5.4 No marketing crosslinks that imply convertibility

Marketing copy must never imply that CAC purchase contributes to TRIB ownership, or that TRIB holders get free CAC, or that the two are functionally interchangeable. A site visitor must come away with two distinct mental models.

### 5.5 No KYA shortcuts

A KYA verification for CAC purchase does NOT count as accreditation verification for TRIB purchase. They are different processes — accreditation requires income / asset verification beyond identity. Conversely, accreditation for TRIB doesn't shortcut KYA — KYA is about identity binding and constitutional agreement, accreditation is about financial qualification.

### 5.6 No commingled custody

The USDC reserve backing CAC sits in a segregated account. The real estate equity backing TRIB sits in the property-owning LLC. Neither account can be debited to satisfy obligations of the other. This is a basic principle of segregated-asset structures and must be enforced contractually at the smart contract level *and* at the legal entity level.

---

## 6. Naming convention

| Use case | Term |
|---|---|
| The protocol | **CAC Protocol** |
| The credential | **CAC Card** or **CAC Credential** |
| The compute utility token | **CAC** (no further qualifier needed) |
| The real estate equity token | **TRIB** *(proposed — verify trademark availability)* |
| The first campus | **Tributary AI Campus** (or successor name per Brand-A decision) |
| The legal entity holding the campus | **Tributary Campus LLC** (or similar single-property LLC) |
| The DAO governing the campus | **Tributary DAO** |
| The umbrella company | **Cuttlefish Labs** |

**Decision needed:** Confirm TRIB as the equity token symbol. Alternatives: REIT-T, CFL-RE, BMHM (Birmingham). TRIB ties cleanly to the property name but creates ambiguity if "Tributary" is renamed (Brand-A pending).

---

## 7. Site implications

The current `cuttlefishclaws.com` site **mixes both stacks in the same scroll** and this is the highest-risk thing I observed in the site review. Specific fixes:

### 7.1 Visual separation

The capital stack section (image 14 of the prior review) and the prepaid tokens section (image 4) need to be visually and structurally separated. Two ideas:

**Option A — single site, two clearly labeled sections:**
- Section header: "FOR DEVELOPERS — CAC Compute Stack"
- Section header: "FOR ACCREDITED INVESTORS — Tributary DAO-REIT"
- A visible horizontal separator between them
- Different background treatments (e.g., compute stack on dark navy, capital stack on slightly different shade)

**Option B — split by URL path:**
- `cuttlefishlabs.io/cac` — compute stack only
- `cuttlefishlabs.io/tributary/invest` — capital stack only
- Top-level chooser page that funnels the visitor to one or the other

Option B is legally safer because it physically separates the audiences. Option A is friendlier but requires more careful copy.

### 7.2 Disclaimer language

Current footer combines both disclaimers in the same paragraph. **Split them.**

**Proposed footer block for compute stack pages:**
> CAC is a prepaid compute credential — not a security, equity interest, or investment contract. The 4.5% APY on prepaid balance is a savings rate on USDC reserves, not an investment return. Tokens expire on a rolling 3-month basis.

**Proposed footer block for capital stack pages:**
> The DAO-REIT equity offering is a security available only to accredited investors as defined under SEC Rule 501. Available pursuant to Regulation D 506(c). Past performance does not guarantee future results. The 6.4% APR is an estimate of pro-rata real estate income distributions and may vary. Subject to standard investment risks including loss of principal. Resale restrictions apply.

### 7.3 The "OPP-ZONE-B" badge in the hero

The badge showing "REIT / TVL $40.4M / APR 6.4%" in the hero (image 2) is a security yield being displayed at the top of a page that also markets CAC. **This must move** — it belongs in the investor-only section, behind an accreditation gate.

### 7.4 The 4.5% APY visibility

Conversely, the 4.5% APY in the prepaid tokens panel is fine where it is, but the words "APY" and "yield" are dangerous. Consider relabeling to "**4.5% savings on prepaid balance**" — avoids the financial-instrument terminology while preserving the benefit.

---

## 8. Smart contract implications

The contract list in the Canonical Reconciliation §6.2 should be restructured to make the two-stack separation explicit. **Proposed update:**

**STACK A contracts (compute, Base L2):**
- `CACToken.sol` — ERC-20 utility token
- `AgentWallet.sol` — per-agent payment surface
- `InferenceTokenVault.sol` — burn-on-inference
- `ComputeOracle.sol` — compute consumption reporting
- `RevenueDistributor.sol` — 40/40/20 fee split (CAC fees only)
- `Treasury.sol` — CAC operations treasury (NOT the REIT treasury)
- `FeeRouter.sol` — routes 0.25% CAC protocol fee
- `CACTransferProtocol.sol` — face-value P2P
- `CACAnchor.sol` (Ethereum) — cross-chain credential anchor

**STACK B contracts (capital, Ethereum primary):**
- `TRIBToken.sol` — security token (Reg D 506(c) restricted, with transfer whitelist)
- `CooperativeCharter.sol` — bylaws (already exists, references both stacks)
- `RealEstateAnchor.sol` (proposed) — campus property registry
- `DAOREITGovernance.sol` (proposed) — voting / proposal contract
- `DAOTreasury.sol` (separate from CAC Treasury) — REIT operating treasury
- `DistributionEscrow.sol` (proposed) — quarterly distribution handler

**Shared / cross-stack contracts:**
- `IssuerKeyRegistry.sol` — Cuttlefish master keys (referenced by both)
- `KYAValidator` (Cardano) — KYA for CAC; **does not validate accreditation for TRIB** (that requires a separate process)

---

## 9. Open decisions

| ID | Decision | My recommendation |
|---|---|---|
| **Stack-A** | Confirm TRIB as REIT token symbol? | Yes (pending Brand-A resolution for Tributary name) |
| **Stack-B** | Split site to two URLs or single site with separation? | Option B (separate URLs) for legal cleanliness |
| **Stack-C** | Relabel 4.5% APY to "savings rate" in all copy? | Yes |
| **Stack-D** | Move 6.4% APR badge out of public hero? | Yes — accreditation gate |
| **Stack-E** | Build `TRIBToken.sol` and `DAOREITGovernance.sol` as Phase 2? | Yes — required for $550K tranche to be deployable |
| **Stack-F** | Engage securities counsel specifically for TRIB structure? | Yes — adds to the counsel list in Legislation Tracker §12 |

---

## 10. The one-sentence test

After any change to copy, contracts, or site IA, ask:

> Would a regulator looking at this think CAC and TRIB are the same instrument, or different instruments?

If the answer is "the same" or "I can't tell" — **stop and re-separate**. The two-stack architecture only works if the separation is unambiguous to a skeptical outsider.

---

*End of CAC Two-Stack Architecture v1.0*
*Companion to Canonical Reconciliation v1.0 and Product Thesis v1.0.*
