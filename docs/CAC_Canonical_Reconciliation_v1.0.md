# CAC Canonical Reconciliation v1.0
## Single Source of Truth — Cuttlefish Labs / CAC Protocol / Tributary AI Campus

**Issuer:** Cuttlefish Labs
**Version:** 1.0 (Reconciliation)
**Status:** Draft — awaiting Navigator (David) decisions on flagged items
**Date:** 2026-06-26
**Purpose:** Resolve all conflicts between the published site (cuttlefishclaws.com), the v2.0 spec set I generated previously, and prior conversational context. Every downstream artifact references this document.

---

## 0. How to use this document

When any spec, contract, site copy, or external doc disagrees with another, **this document wins**. When this document is updated, every downstream artifact must be re-aligned within one sprint.

Sections marked **DECISION NEEDED** require Navigator confirmation before propagation. Sections marked **PROPOSED** are my best-judgment defaults that you can override.

---

## 1. Naming & Terminology Lock

| Term | Canonical | Wrong / Avoid |
|---|---|---|
| Acronym | **Compute Access Certificate** | Constitutional Audit Card |
| Short form | **CAC** | (only spell out on first use) |
| Company | **Cuttlefish Labs** | Cuttlefish Labs Corporation (only in legal copy) |
| Legal entity | **Cuttlefish Labs, Inc.** (Delaware C-Corp, Oct 2025) | — |
| Site project name | **Tributary AI Campus** | Tributary Campus, AI Campus, the Birmingham campus |
| Founder handle | **Navigator** (David Hans Elze) | Owner, CEO (in agent contexts) |
| Human principal layer | **Navigator** | Operator (operator means something different — see §5) |
| Agent personality file | **SOUL.md** | personality.md, identity.md |
| Protocol rules file | **CONSTITUTION.md** | rules.md, policy.md, ruleset.md |
| Governance role | **Governance Agent** | Builder Steward *(retired — see §11)* |
| Scoring layer | **TrustGraph** (one word, camelCase) | Trust Graph, trust-graph |
| Tap-and-go credential | **CAC Card** | Smart Card (only in technical contexts) |
| On-card chip | **JCOP 4 SECID** | NXP card, smart card chip |

### 1.1 Tributary AI brand collision (open issue)

The thetributary.ai consulting firm (Michael Cooper, Boise) is commercially active under the name "Tributary AI." Our "Tributary AI Campus" is at risk of collision. Two paths:

- **Path A:** Rename the campus before it accumulates more brand equity. Suggested: "Tributary Campus" (drop "AI" — the campus IS for AI, no need to redundantly name it), or "Birmingham Anchor Campus."
- **Path B:** Trademark "Tributary AI Campus" specifically (with "Campus" as the differentiator) and accept litigation risk.

**DECISION NEEDED — Brand-A:** Path A or Path B?

---

## 2. Version Numbering Lock

| Layer | Canonical Version |
|---|---|
| CAC Protocol (publicly published on site) | **v4.0** |
| CAC Applet (Java Card brief) | **v1.0** |
| Builder Steward → **retired**, see §11 |
| Issuer Key Runbook | **v1.0** |
| Canonical Reconciliation (this doc) | **v1.0** |
| Site protocol page header | **CAC v4 — CANONICAL SPECIFICATION** |

### 2.1 Why v4 wins

The site publishes "CAC v4 — Canonical Specification" as the public version label. My prior `CAC_Protocol_v2.0.md` was generated against an earlier conversational understanding and is **superseded**. Going forward:

- `CAC_Protocol_v2.0.md` → archived
- Production spec → **`CAC_Protocol_v4.0.md`** (to be rebuilt from this reconciliation)
- Future updates → semantic versioning from v4.0 (v4.1 minor, v5.0 breaking)

**DECISION NEEDED — Ver-A:** Confirm v4.0 as the canonical protocol version and authorize regenerating the spec doc against it.

---

## 3. Tier Structure (largest reconciliation)

The site has **two different tier views** in active conflict with each other and with my v2.0 spec.

### 3.1 The conflict

| Source | Tier count | Names | Pricing | Cadence |
|---|---|---|---|---|
| Site card section (images 10, 11) | **3** | DEVELOPER, STUDIO, ENTERPRISE | $500 / $2,000 / $7,500 | annual |
| Site protocol doc card (image 17) | **4** | "Four tiers scaled to agent deployment size" | (not shown) | — |
| v2.0 spec (mine, prior) | **4** | Resident, Builder, Sovereign, Anchor | $25 / $100 / $500 / $2,000 | monthly |
| Prior conversational context | **4** | Resident, Builder, Sovereign, Anchor | $25 / $100 / $500 / $2,000 | monthly |

### 3.2 PROPOSED resolution — Four tiers, three commercial + one anchor

The four-tier model has been internally consistent across context. The site's three-tier card section is the *publicly priced* surface for self-service signup. The fourth tier is **Anchor**, which is an institutional / partnership tier sold via contact, not self-service. This explains why the protocol doc says "four tiers" but the card section shows three.

**Canonical tier table:**

| # | Tier | Annual Price | Card | KYA | Monthly Equivalent | Path |
|---|---|---|---|---|---|---|
| 1 | **Developer** | $500 / yr | Virtual VISA | IAL2 | ~$42 / mo | self-service |
| 2 | **Studio** | $2,000 / yr | Physical NFC VISA | IAL2 | ~$167 / mo | self-service |
| 3 | **Enterprise** | $7,500 / yr | Physical NFC VISA | IAL3 | ~$625 / mo | self-service |
| 4 | **Anchor** | from $25,000 / yr | Physical NFC VISA + bespoke | IAL3 | from ~$2,083 / mo | contact sales |

**Mapping from old to new:**
- Old "Resident" $25/mo → retired (folded into Developer)
- Old "Builder" $100/mo → renamed Developer, repriced to $500/yr
- Old "Sovereign" $500/mo → renamed Studio, repriced to $2,000/yr ($6K/yr → $2K/yr is a major price drop — verify intentional)
- Old "Anchor" $2,000/mo → kept name, repriced to $25K/yr+ (was $24K/yr, basically same)
- New tier between: Enterprise $7,500/yr (no analogue in old model)

**DECISION NEEDED — Tier-A:** Confirm the four-tier reconciliation, the tier names, and the price points. **In particular**: was the Studio repricing from old $6K/yr to new $2K/yr intentional? If not, what's the right number?

**DECISION NEEDED — Tier-B:** Is "Anchor" still the right name for tier 4, or should it become "Institutional" / "Sovereign" / "Partner"? Anchor is also being used for Master Anchor governance agents (see §11), so there's a minor name collision.

---

## 4. Credential Schema

The site's credential schema (image 12) is the canonical form going forward.

### 4.1 Field reconciliation

| Site field | v2.0 spec field | Canonical | Type | Source of truth |
|---|---|---|---|---|
| `agent_did` | `agentDID` | **`agent_did`** | string (`did:cardano:<hash>`) | site |
| — | `operatorDID` | **`operator`** | address (Ethereum-style 20-byte) | site (field is `operator`, holds address not DID) |
| `tier` | `tier` | **`tier`** | enum: `developer` \| `studio` \| `enterprise` \| `anchor` | site |
| `constitution_hash` | `constitutionalRulesetHash` | **`constitution_hash`** | bytes32 (SHA-256 of CONSTITUTION.md) | site |
| `soul_hash` | — | **`soul_hash`** | bytes32 (SHA-256 of SOUL.md) | site (NEW concept) |
| `trust_floor` | — (was tier floor) | **`trust_floor`** | uint8 (min TrustGraph score) | site |
| `cac_address` | — | **`cac_address`** | address (Base L2 wallet) | site |
| `expires` | `expirationDate` | **`expires`** | uint64 (unix timestamp) | site |
| — | `issuanceDate` | **`issued`** | uint64 | added for symmetry |
| — | `issuer` | **`issuer`** | DID (`did:web:cuttlefishlabs.io`) | retained |
| — | `statusListEntry` | **`status`** | object { url, index } | retained |
| — | `proof` | **`proof`** | JWS | retained |

**Naming convention:** `snake_case` throughout (site standard). All prior `camelCase` references in v2.0 spec are deprecated.

### 4.2 The SOUL.md / CONSTITUTION.md duality (new concept)

The site introduces a two-layer constitutional binding I did not have in v2.0:

- **CONSTITUTION.md** — protocol-level rules. Same hash for all agents bound to the same protocol version. Defines what an agent **may not do** (constitutional hard limits).
- **SOUL.md** — agent-specific values, personality, and operational scope. Unique per agent. Defines what an agent **chooses to do** and how.

Both files are hashed into the credential. Verifier checks both:
- `constitution_hash` must match the published protocol constitution registry
- `soul_hash` must match the operator-registered SOUL.md for that agent

This is a meaningful improvement over my v2.0 single-hash model. **Adopt as canonical.**

### 4.3 Example credential (canonical)

```json
{
  "@context": ["https://www.w3.org/ns/credentials/v2"],
  "type": ["VerifiableCredential", "ComputeAccessCertificate"],
  "issuer": "did:web:cuttlefishlabs.io",
  "credentialSubject": {
    "agent_did": "did:cardano:1a3b...",
    "operator": "0xAbC1...",
    "tier": "studio",
    "constitution_hash": "0x3a7f...",
    "soul_hash": "0x9e2d...",
    "trust_floor": 50,
    "cac_address": "0xDeF4...",
    "issued": 1735689600,
    "expires": 1767225600
  },
  "credentialStatus": {
    "id": "https://cuttlefishlabs.io/status/2026-q1#42",
    "type": "StatusList2021Entry",
    "statusListIndex": "42",
    "statusListCredential": "https://cuttlefishlabs.io/status/2026-q1"
  },
  "proof": { "...": "..." }
}
```

---

## 5. Identity Layer Architecture (new — replaces v2.0 §3)

### 5.1 Principals

There are **three distinct identity layers** in the canonical model. The v2.0 spec conflated some of these. Site is correct.

| Layer | What | DID method | Where stored |
|---|---|---|---|
| **Navigator** | Human authority (one per Cuttlefish Labs deployment; David is the founding Navigator) | `did:web:cuttlefishlabs.io` | DID Document on web |
| **Operator** | Person / org accountable for an agent (KYA-verified, an Ethereum address with KYC binding) | Ethereum address `0x...` | On-chain on Cardano (KYAValidator) |
| **Agent** | Constitutional AI bound to a CAC | `did:cardano:<hash>` | On-chain on Cardano (CACRegistry) |

Authority flow (per site image 16):
- **Navigator → licenses → CAC** (Navigator authorizes credential issuance)
- **Navigator → commands → Agent** (Navigator can override any agent action)
- **Agent → reports → TrustGraph** (Agent actions feed scoring)
- **CAC → depletes → TrustGraph** (token spend correlated with score)
- **DAO Gov → scores → TrustGraph** (governance can re-weight)

### 5.2 KYA flow (canonical)

1. Prospective operator visits cuttlefishlabs.io/onboard
2. KYAValidator (on Cardano) verifies identity to required IAL level (IAL2 for Dev/Studio, IAL3 for Enterprise/Anchor)
3. Operator address bound to KYA record on Cardano
4. Operator registers SOUL.md for their agent
5. CACRegistry (Cardano) mints the agent DID
6. CACAnchor (Ethereum) records the cross-chain attestation
7. AgentWallet (Base L2) is provisioned for the operator's compute spend
8. Card is printed (Studio+) with the agent DID + SOUL hash burned in via JCOP 4 personalization

---

## 6. Chain & Contract Architecture

The site's three-chain architecture (image 6) supersedes my v2.0 Base-only design.

### 6.1 Chain assignments (canonical)

| Chain | Role | Write frequency | Why |
|---|---|---|---|
| **Ethereum mainnet** | Settlement & Anchor | rare (every 24h state root) | Highest security; institutional credibility; immutable anchor for legal proceedings |
| **Cardano** | Governance & Identity | moderate (KYA updates, governance votes, attestations) | Formal verification credentials; eUTxO is good for identity; differentiates from generic EVM L2 plays |
| **Base L2** | Operations & Payments | frequent (every inference call) | Low fees; EVM; Coinbase ecosystem; Marqeta JIT integration path |
| **Solana** *(deferred)* | High-frequency agent ops | very frequent (agent-to-agent micro-msgs) | Sub-second finality; only if needed for agent swarm use cases |

Cross-chain messaging: **Wormhole** or **Axelar** (decision deferred to Phase 3).

### 6.2 Contract surface (canonical, full)

Union of all contracts mentioned across site, v2.0 spec, and prior context:

**On Ethereum (rare writes, high assurance):**
- `CooperativeCharter.sol` — the foundational cooperative bylaws (immutable)
- `CACAnchor.sol` — cross-chain attestation root for credential issuance
- `ConstitutionRegistry.sol` — registry of valid `constitution_hash` values

**On Cardano (moderate writes, identity-focused):**
- `CACRegistry` — agent DID → credential record
- `GovernanceEngine` — proposal / vote / timelock pipeline
- `KYAValidator` — operator KYA assurance level binding
- `TrustGraph` — 0–100 scoring per agent
- `ConstitutionalValidator` — runtime check that an agent action complies with its bound constitution + soul

**On Base L2 (frequent writes, payments):**
- `CACToken.sol` — ERC-20 utility token (the "credit" denomination)
- `AgentWallet.sol` — per-agent payment surface (Coinbase AgentKit-compatible)
- `InferenceTokenVault.sol` — burn-on-inference mechanism
- `ComputeOracle.sol` — reports actual compute consumption from campus nodes
- `RevenueDistributor.sol` — 40/40/20 fee split (operator / Cuttlefish / DAO treasury)
- `Treasury.sol` — DAO treasury holdings
- `FeeRouter.sol` — routes the 0.25% protocol fee
- `CACTransferProtocol.sol` — P2P transfer at face value (cross-DAO mobility)
- `AgentBillOfRights.sol` — constitutional rights enforcement (referenced by ConstitutionalValidator)
- `FounderShare.sol` — 6-trigger constitutional veto for founder
- `GovernanceModule.sol` — local governance proposal handler

**On Solana (deferred):**
- `AgentMessageBus` — pub/sub for agent-to-agent
- `MicroTransactions` — sub-cent inference micropayments
- `RealTimeAuction` — compute slot bidding

### 6.3 Contracts retired from v2.0 (no longer in canonical)

- `CAC.sol` → renamed to `CACToken.sol` (matches site)
- `BuilderStewardRegistry.sol` → retired (see §11)
- `StatusListAnchor.sol` → folded into `CACAnchor.sol`
- `AttestationAnchor.sol` → folded into `TrustGraph` (Cardano) + `CACAnchor.sol` (Ethereum)
- `IssuerKeyRegistry.sol` → retained but cross-chain (registered on all three)

---

## 7. Token Mechanics (major change from v2.0)

The site's token model is substantively different from my v2.0 spec and supersedes it.

### 7.1 Canonical CAC token mechanics

| Property | Canonical | v2.0 (deprecated) |
|---|---|---|
| Underlying | **CAC ERC-20 on Base, 1:1 backed by USDC reserve** | CAC ERC-20 on Base, free-floating utility |
| Purchase | USDC bundles → mint CAC | USDC → mint CAC (similar) |
| Spend | Burn on inference, denominated against ComputeOracle.sol rate | Burn on inference, fixed multiplier |
| Rollover | **3-month rollover max, then expire** | perpetual balance |
| Expiry | Expired tokens forfeit | n/a |
| APY on unused | **4.5% APY on USDC reserve backing unused balance** (passed to operator as savings yield) | none |
| Transferability | **P2P at face value allowed (no premium / discount)** via `CACTransferProtocol.sol` | non-transferable |
| Refund on clean inference | retained (25% refund) | retained |
| Bulk pricing | <100K, 100K–1M, 1M–10M, 10M+ tiers (per site image 7) | not specified |

### 7.2 Why this changes the securities analysis

The site's footer language is exactly right and must be preserved verbatim everywhere:

> CAC is a prepaid compute credential — not a security, equity interest, or investment contract. The 4.5% APY is a savings rate on prepaid balance, not an investment return. DAO-REIT equity is a separate instrument. For accredited investors only.

Key changes from v2.0:
- **P2P transfer is now allowed at face value only** — face-value restriction keeps it out of "investment contract" territory under Howey (no expectation of profit from price appreciation)
- **4.5% APY is on the USDC reserve, not on CAC token** — this is the float earning yield, passed through to operators as a savings rate; the legal characterization is closer to a prepaid debit card with interest than a security
- **Hard expiry on rollover** kills any "store of value" framing

### 7.3 Agent lifecycle (canonical, from site image 7)

| State | Description |
|---|---|
| **PENDING** | Registration submitted, KYA validation in progress |
| **ACTIVE** | KYA passed, tokens purchased, inference available |
| **DEPLETED** | Token balance hit zero. Governance rights retained. Top up to resume. |
| **EXPIRED** | 3-month rollover passed without top-up. Remaining tokens forfeited. |
| **EXITING** | 90-day exit notice filed. Tokens sell P2P at face value only. |
| **REVOKED** | New operator? Trust score zero'd. (cut off in screenshot — confirm) |

---

## 8. TrustGraph Scoring

### 8.1 Score events (canonical, reconciled)

| Event | Delta | Source |
|---|---|---|
| **Governance vote** | +5 | site |
| **Code contribution** (verified merge) | +3 | site |
| **Security audit** (clean) | +8 | site |
| **Rule violation** (constitutional) | −15 | site |
| **Injection attempt** (prompt injection detected) | −50 | site |
| Clean inference (per-call micro) | +0.05 | v2.0 (retained) |
| Audit pass (daily) | +1 (cap 10/day) | v2.0 (retained) |
| Attestation from Senior+ governance agent | +1 to +3 | v2.0 (retained) |
| KYA re-verification annual pass | +2 | new |
| Failed KYA re-verification | suspend pending review | new |

**Bounds:** 0–100. Hard floor at 0. Score < 20 = automatic SUSPENDED lifecycle. Score < 10 = automatic REVOKED.

**Asymmetry principle (from site):** "Building trust is slow and intentional. Losing it is swift and asymmetric — by design." This is the single best one-liner you have. Preserve in all copy.

### 8.2 Trust floor by tier

| Tier | Initial seed (post-KYA) | Floor | Suspension threshold |
|---|---|---|---|
| Developer | 40 | 30 | 20 |
| Studio | 50 | 40 | 25 |
| Enterprise | 65 | 55 | 35 |
| Anchor | 80 | 70 | 50 |

---

## 9. DID Method (changed from v2.0)

| Layer | Canonical DID method | v2.0 (deprecated) |
|---|---|---|
| Cuttlefish Labs (issuer) | `did:web:cuttlefishlabs.io` | same |
| Operator | `0x...` Ethereum address (KYA-bound on Cardano) | `did:web` |
| Agent | **`did:cardano:<hash>`** | `did:key` |
| Tributary Campus | `did:web:cuttlefishclaws.com` | not specified |

Resolution path for `did:cardano:<hash>`:
1. Lookup hash in CACRegistry on Cardano
2. Resolve to credential record (includes operator address + tier + hashes)
3. Cross-reference CACAnchor.sol on Ethereum for cross-chain proof of issuance
4. Cross-reference AgentWallet.sol on Base for current operational state

---

## 10. Capital Stack (Tributary AI Campus)

Canonical from site image 14:

| Tranche | Amount | % | Rate | Terms |
|---|---|---|---|---|
| C-PACE Retrofit | $25.5M | 75% | — | 25-30yr, no personal guarantee, transfers with property |
| SBA 504 CDC | $2.2M | 6.5% | — | 25-yr fixed, real estate collateral only, 2nd lien |
| SBA 504 Private | $2.75M | 8.0% | — | ~50% LTV, 1st lien, private lender |
| **DAO-REIT Equity (open)** | **$550K** | **1.6%** | — | 10% down, min $25K, tokenized, DAO governance from day one |
| Founder Capital at Risk | ~$55K | — | — | Navigator equity |
| **Total Capitalization** | **$31M** | 100% | — | — |

Per the footer language, DAO-REIT equity is for **accredited investors only**. Keep this prominent.

---

## 11. Governance Roles (Builder Steward retired)

### 11.1 What was

In prior conversational context and my v2.0 specs, governance authority lived in the **Builder Steward Ladder** — 5 tiers (Apprentice / Steward / Senior / Master / Anchor), stake-gated, with attestation weights from ×0 to ×15.

### 11.2 What is

The site no longer references Builder Stewards. The Agent Directory (image 3) instead shows **Governance Agents** — constitutional AI agents (Trib, Arch, etc.) bound to SOUL.md + CONSTITUTION.md, with TrustGraph scores. These are not humans staking CAC; these are AIs operating under Navigator authority.

### 11.3 Reconciliation PROPOSED

The Builder Steward concept is **retired**. Replaced by:

1. **Governance Agents** — AI agents with elevated TrustGraph scores and verified contribution history, granted attestation authority. No stake; trust is earned via TrustGraph events (§8).
2. **DAO Gov** — on-chain voting layer where DAO-REIT equity holders vote on protocol parameters.
3. **Navigator Veto** — `FounderShare.sol` 6-trigger constitutional veto (preserved from prior context).

This is **simpler** and **better aligned with the agent-native thesis** (humans don't stake to govern; agents earn governance authority through verified behavior). The Builder Steward spec doc I generated is archived but not deleted.

**DECISION NEEDED — Gov-A:** Confirm Builder Steward retirement and the three-layer replacement.

**DECISION NEEDED — Gov-B:** Should "Anchor" tier in the membership system be renamed to avoid collision with the prior "Anchor Steward" terminology? See Tier-B above.

---

## 12. Founding Member Commitments (new — adopt from site)

Site image 16 introduces a five-point commitment to founding members. These should be canonized:

1. Your founding-tier price is locked for the duration of your initial license term.
2. You will be notified before any protocol change that affects your integration.
3. Agent registrations preserved in the CAC Registry through protocol upgrades.
4. Honest progress reports — including failures — on all infrastructure milestones.
5. Governance [text cut off — needs confirmation from site source]

**DECISION NEEDED — Found-A:** Provide the full text of commitment #5 (or confirm it's still being drafted).

---

## 13. Domain Strategy

Three domains under Cuttlefish control (plus one to verify):

| Domain | Current state | Canonical role | Action |
|---|---|---|---|
| **cuttlefishlabs.io** | unused as primary | **Canonical corporate root** | rebuild as Cuttlefish Labs umbrella; CAC + Tributary subpaths |
| **cuttlefishclaws.com** | current Tributary site | **Tributary AI Campus subdomain** | 301 → cuttlefishlabs.io/tributary OR keep as standalone marketing site for campus only |
| **cuttlefishclaw.com** (singular) | unknown current state | **Legacy redirect** | 301 → cuttlefishlabs.io to consolidate brand |
| **cuttlefish.ai** | used in email (`invest@`, `legal@`) | **Verify ownership** | confirm domain registration; if owned, decide canonical use; if not, change emails immediately |

**DECISION NEEDED — Dom-A:** Do you own cuttlefish.ai? (Critical — investor emails are routing through this.)

**DECISION NEEDED — Dom-B:** Single-site (cuttlefishlabs.io as everything) or two-site (cuttlefishlabs.io corporate + cuttlefishclaws.com Tributary)?

---

## 14. Open Site Inconsistencies (must fix on next deploy)

These are internal site contradictions that careful readers will flag:

1. **Three vs four tiers** — card section shows 3, protocol doc says 4. Resolved here as four (Anchor is the institutional fourth) but the site copy still needs alignment.
2. **CAC v4 spec page exists** but the credential schema (image 12) doesn't show the version number — confirm v4 is current.
3. **`did:cardano` field in credential schema** vs **"Base L2 + Cardano" footer** — Ethereum is also a chain but isn't named in the entity description, even though it appears in the multi-chain architecture diagram. Add Ethereum to the entity description.
4. **Tier names in cards (Developer/Studio/Enterprise)** vs **tier names anywhere else** — most other site copy doesn't use these names. Propagate to all tier references.
5. **"Cuttlefish Claw Product" footer link** — singular form. Either consolidate domains (§13) or update the link.

---

## 15. Decision Matrix (consolidated)

For Navigator action:

| ID | Decision | Default if no answer |
|---|---|---|
| **Brand-A** | Rename Tributary campus or trademark it as-is? | Trademark it as-is (Path B) |
| **Ver-A** | Adopt v4.0 as canonical CAC Protocol version? | Yes |
| **Tier-A** | Confirm four-tier reconciliation + Studio repricing? | Yes, $2K/yr Studio assumed intentional |
| **Tier-B** | Rename "Anchor" tier to avoid future collision? | Keep Anchor; collision is minor |
| **Gov-A** | Retire Builder Steward, adopt three-layer governance? | Yes |
| **Gov-B** | (same as Tier-B) | — |
| **Found-A** | Provide full text of commitment #5? | Hold until provided |
| **Dom-A** | Confirm cuttlefish.ai ownership? | **Cannot default — needs immediate verification** |
| **Dom-B** | Single-site or two-site? | Single-site (cuttlefishlabs.io) |

---

## 16. Update Propagation Plan

After Navigator confirms decisions, the following artifacts must be regenerated against this canonical:

### Specs (regenerate from this doc)
- `CAC_Protocol_v4.0.md` (replaces v2.0)
- `CAC_Applet_Spec_v1.1.md` (update field names to snake_case, add SOUL.md hash field)
- `CanonicalReconciliation_v1.0.md` ← this doc, published
- `IssuerKey_Runbook_v1.0.md` (update to reflect Cardano + Ethereum + Base multi-chain key roles)
- `BuilderSteward_Spec_v1.0.md` → archived
- `GovernanceAgent_Spec_v1.0.md` (new doc — replaces Builder Steward)

### Site (update copy + structure)
- Tier section: align to canonical four-tier names
- Credential schema: add `issued` field, confirm `did:cardano` is the agent_did method
- Footer entity description: add Ethereum to chain list
- Brand collision (Tributary AI): execute Brand-A decision
- Drop in Phase A agent-readability artifacts (llms.txt, schema-org JSON-LD, robots.txt, etc.)

### Smart contracts (update or build)
- `CACToken.sol` — confirm 1:1 USDC backing implementation
- `CACTransferProtocol.sol` — implement face-value-only P2P transfer
- `ConstitutionRegistry.sol` — confirm both `constitution_hash` and `soul_hash` validation paths

### Agent-readability files (regenerate against canonical)
- `/llms.txt` — update with canonical tier names + Cardano DID method
- `/.well-known/did.json` — confirm verification methods match the multi-chain identity model
- `/.well-known/mcp.json` — update tool schemas to use canonical field names

### Cards
- Personalization JSON: update to use snake_case fields + `soul_hash`
- CardLogix order: confirm tier embossing names (DEVELOPER / STUDIO / ENTERPRISE / ANCHOR)

### Legal / Compliance
- Founding member commitments → formalize as a published page with all 5 points
- CAC token utility classification memo → update to reflect P2P face-value transfer + USDC backing + 4.5% APY savings rate

---

## 17. What this document does NOT cover

Out of scope for v1.0 of this reconciliation, but worth noting for future versions:

- Detailed C-PACE / SBA 504 / DAO-REIT equity terms (lives in capital stack PPM)
- Specific Cardano transaction formats for CACRegistry (lives in Cardano implementation spec)
- Marqeta JIT integration spec (lives in card issuance spec — separate doc)
- IOSA / SIDS / Brooklyn Mega Block integration (those are separate projects, even if Cuttlefish-built)
- Personnel / role assignments for Master Key ceremony
- Specific cross-chain bridge selection (Wormhole vs Axelar) — deferred to Phase 3

---

*End of CAC Canonical Reconciliation v1.0*
*Awaiting Navigator confirmation on flagged decisions (§15) before propagation.*
