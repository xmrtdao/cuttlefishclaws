# Two Stack Architecture

**Role:** Compute Stack vs Capital Stack — Clean Separation
**Type:** Documentation
**Status:** Canonical

Cuttlefish Labs runs **two separate financial instruments** that must never mix:

## Stack A — Compute (CAC Token)

- Prepaid compute access credential (utility)
- ERC-20 on Base L2, 1:1 USDC-backed
- Buyer: any KYA-verified AI agent operator
- 4.5% savings rate on USDC reserve (not investment return)
- P2P at face value only, 3-month hard expiry
- Structurally fails all four Howey prongs
- Contracts: [[CACToken.sol]], [[FeeRouter.sol]], [[CACTransferProtocol.sol]], [[GovernanceModule.sol]], [[FounderShare.sol]]

## Stack B — Capital (DAO-REIT Equity)

- Tokenized real estate equity (security)
- ERC-20 security token on Ethereum, Reg D 506(c) restricted
- Buyer: accredited investors only, min $25,000
- 6.4% APR from real estate income (investment return)
- No expiry, no refund, restricted transfer
- Openly a security — compliant by design
- Contracts: TRIBToken.sol (proposed), CooperativeCharter.sol, RealEstateAnchor.sol (proposed)

## Where they connect

Exactly one legitimate connection point: the **governance bridge**. TRIB equity holders vote on DAO-REIT decisions that affect campus operations, which in turn affects CAC operations. But: no bundled offerings, no mutual collateralization, no automatic conversion, no marketing crosslinks implying convertibility, no KYA shortcuts.

## Related

- [[CAC]] — compute stack credential
- [[CACToken.sol]] — compute utility token
- [[Navigator]] — human authority
- [[DAO Gov]] — governance pipeline
- [[TrustGraph]] — scoring layer
- [[Contracts]] — full contract surface
- [[AgentBillOfRights.sol]] — constitutional rights
- [[FeeRouter.sol]] — fee distribution
- [[CACTransferProtocol.sol]] — P2P transfer
- [[GovernanceModule.sol]] — governance handler
- [[FounderShare.sol]] — constitutional veto
- [[Canonical Reconciliation]] — single source of truth
- [[Product Thesis]] — why this exists
