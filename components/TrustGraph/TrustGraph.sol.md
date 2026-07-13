# TrustGraph.sol

**Address:** `0x5FbDB2315678afecb367f032d93F642f64180aa3`  
**Status:** Built

Dynamic 0-100 trust scoring contract. Every agent in the network has a trust score that follows an asymmetric earn/lose curve.

## Data Flow

- Receives score reports from [[Agent]] framework
- Receives depletion events from [[CAC]]
- Sends scores to [[DAO Gov]]
- Scores are cross-DAO portable

## Related

- [[TrustGraph]] — scoring engine overview
- [[AgentBillOfRights.sol]] — rights enforcement
- [[CACTransferProtocol.sol]] — cross-DAO portability
