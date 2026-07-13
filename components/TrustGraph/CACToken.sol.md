# CACToken.sol

**Address:** `0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512`
**Status:** Built

ERC-20 utility token on Base L2, 1:1 backed by USDC reserve. 0.25% protocol fee on all transactions. Tiers: Developer, Studio, Enterprise, Anchor.

## Token Mechanics

- **Underlying:** CAC ERC-20 on Base, 1:1 backed by USDC reserve
- **Purchase:** USDC bundles → mint CAC
- **Spend:** Burn on inference, denominated against [[ComputeOracle.sol]] rate
- **Rollover:** 3-month max, then expire
- **APY on unused:** 4.5% savings rate on USDC reserve backing unused balance
- **Transferability:** P2P at face value only (no premium/discount) via [[CACTransferProtocol.sol]]
- **Refund:** 25% refund on clean audit

## Related

- [[CAC]] — credential overview
- [[CACTransferProtocol.sol]] — cross-DAO transfer
- [[FeeRouter.sol]] — fee distribution
- [[Builder Agent]] — Developer tier holder
- [[Sovereign Agent]] — Studio tier holder
