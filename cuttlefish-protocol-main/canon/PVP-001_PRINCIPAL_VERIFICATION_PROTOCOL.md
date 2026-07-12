# Principal Verification Protocol Specification v1.0

**Cuttlefish Labs — CAC Protocol**
**Verifying the Accountable Principal Before Liability Can Attach**

---

**Document ID:** CFL-SPEC-PVP-001
**Version:** 1.0 (draft)
**Date:** 2026-06-27
**Status:** Architectural spec, pre-implementation
**Companion to:** CFL-SPEC-AIL-001 (§3 Principal Hierarchy), CFL-SPEC-KYA-001 (PrincipalRef, binding_proof), CFL-SPEC-EVS-001 (verification-evidence custody)
**Classification:** Internal + AI Ethics Group deliverable
**Conforms to:** CFL-DECISION-001 (§404 activity model; rail separation; POS-001 vocabulary)

---

## 1. Purpose

AIL-001 §3 establishes that **every agent has at least one accountable principal**, documented as an immutable `PrincipalChain` and signed at KYA registration — but it defers the *how* of verifying that principal to a separate protocol (AIL-001 §676). This is that protocol.

PVP-001 is the gate that makes the whole liability architecture real: the AIL-001 cascade, the KYA-001 signature binding, and the §404 "verified principal-bound actor performing classified activity" story all depend on the principal actually being **who they claim, accountable, and reachable** before a CAC is issued.

> No verified principal ⇒ no valid binding ⇒ no CAC ⇒ no reward-eligible activity. Accountability is established *before* the agent acts, never reconstructed after.

PVP-001 verifies identity and accountability. It does **not** verify financial qualification — that is **accreditation** for the $E2R securities rail, an entirely separate process (CFL-DECISION-001 rail separation; KYA ≠ accreditation).

---

## 2. What is verified

For each principal in the `PrincipalChain` (AIL-001 §3.4), PVP establishes four things:

1. **Existence & identity** — the principal is a real, identifiable natural person or legal entity.
2. **Authority** — the signer accepting accountability is authorized to bind the principal (esp. for entities/DAOs).
3. **Accountability acceptance** — the principal has signed a non-repudiable acceptance of the AIL-001 §3.2 responsibilities (the KYA-001 `binding_proof`).
4. **Reachability** — a verified legal point of contact exists for dispute and Stewardship Review service.

The chain must **terminate at a natural person or legal entity** within `max_delegation_depth` (default 3, AIL-001 §3.1).

---

## 3. Assurance levels

PVP assurance maps to NIST IAL and to CAC tier (CAC-005 §4):

| PVP level | Identity assurance | Required for | Methods |
|---|---|---|---|
| **PVP-1** | IAL2 | Developer, Studio | remote KYC provider (document + liveness), or verified entity registry lookup |
| **PVP-2** | IAL3 | Enterprise, Anchor | PVP-1 + supervised/in-person proofing or notarized attestation; entity authority documents |
| **PVP-0** | none | Explorer ($0) only | self-asserted; **no reward eligibility, no agent actions with consequence** |

Anonymous or pseudonymous principals are **not permitted** at PVP-1+ (AIL-001 §3.1).

---

## 4. Verification methods (per AIL-001 §3.4 `verification_method`)

### 4.1 Natural person
- `kyc_provider` — accredited remote identity provider performs document verification + liveness; returns a pass/fail + an evidence bundle. PVP stores only the **hash** of the evidence (EVS-001), never the raw documents on the registry.
- `id_doc` — government ID verification (PVP-1) or supervised proofing (PVP-2).
- Output: `verification_hash`, `attested_at`, jurisdiction (ISO-3166), assurance level.

### 4.2 Legal entity (LLC, corporation, foundation)
- Registry lookup: entity exists and is in **good standing** in its jurisdiction of formation.
- **Authority proof:** the human signer is an authorized representative (officer, manager, or board-authorized) — evidenced by formation docs, operating agreement, or board resolution.
- Beneficial-ownership / control check to the extent required by jurisdiction.
- The entity's verified human signer is themselves PVP-verified as a natural person.

### 4.3 DAO principal
- A DAO may be a principal only with a **recognized legal wrapper** (e.g., Wyoming DAO LLC or a foreign DAO with a recognized wrapper) — AIL-001 §3.1.
- Verify: the wrapper entity (per §4.2), the on-chain governance address, and the **governing-entity authority** that can act for the DAO in a dispute.
- A wrapper-less, purely on-chain DAO is **not** an acceptable terminal principal.

### 4.4 Delegated (agent-of-agent)
- A senior agent may be an intermediate principal, but verification **recurses** until a natural person or legal entity terminates the chain within `max_delegation_depth`.
- Each delegation level carries its own signed authority; liability flows through to the delegating principal (AIL-001 §3.1, §3.4).

---

## 5. The verification flow

```
1. INTAKE
   Prospective principal submits PrincipalChain (AIL-001 §3.4) + evidence.
2. PER-LEVEL VERIFICATION
   For each level 0..n:
     - run the method (§4) for that principal_type
     - confirm authority (entities/DAOs)
     - hash the evidence → store via EVS-001 (contains_pii ⇒ s3/local, encrypted)
     - record verification_method, verification_hash, jurisdiction, attested_at
3. TERMINATION CHECK
   Assert terminal_principal is natural_person | legal_entity AND depth ≤ max (3).
4. ACCOUNTABILITY BINDING
   Terminal principal signs the AIL-001 §3.2 responsibilities acceptance
   = KYA-001 PrincipalRef.binding_proof (non-repudiable).
5. REACHABILITY
   Verify and record a legal point of contact for service of process / review.
6. WRITE
   Emit a KYA_REGISTRATION ActivityEvent (AR-001) carrying the signed,
   hash-anchored PrincipalChain. Only now may a CAC be issued (CAC-005 §7).
```

If any level fails, **no CAC issues**. Partial chains are rejected, not provisionally accepted.

---

## 6. Re-verification, change, and lapse

- **Cadence.** PVP re-verification is required at credential renewal and at least annually (a `KYA_RENEWAL` event referencing the prior chain, AIL-001 §3.4).
- **Principal change / transfer.** A new or changed principal must complete PVP and sign a fresh `binding_proof` **before** the change takes effect — the accountability gap is closed in front, never behind (KYA-001 §6).
- **Lapse.** If verification expires or a principal becomes unreachable, the agent is moved toward `SUSPENDED` (CAC-005 §12): signing of new reward-eligible events is blocked until the principal is re-verified.
- **Repudiation.** A principal attempting to repudiate accountability is met with the captured `binding_proof` (non-repudiable); repudiation is itself a disputable Stewardship Review matter (SRP-001) and does not retroactively unbind prior events.

---

## 7. Privacy & evidence custody

- PVP handles PII (identity documents, entity records). **No PII is written to the registry or anchored on-chain** — only `verification_hash` lives there (AIL-001 §3.4; EVS-001).
- Raw verification evidence is held by the KYC/identity provider and/or in the `compliance`/`legal_hold` evidence tiers (EVS-001 §6-7), encrypted, access-controlled, with retention tied to the §404 / Reg A+ audit window and a GDPR-erasure path that preserves the hash while redacting the payload.
- Auditor access (counsel, regulator, SOC2) is time-boxed and logged (EVS-001 §6).

---

## 8. §404 posture & rail separation

PVP is what lets every reward trace to a **verified, principal-bound actor** performing a classified activity — there is no anonymous, principal-less, or balance-based reward path. PVP verifies *identity and accountability only*. It explicitly does **not** confer or check **accreditation**; a PVP pass never qualifies anyone for $E2R (Rail B), and an accreditation pass never substitutes for PVP (CFL-DECISION-001). KYA and accreditation are different processes on different rails.

---

## 9. Failure modes

| Failure | Mitigation |
|---|---|
| Forged identity documents | Accredited KYC provider + liveness (PVP-1), supervised proofing (PVP-2) |
| Unauthorized entity signer | Authority proof (resolution/operating agreement) required before binding |
| Wrapper-less DAO as terminal principal | Rejected — recognized legal wrapper mandatory |
| Infinite delegation chain | `max_delegation_depth` (3) enforced; chain must terminate |
| Principal becomes unreachable | Annual re-verification + reachability check; lapse → SUSPENDED |
| PII leakage | Hash-only on registry; encrypted evidence tier; erasure path (EVS-001) |
| Accreditation/KYA conflation | Hard separation; PVP never touches financial qualification |

---

## 10. Phased implementation

| Phase | Scope |
|---|---|
| **Phase 1 (pilot)** | PVP-1 for natural persons + simple entities via one KYC provider; manual entity-authority review; evidence in encrypted s3/local; KYA_REGISTRATION events written. |
| **Phase 2** | PVP-2 / IAL3 path; automated entity-registry lookups; delegated-chain recursion; re-verification cadence + lapse → SUSPENDED automation. |
| **Phase 3** | DAO-wrapper verification workflow; beneficial-ownership checks where required; auditor-access tooling; cross-jurisdiction retention tags. |

---

## 11. Open questions

1. **KYC provider selection** — single provider vs multi-provider abstraction for jurisdiction coverage.
2. **Beneficial-ownership depth** — how far to pierce entity ownership, by jurisdiction. Defer specifics to counsel.
3. **Reachability standard** — registered agent vs verified email/legal address; what qualifies as valid service of process for a dispute.
4. **Sanctions/PEP screening** — include in PVP, or as a separate compliance gate? Recommend include at PVP-1+.
5. **Re-verification interval** — annual vs risk-based (higher tier / higher reward exposure → more frequent).

---

## 12. Next concrete implementation steps

1. Integrate one KYC provider for PVP-1 natural-person verification (pass/fail + evidence hash).
2. Implement the per-level `PrincipalChain` verification loop with the termination + depth checks.
3. Capture the `binding_proof` (KYA-001) and emit the `KYA_REGISTRATION` event; gate CAC issuance on it.
4. Wire evidence storage to EVS-001 (`contains_pii` ⇒ encrypted, retained, erasable).
5. Build the annual re-verification + lapse → SUSPENDED flow.

---

**Maintainer:** Cuttlefish Labs (Navigator) + collaborating Builder Stewards

**Companion documents:**
- `AGENT_IDENTITY_AND_LIABILITY_FRAMEWORK.md` (AIL-001 §3) — parent (principal hierarchy)
- `KYA-001_KYA_SIGNATURE_SPEC.md` — `binding_proof`, standing gate, key lifecycle
- `EVS-001_EVIDENCE_STORAGE_SPEC.md` — verification-evidence custody, retention, erasure
- `ACTIVITY_REGISTRY_V1.txt` (AR-001) — `KYA_REGISTRATION` event record
- `CAC_SECTION_404_POSITIONING.md` (POS-001) — vocabulary discipline
