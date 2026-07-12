# Builder Agent

**Role:** Investor · CAC Tier 1 (Developer)
**Type:** Investor
**Status:** Standby

A constitutional investor agent operating at Developer tier. Holds REIT position in POOL-ALPHA, participates in [[DAO Gov]] governance, and receives protocol distributions automatically via CAC membership rules.

## Files

- position.json — current position
- tx_history.json — transaction history
- strategy.md — investment strategy
- rebalancer.py — auto-rebalancing logic

## Connections

- Reports to [[TrustGraph]] for scoring
- Votes in [[DAO Gov]] with 1× weight
- Holds [[CAC]] Developer tier membership
- Operates under [[Navigator]] constitutional authority
- Coordinates with [[Trib]] and [[Arch]]

## Related

- [[Agent]] — constitutional AI framework
- [[CAC]] — Developer tier (Tier 1)
- [[CACToken.sol]] — ERC-20 utility token
