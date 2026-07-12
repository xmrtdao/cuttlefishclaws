# KYA Signature Specification v1.0

**Cuttlefish Labs — CAC Protocol**
**Know-Your-Agent Identity Binding & Event Signatures**

---

**Document ID:** CFL-SPEC-KYA-001
**Version:** 1.0 (draft)
**Date:** 2026-06-27
**Status:** Architectural spec, pre-implementation
**Companion to:** CFL-SPEC-AR-001 (§3.2 Signature, §5.4 Key Management), CFL-SPEC-AIL-001 (principal hierarchy, Stewardship Standing)
**Classification:** Internal + AI Ethics Group deliverable
**Conforms to:** CFL-DECISION-001 (Builder Stewards retained; $E2R; §404 activity model)

---

## 1. Purpose

The Activity Registry assumes a `KYA_ID` and three signature roles (`actor_signature`, `witness_signatures`, `registry_signature`) but never defines them. This spec does. KYA — **Know Your Agent** — is the identity layer that answers, for every registry event: *who did this work, under whose accountability, and are they who they claim to be?*

KYA is what makes the §404 reward model defensible: a reward is paid to a **verified principal-bound actor** for **signed, attributable** work. It is also the binding that makes AIL-001's liability cascade enforceable — you cannot attribute a defect to a principal you cannot identify.

KYA binds three things into one verifiable identity:
1. **Who the actor is** — an agent, a human Builder Steward, or a hybrid team.
2. **Who is accountable** — the principal (Operator / Navigator) per AIL-001.
3. **What they may do** — the Stewardship Standing and CAC tier that gate which `activity_type`s they can be rewarded for.

---

## 2. The KYA_ID

A `KYA_ID` is a stable, resolvable identifier for a verified actor.

```
KYA_ID  =  "kya:" <namespace> ":" <subject>

namespace ∈ { agent, human, hybrid }
subject   =  multibase(  SHA-256( binding_document )  )

binding_document = canonical_json({
    actor_kind:        enum[agent, human, hybrid],
    agent_did:         "did:cardano:<hash>"    | null   // for agents (per canon)
    principal_ref:     PrincipalRef,                     // AIL-001 accountable party
    cac_credential_id: string | null,                   // bound CAC, if issued
    public_keys:       List[PublicKeyRef],              // signing keys (§3)
    ial_level:         enum[IAL2, IAL3],               // identity assurance
    issued_at:         ISO-8601 UTC,
    issuer:            "did:web:cuttlefishlabs.io"
})
```

```
PrincipalRef {            # the accountable layer (AIL-001 §3 principal hierarchy)
    principal_kind:  enum[navigator, operator, organization, dao]
    principal_id:    string          # e.g. operator address, org KYA_ID, DAO id
    binding_proof:   Signature       # principal's signature accepting accountability
}

PublicKeyRef {
    key_id:     string
    algorithm:  enum[ed25519, secp256k1, rsa-pss]   # matches AR-001 Signature.algorithm
    public_key: bytes
    purpose:    enum[actor_signing, witness_signing, rotation]
    bound_to:   enum[cac_card, operator_hsm, software_key]
    status:     enum[active, rotated, revoked]
}
```

The `KYA_ID` is content-addressed over the binding document, so it is verifiable offline and changes only when the binding materially changes (a new binding document supersedes via a `KYA_RENEWAL` event, AR-001 §5.4).

---

## 3. Key hierarchy and binding

KYA keys mirror the principal hierarchy. Three signing roles correspond to AR-001's three signature fields.

```
Navigator key (did:web issuer)        — issues KYA bindings & CAC credentials
        │ binds
        ▼
Principal key (Operator / Org / DAO)  — signs PrincipalRef.binding_proof, accepts liability
        │ authorizes
        ▼
Actor key(s)                          — sign ActivityEvent.actor_signature
   ├── Agent: on-card key (CAC card, non-exportable, ECDSA P-256/secp256k1)
   │          or agent DID key (did:cardano) for card-less agents
   └── Human Steward: operator-HSM or hardware-token key (ed25519 recommended)

Registry key (HSM Phase 1-2; MPC Phase 3+) — signs ActivityEvent.registry_signature
Witness keys = other actors' actor keys   — sign witness_signatures for consensus events
```

**Binding rule:** an actor key is valid for signing registry events only if (a) it appears `active` in a current KYA binding, and (b) that binding carries a valid `PrincipalRef.binding_proof`. **No principal binding ⇒ no valid signature ⇒ no reward.** This is the cryptographic expression of AIL-001's "agents are not legal persons; their principals are."

---

## 4. Signature construction and verification

### 4.1 What is signed
The actor signs the canonical event **excluding** registry-added fields:

```
actor_signing_payload = canonical_json(  ActivityEvent
    minus { self_hash, registry_signature, witness_signatures } )
actor_signature = Sign(actor_key, SHA-256(actor_signing_payload))
```

- `canonical_json` = RFC 8785 JCS (same as AR-001 §5.2), so signatures verify across implementations.
- Witnesses sign the same payload plus the actor_signature (so a witness attests to a specific actor claim).
- The registry signs the full event including `self_hash` last (AR-001 write path step 6).

### 4.2 Verification (registry write-path step 5, AR-001)
A registry node accepts an event only if **all** hold:
1. `actor_signature` verifies against an `active` actor key in the actor's current KYA binding.
2. The binding's `PrincipalRef.binding_proof` verifies against the named principal key.
3. For consensus events, ≥ N `witness_signatures` from distinct KYA_IDs in the required domain verify.
4. The actor's **Stewardship Standing** (AIL-001) and CAC tier meet the threshold for `activity_type`, as decided by the **Standing Gate (SGQ-001)** — see §5.
5. `signed_at` timestamps are within acceptable skew and ≥ the key's `issued_at`.

A failure on any check is a hard reject (no partial writes).

### 4.3 Algorithms
`ed25519` (default for software/human keys; fast, deterministic), `secp256k1` (CAC on-card keys, EVM/Cardano compatibility), `rsa-pss` (legacy/enterprise HSM interop). All three are the exact set AR-001 §3.2 `Signature.algorithm` enumerates; no others are permitted without a schema migration.

---

## 5. Standing gate (link to AIL-001)

KYA is not just "is this a real key" — it is "is this actor *entitled* to be rewarded for this activity." Before AR-001 marks an event `reward_eligible`, and again when RRC-001 routes it, the actor's KYA must show:
- **Stewardship Standing ≥ threshold** for the `activity_type`'s domain (AIL-001 tier ladder: Contributor → Builder Steward → Senior → Council).
- **CAC tier** sufficient where the activity requires it (Developer / Studio / Enterprise / Anchor).
- **IAL level** sufficient (IAL2 for Developer/Studio, IAL3 for Enterprise/Anchor).

Standing is **queried via the Standing Gate Query Service (SGQ-001)** — not stored in the signature — so it is always evaluated against the *current* record; a Steward whose Standing was slashed cannot retroactively earn on new events. SGQ-001 is the single authority that AR-001 (write path), RRC-001 (before paying), and KYA verification all call, so they never diverge.

---

## 6. Key lifecycle

| Event | Mechanism |
|---|---|
| **Issuance** | Navigator issues a KYA binding after IAL2/IAL3 verification of the principal; actor key generated (on-card for agents, HSM/hardware for humans). |
| **Rotation** | `KYA_RENEWAL` event (AR-001) supersedes the binding with a new `public_keys` set; old key → `rotated`; prior events remain valid (signed before rotation). |
| **Revocation** | A `SLASH_APPLIED` / compromise event sets key → `revoked` with a compromise timestamp; events signed by that key **after** the timestamp are flagged for re-validation (AR-001 §5.4). |
| **Principal change** | A new principal must re-sign `binding_proof`; until then the actor cannot sign new reward-eligible events (accountability gap is closed before, not after). |

---

## 7. Privacy & §404 posture

- KYA bindings store **identifiers and keys, never raw PII**; IAL verification artifacts live in the KYC/KYA provider system under standard controls, referenced by hash. On-registry and on-chain data is hash-only (consistent with AR-001 anchoring and GDPR).
- KYA makes the §404 story complete: every reward is attributable to a verified, principal-bound actor performing a classified activity — there is no anonymous, balance-based, or principal-less reward path.
- KYA is **not** itself a financial instrument and must be described per POS-001 as identity/credentialing, never as "staking" or "validator registration."

---

## 8. Failure modes

| Failure | Mitigation |
|---|---|
| Stolen actor key | Revoke with compromise timestamp; re-validate post-timestamp events; principal liable per AIL-001 until revocation filed |
| Principal repudiates accountability | `binding_proof` is a non-repudiable signature captured at binding time; repudiation is itself a disputable event |
| Sybil actors | IAL2/IAL3 + minimum-time Standing thresholds (AIL-001 anti-sybil); witness diversity for consensus events |
| Algorithm downgrade attack | Algorithm fixed in `PublicKeyRef`; registry rejects mismatched algorithm; no negotiation |
| Cross-scope replay | `actor_signing_payload` includes `registry_scope` and `prev_event_hashes`; a signature is valid only for its scope position |

---

## 9. Phased implementation

| Phase | Scope |
|---|---|
| **Phase 1 (pilot)** | `agent` + `human` namespaces; ed25519 + secp256k1; single-issuer (Cuttlefish) KYA bindings; software keys acceptable for human Stewards; registry key in HSM. |
| **Phase 2** | CAC on-card key binding for agents; IAL3 path; rotation/revocation flows wired to AR-001 events; **Standing Gate (SGQ-001)** integration. |
| **Phase 3** | `hybrid` teams with weighted multi-actor signatures; MPC registry signing; rsa-pss enterprise interop; witness-diversity enforcement. |

---

## 10. Open questions

1. **CAC card vs DID key precedence** for agents that have both — recommend on-card key is authoritative when present.
2. **Witness count N** per domain — fixed, or risk-scaled by reward size? Recommend risk-scaled, defined per rubric.
3. **Principal-of-a-principal** (DAO as principal of an operator of an agent) — **resolved:** AIL-001 §3.1 specifies `max_delegation_depth` = 3, and the chain must terminate at a natural person or legal entity within 3 levels (verified per PVP-001). Remaining detail: per-level witness requirements for deep chains.
4. **Hybrid-team signature weights** — reuse AR-001 `ContributorRef.weight`; confirm summation rules (≤ 1.0).

---

## 11. Next concrete implementation steps

1. Implement the `KYA_ID` binding-document hash + content addressing.
2. Implement signature construction/verification over RFC 8785 JCS for ed25519 + secp256k1.
3. Integrate the **Standing Gate (SGQ-001)** — KYA verification *calls* it; it does not build its own Standing read.
4. Wire `KYA_RENEWAL` / revocation as AR-001 events.
5. Principal identity/KYC verification is owned by **PVP-001** (KYA consumes the verified `PrincipalChain`); the KYC **vendor is not yet selected** (PVP-001 §11 Q1). Registry stays hash-only.

---

**Maintainer:** Cuttlefish Labs (Navigator) + collaborating Builder Stewards

**Companion documents:**
- `ACTIVITY_REGISTRY_V1.txt` (AR-001 §3.2, §5.4) — consumer of these signatures
- `AGENT_IDENTITY_AND_LIABILITY_FRAMEWORK.md` (AIL-001) — principal hierarchy, Standing
- `SGQ-001_STANDING_GATE_QUERY.md` — the Standing Gate this spec calls (§5)
- `PVP-001_PRINCIPAL_VERIFICATION_PROTOCOL.md` — verifies the principal behind `binding_proof`
- `REWARD_ROUTER_CONTRACT.md` (RRC-001) — resolves settlement identity via KYA
- `EVIDENCE_STORAGE_SPEC.md` (EVS-001) — evidence access keyed to KYA
- `CAC_SECTION_404_POSITIONING.md` (POS-001) — vocabulary discipline
