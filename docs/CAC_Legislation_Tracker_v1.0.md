# CAC Legislation Tracker v1.0
## Living index of laws & regulations gating CAC design decisions

**Status:** Canonical — REVIEW QUARTERLY
**Date:** 2026-06-26
**Next review:** 2026-09-26
**Owner:** Navigator (David Hans Elze)
**Counsel of record:** TBD — must be retained before Phase 2 launch

---

## 0. Purpose

CAC's token mechanics, identity model, and routing architecture are **deliberately engineered against current and proposed legislation**. As laws change, CAC's design must move with them. This document is the single index of:

1. Every law / rule / proposal that gates a CAC design decision
2. Which design decisions it gates
3. Current status (in force / proposed / draft / dormant)
4. What we do if it changes

This is **not legal advice**. It is an engineering reference for tracking external dependencies. Counsel review is required before relying on any positioning here.

---

## 1. Status legend

| Symbol | Meaning |
|---|---|
| ✅ | In force, CAC currently compliant |
| 🟡 | In force or proposed, CAC needs adjustment |
| 🟠 | Proposed / pending, CAC pre-positioned |
| 🔴 | Adverse — would require material redesign if enacted |
| ⚪ | Dormant / withdrawn / unclear |

---

## 2. U.S. Federal — Securities & Crypto

### CLARITY Act (H.R. 3633) — Digital Commodities Consumer Protection
**Status:** 🟠 Proposed (House passed, Senate pending as of mid-2026)
**Relevance:** Token classification — utility credential vs security
**Gates these CAC decisions:**
- CAC token as "prepaid compute credential" (not security)
- 4.5% APY on USDC float framed as savings rate (not return on investment)
- Face-value-only P2P transfer (kills price-discovery argument)
- 3-month hard expiry (kills store-of-value argument)
**Action if enacted:** Adopt §401 utility credential safe harbor language verbatim in footer + ToS.
**Action if rejected / amended:** Re-evaluate token mechanics; possibly add jurisdictional gating (US operators get different token model).
**Last reviewed:** 2026-06-26

### GENIUS Act — Stablecoin Regulation
**Status:** 🟠 Proposed
**Relevance:** USDC backing model
**Gates these CAC decisions:**
- 1:1 USDC reserve backing the CAC token
- Reserve attestation cadence (monthly? quarterly?)
- Auditor selection for reserve
- Permitted issuer status (do we need to be one, or is Circle's status sufficient because we hold USDC, not mint a stablecoin?)
**Action if enacted:** Confirm with counsel whether CAC token's USDC-backing is "wrapped stablecoin" requiring issuer registration, or "prepaid digital asset" outside the regulation. Two very different compliance regimes.
**Risk if enacted with strict reading:** 🔴 Could force CAC to register as a stablecoin issuer with associated capital and audit requirements.

### Howey Test (SEC enforcement precedent)
**Status:** ✅ In force (case law, not statute)
**Relevance:** Investment contract classification
**Gates these CAC decisions:**
- No expectation of profit from price appreciation (face-value transfer)
- No common enterprise (each operator buys their own bundle)
- No reliance on issuer's efforts for returns (4.5% APY is on the USDC float — passive savings, not active management)
- Hard expiry kills "speculative asset" framing
**Current positioning:** All four Howey prongs structurally not met. Footer disclaimer reinforces.
**Counsel review:** Required before mainnet launch.

### Bank Secrecy Act / FinCEN MSB Registration
**Status:** ✅ In force
**Relevance:** Money transmission
**Gates these CAC decisions:**
- Whether CAC's USDC-bundle-purchase flow requires MSB registration
- Whether P2P transfer at face value triggers transmission
- State-by-state money transmitter licensing (50 jurisdictions to evaluate)
**Action:** Counsel must opine before opening US operator signups beyond pilot. If MSB required, this is months of work and a measurable burn rate impact.
**Risk:** 🟡 — likely some form of registration required.

### FATF Travel Rule (FinCEN implementation)
**Status:** ✅ In force above $3,000
**Relevance:** Cross-border CAC P2P transfers
**Gates:** Any P2P transfer >$3,000 needs originator + beneficiary information attached.
**Action:** Build identity attestation into CACTransferProtocol.sol for transfers above threshold. May need to gate non-KYA'd transfers entirely.

---

## 3. U.S. Federal — AI

### Executive Order on Trustworthy AI (current admin)
**Status:** ✅ In force (terms evolving)
**Relevance:** Federal procurement, transparency obligations
**Gates these CAC decisions:**
- Agent provenance attestation (CAC inherently provides this)
- Model card / system card requirements (SOUL.md plays this role)
- Reporting on high-compute models
**Positioning:** CAC's constitutional binding + audit log is **closer to compliant than typical agent deployments**. This is a market-positioning advantage.

### NIST AI Risk Management Framework (RMF) 1.0
**Status:** ✅ In force (voluntary, but de facto standard)
**Relevance:** Federal contracting + insurance underwriting
**Gates:** TrustGraph design, audit log retention, constitutional definition
**Positioning:** Align CAC controls to NIST RMF "Govern / Map / Measure / Manage" so partners can claim compliance through CAC integration.

### Proposed federal AI accountability legislation
**Status:** 🟠 Multiple bills in committee
**Relevance:** Operator liability, agent registration
**Gates:** KYA requirements, operator-to-agent binding strength
**Action:** Track all major bills monthly. Pre-position by maintaining IAL3 path even though IAL2 is currently sufficient.

---

## 4. U.S. State — AI

### California SB 1047 (Frontier AI Safety)
**Status:** ⚪ Vetoed 2024, possible re-introduction 2026
**Relevance:** Foundation model accountability
**Gates:** Provider selection logic in the router — if re-enacted, certain models may have to be excluded from CA-jurisdictioned requests.
**Positioning:** Router's jurisdictional routing logic is exactly the mechanism that satisfies this if it returns.

### New York S2058 / similar
**Status:** 🟠 Proposed
**Relevance:** Automated decision system disclosure
**Gates:** Whether CAC must surface model attribution per inference call

### Texas, Colorado, Illinois, Tennessee AI laws
**Status:** 🟡 Various, some in force
**Relevance:** Sector-specific (employment, insurance, consumer)
**Gates:** Operator-level disclosure requirements
**Action:** Build a state-jurisdiction tag into CAC; let SOUL.md declare jurisdictional bindings.

---

## 5. European Union

### EU AI Act
**Status:** ✅ In force (phased, fully effective by August 2026)
**Relevance:** Risk classification, transparency, provenance
**Gates these CAC decisions:**
- Article 50 transparency obligations — CAC inherently provides agent identification
- General-purpose AI provider obligations (Articles 53-55)
- Prohibited practices (Article 5) — router must refuse certain class of requests
**Positioning:** CAC's constitutional binding is **more than sufficient** for Article 50 transparency. Position as "AI Act-native infrastructure."
**Action required:** Map every Article 50/53 requirement to a CAC enforcement point.

### GDPR
**Status:** ✅ In force
**Relevance:** Operator + agent data handling
**Gates:** Audit log retention limits, KYA data retention, right to erasure conflicts with on-chain immutability
**Tension:** 🟡 — On-chain anchoring of audit hashes vs GDPR right to erasure. Resolution: anchor hashes only, never PII; PII lives in Supabase under standard GDPR controls.

### DORA (Digital Operational Resilience Act)
**Status:** ✅ In force (Jan 2025)
**Relevance:** Financial sector ICT risk
**Gates:** If CAC integrates with EU financial institutions, DORA applies to the integration layer.
**Action:** Defer until first EU FI partner.

### MiCA (Markets in Crypto-Assets)
**Status:** ✅ In force (phased)
**Relevance:** Token classification in EU
**Gates:** Whether CAC token is e-money token, asset-referenced token, or utility token under MiCA
**Positioning:** Likely "utility token" under MiCA Title II — similar structural argument to Howey. Needs EU counsel review.

---

## 6. United Kingdom

### UK FCA Crypto Promotion Rules
**Status:** ✅ In force
**Relevance:** Marketing CAC to UK users
**Gates:** All UK-facing promotion must comply with FCA financial promotion rules; cooling-off periods etc.
**Action:** UK launch requires UK-specific compliance review.

### UK AI Regulation White Paper (sectoral approach)
**Status:** 🟠 Evolving framework
**Relevance:** Sectoral AI obligations
**Gates:** Variable — depends on what sector an operator's agent works in
**Action:** Defer monitoring until UK launch is on roadmap.

---

## 7. Other jurisdictions

### Singapore (MAS) — Crypto licensing
**Status:** ✅ In force, well-established
**Relevance:** Singapore is a likely partner / launch market
**Action:** Monitor; MAS is reasonable. Could be a good early jurisdiction for international expansion.

### UAE (VARA — Virtual Assets Regulatory Authority)
**Status:** ✅ In force
**Relevance:** Possible launch market
**Action:** Monitor.

### Switzerland (FINMA)
**Status:** ✅ In force
**Relevance:** Crypto-friendly, possible token issuance jurisdiction
**Action:** Evaluate if US registration becomes onerous.

### Small Island Developing States (SIDS) — relevant to IOSA framework
**Status:** Varies
**Relevance:** IOSA framework integration plan
**Action:** Defer; IOSA is Phase 4+.

---

## 8. Industry standards (not law, but de facto binding)

### W3C Verifiable Credentials 2.0
**Status:** ✅ Recommendation
**CAC alignment:** Direct.

### W3C DID Core 1.0
**Status:** ✅ Recommendation
**CAC alignment:** Direct (using `did:web` for issuer, `did:cardano` for agents, Ethereum addresses for operators).

### NIST 800-63-3 Digital Identity (IAL2 / IAL3)
**Status:** ✅ Standard
**CAC alignment:** Direct (IAL2 minimum for Developer / Studio, IAL3 for Enterprise / Anchor).

### Model Context Protocol (MCP)
**Status:** Anthropic-published open standard, broad industry adoption
**CAC alignment:** CAC publishes an MCP server (planned Phase C).

### Coinbase AgentKit
**Status:** Public SDK
**CAC alignment:** AgentWallet.sol designed to be AgentKit-compatible.

---

## 9. Review cadence

**Quarterly review:** Navigator (or designated counsel) reviews this document every 90 days. Updates dated and versioned.

**Triggered review:** Any of the following triggers an out-of-band review within 7 days:
- A 🟠 bill becomes 🔴 or vice versa
- Enforcement action against a similar token / credential product
- SEC, FinCEN, or FTC guidance affecting CAC's positioning
- A material EU AI Act delegated act published
- Any partner / counsel / customer raises a regulatory concern

---

## 10. Pre-positioning principle

CAC's design choices should **anticipate** regulation, not chase it. Where two design choices are equally good operationally, **choose the one that survives the strictest plausible reading of pending legislation**. This is more expensive in the short term and dramatically cheaper in the long term.

Examples of pre-positioning currently in CAC:
- Face-value P2P transfer (anticipates strict reading of Howey)
- USDC backing (anticipates GENIUS / similar stablecoin rules)
- KYA-bound operator identity (anticipates operator accountability laws)
- Constitutional binding hash (anticipates AI provenance / transparency rules)
- Jurisdictional routing in the inference router (anticipates state-by-state and EU/US fragmentation)
- 4.5% APY framed as savings, not yield (anticipates investment-contract framing)

---

## 11. Open monitoring assignments

| Topic | Assigned to | Cadence |
|---|---|---|
| US federal crypto bills | Counsel (TBD) | Monthly |
| EU AI Act delegated acts | EU counsel (TBD) | Quarterly |
| State AI laws (US) | Navigator + counsel | Quarterly |
| SEC enforcement actions on token products | Navigator | As they occur |
| FinCEN / state money transmitter rules | Counsel | Quarterly |
| MAS / VARA / FINMA updates | Defer until international expansion | — |

---

## 12. Counsel requirements

Before Phase 2 launch (500-card production run + public tier signup), Cuttlefish Labs must retain:

1. **US federal counsel** with crypto + securities experience (Cooley, Latham, K&L Gates, or similar)
2. **US state money transmitter counsel** (FS Vector, Lewis Brisbois, or similar specialist firm)
3. **EU counsel** for AI Act + MiCA (Bird & Bird, Linklaters, or similar)
4. **AI / sectoral counsel** as deployment scope clarifies

These are not optional. The token + identity + multi-jurisdiction design surface area requires real legal coverage. Budget: $50K-$150K for opening engagement across all four; $20K-$40K/quarter ongoing.

---

*End of CAC Legislation Tracker v1.0*
*Living document — review quarterly, update on legislative triggers.*
