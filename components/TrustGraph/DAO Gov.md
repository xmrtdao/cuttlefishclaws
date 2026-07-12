# DAO Gov

**Role:** Constitutional Governance Module  
**Type:** System  
**Status:** Always On

Proposal → vote → timelock → execute pipeline. Three proposal types. Founder veto via FounderShare.sol. All governance actions are public, auditable, and constitutional by design.

## Pipeline

1. Proposal submission
2. 7-day voting period
3. 48-hour timelock
4. Execution

## Proposal Types

- **Standard** — simple majority
- **Constitutional** — 66% supermajority
- **Emergency** — requires founder approval

## Data Flow

- Receives **scores** from [[TrustGraph]]
- **Governs** [[Navigator]] (structural sovereignty)
- All actions are on-chain and auditable

## Related

- [[GovernanceModule.sol]] — proposal pipeline
- [[FounderShare.sol]] — 6-trigger constitutional veto
- [[FeeRouter.sol]] — 40/40/20 fee split
- [[Trib]] — governance participant
- [[Arch]] — governance participant
- [[Builder Agent]] — weighted voter
- [[Sovereign Agent]] — 3× weighted voter
