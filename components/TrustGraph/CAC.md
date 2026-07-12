# CAC

**Role:** Compute Access Certificate
**Type:** System
**Status:** Always On

The CAC (Compute Access Certificate) is a prepaid compute credential — not a security, equity interest, or investment contract. It provides compute access, governance participation, and protocol distributions as described in membership terms. The 4.5% savings rate on prepaid balance is a savings rate on USDC reserves, not an investment return.

## Architecture

- Licensed by [[Navigator]]
- **Depletes** trust resources to [[TrustGraph]]
- Tiers: Developer → Studio → Enterprise → Anchor
- 0.25% protocol fee on all transactions
- 3-month hard expiry on rollover
- P2P transfer at face value only (no premium/discount)

## CAC Tiers

| Tier | Price | Voting | Agents | KYA |
|------|-------|--------|--------|-----|
| Developer | $500/yr | 1× | 3 | IAL2 |
| Studio | $2,000/yr | 2× | 12 | IAL2 |
| Enterprise | $7,500/yr | 3× | Unlimited | IAL3 |
| Anchor | from $25,000/yr | 10× | Unlimited | IAL3 |

## Related

- [[Builder Agent]] — holds Developer tier (Tier 1) position
- [[Sovereign Agent]] — holds Studio tier (Tier 2) position
- [[CACToken.sol]] — ERC-20 utility token contract
- [[CACTransferProtocol.sol]] — cross-DAO transfer
- [[Canonical Reconciliation]] — single source of truth
- [[Two Stack Architecture]] — compute vs capital separation
