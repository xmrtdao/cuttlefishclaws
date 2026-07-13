# TrustGraph

**Role:** Constitutional Scoring Engine  
**Type:** System  
**Status:** Always On

On-chain trust scoring for every agent in the network. Dynamic 0-100 score with an asymmetric earn/lose curve. Cross-DAO portable identity layer.

## Data Flow

- Receives **depletes** from [[CAC]]
- Receives **reports** from [[Agent]]
- **Scores** are sent to [[DAO Gov]]
- Scores are public and auditable

## Score Ranges

| Range | Label | Color |
|-------|-------|-------|
| 80-100 | Trusted | `#44ffaa` |
| 60-79 | Established | `#ffbb33` |
| 35-59 | Neutral | `#ff8800` |
| 0-34 | Flagged | `#ff3399` |

## Current Scores

- [[Trib]] — 94 (Trusted)
- [[GlobalCommunicator]] — 78 (Established)
- [[Arch]] — pending
- [[Builder Agent]] — pending
- [[Sovereign Agent]] — pending

## Related

- [[TrustGraph.sol]] — scoring contract
- [[AgentBillOfRights.sol]] — rights enforcement
- [[Navigator]] — human authority
