# Evidence Storage Specification v1.0

**Cuttlefish Labs — CAC Protocol**
**Off-Registry Evidence Custody, Addressing & Retention**

---

**Document ID:** CFL-SPEC-EVS-001
**Version:** 1.0 (draft)
**Date:** 2026-06-27
**Status:** Architectural spec, pre-implementation
**Companion to:** CFL-SPEC-AR-001 (§3.1 evidence fields, §6 Storage Architecture), CFL-SPEC-KYA-001
**Classification:** Internal + AI Ethics Group deliverable
**Conforms to:** CFL-DECISION-001 (§404 activity model; rail separation)

---

## 1. Purpose

The Activity Registry is **evidence-anchored**: every event carries an `evidence_hash` (and optional `evidence_uri`, `evidence_storage`), but **the payload itself never lives in the Registry** (AR-001 §2 principle 3, §3.1). This spec defines where that payload *does* live, how it is addressed, how its integrity is proven against the registry hash, who may read it, how long it is kept, and how erasure is reconciled with an append-only chain.

This matters for three reasons:
1. **Compliance defensibility.** A §404 reward is only as auditable as the work product behind it. When counsel or a regulator asks "show me the validation that earned this reward," EVS-001 is what produces it — provably the same artifact whose hash is in the chain.
2. **Privacy / GDPR.** Keeping payloads off the immutable chain is what lets Cuttlefish honor erasure and data-minimization while preserving a tamper-evident audit trail (hash-only on-chain).
3. **Cost & scale.** Evidence (reports, transcripts, attestation payloads) is large; the chain stays small by holding only hashes.

---

## 2. Design principles

1. **Hash on the Registry, payload off it.** The Registry stores `evidence_hash = SHA-256(payload)`. EVS-001 stores the payload. The two are linked only by the hash.
2. **Content-addressed integrity.** The stored object is verifiable against `evidence_hash` independent of where it lives. Move it between tiers freely; the hash never changes.
3. **No PII on-chain, ever.** Anchored data (AR-001 §5.3) is hash-only. Any payload containing PII lives in an erasable, access-controlled tier — never IPFS/Arweave if it contains PII (see §6).
4. **Least authority.** Evidence is private by default; public exposure is opt-in per object and per audience (public / actor / sponsor / auditor).
5. **Retention is policy, not accident.** Every object has a retention class and disposition date; nothing is "kept forever by default" except its hash.
6. **Erasure-safe append-only.** Deleting a payload must never break the chain. The chain holds the hash; erasing the payload leaves a verifiable *tombstone*, not a gap (§7).

---

## 3. The evidence object

AR-001 §3.1 fields, defined here:

```
evidence_hash:     SHA-256(payload_bytes)          // canonical link; immutable
evidence_uri:      URI                              // where to fetch (resolvable)
evidence_storage:  enum[ ipfs, s3, ar, local ]      // backing store class
```

EVS-001 adds a custody record (kept off-registry, in the evidence index):

```
EvidenceRecord {
    evidence_hash:    SHA-256                 // primary key; == AR-001 field
    event_id:         UUID                    // owning ActivityEvent (back-ref)
    media_type:       string                  // e.g. application/pdf, text/markdown
    size_bytes:       uint64
    contains_pii:     bool                    // determines eligible stores (§6)
    storage_class:    enum[ipfs, s3, ar, local]
    locations:        List[StoredLocation]    // 1..n replicas/tiers
    encryption:       EncryptionRef | null
    visibility:       enum[public, actor, sponsor, auditor]
    retention_class:  enum[transient, standard, compliance, legal_hold]
    disposition_at:   ISO-8601 UTC | null     // null for indefinite (hash only)
    redacted:         bool                     // payload erased, tombstone remains
}

StoredLocation { backend, uri, replica_of, written_at, verified_at }
EncryptionRef  { scheme: enum[aes-256-gcm, age, none], key_ref, wrapped_for: List[KYA_ID] }
```

---

## 4. Storage classes (the `evidence_storage` enum)

| Value | Backing | Use | PII allowed? |
|---|---|---|---|
| `local` | Operator filesystem (pilot) / node-local | Phase-1 pilot; pre-upload staging | Yes (access-controlled) |
| `s3` | S3 / R2 object store | Default warm tier; private by ACL | Yes (encrypted) |
| `ipfs` | IPFS (pinned) | Public, content-addressed evidence | **No** |
| `ar` | Arweave | Permanent public archival | **No** |

**Rule:** `contains_pii = true` ⇒ `storage_class ∈ {local, s3}` **only**, encrypted, with a disposition date. `ipfs`/`ar` are for **public, non-PII** evidence whose permanence is a feature (e.g., a published validation report the campaign sponsor wants immutable).

This maps onto AR-001 §6's tiers: HOT (local/s3 + indices) → WARM (s3 parquet) → COLD (ipfs/ar, non-PII only) → ANCHOR (hash on public chain).

---

## 5. Write & verify

### 5.1 Write path (SDK side, before the registry write)
```
1. actor produces payload (validation report, vote receipt, attestation, …)
2. SDK computes evidence_hash = SHA-256(payload)
3. SDK sets contains_pii (see §5.1.1), then chooses storage_class
4. SDK encrypts if required, stores payload, gets evidence_uri
5. SDK constructs ActivityEvent with evidence_hash / evidence_uri / evidence_storage
6. event is signed (KYA-001) and written (AR-001)   ← hash now anchored to the chain
```
The payload is stored **before** the event is written, so a written event always has retrievable (or intentionally-private) evidence.

### 5.1.1 The `contains_pii` gate (fail-safe)

This is the most legally consequential decision in the spec — a `false` that should be `true` can put PII on IPFS/Arweave, which is **unrecoverable**. Therefore:

- **Default is `true`.** An object is treated as PII-bearing (→ `local`/`s3` only, encrypted, dispositioned) **unless affirmatively cleared**. There is no "probably fine" path.
- **Phase 1 (PILOT-001): actor-flagged only.** The actor/SDK explicitly marks each object `contains_pii` (default `true`); only an explicit clear allows `ipfs`/`ar`. **No automated heuristic is trusted to clear PII in the pilot.** A public, permanent store requires an explicit clearance step.
- **Phase 2+: automated detection** is added as a *defense-in-depth* layer that can only *raise* the flag, never silently clear it — specified in a separate `EVS-PII-DETECT` spec, keyed on NIST SP 800-122 PII categories, structured-data field tags, and pattern matchers (names, gov-IDs, contact, financial). Automated `true` overrides a human `false`; automated `false` never overrides a human/default `true`.
- **Clearance to a public/permanent store** (`ipfs`/`ar`) requires a recorded **PII-clearance review** (logged as an access/decision event), never a heuristic alone.

### 5.2 Verify
```
verify(evidence_hash, fetched_payload):
    return SHA-256(fetched_payload) == evidence_hash
```
Any auditor with read access can independently confirm the payload matches the on-chain hash. This is the whole point: provenance without trusting the storage layer.

### 5.3 Interface (SDK + verification API)

```
# SDK (actor side) — store BEFORE the event is written (§5.1)
evs.put(payload, contains_pii=True, retention="compliance", visibility="actor")
    → { evidence_hash, evidence_uri, storage_class }
evs.get(evidence_hash, as=kya_id)        → payload | 403 | 410(redacted/tombstone)
evs.verify(evidence_hash, payload)       → bool          # SHA-256 match (§5.2)

# Service API (access resolved against KYA-001 §6 on every read)
GET   /evidence/v1/{hash}              ?as=kya_id           → payload | 403 | 410(redacted)
POST  /evidence/v1/verify             {hash, payload}       → { match: bool }
GET   /evidence/v1/{hash}/record      ?as=kya_id            → EvidenceRecord (metadata)
POST  /evidence/v1/{hash}/erase       {requester, reason}   → tombstone | 423(legal_hold)
POST  /evidence/v1/{hash}/grant       {auditor_kya_id, ttl} → time-boxed access grant (logged)
```

A redacted object returns `410` with the tombstone, never the payload; erase honors retention class + legal hold (§7); every auditor read is logged as an access event (§6).

---

## 6. Access control

Resolved against KYA-001 identity:
- **public** — anyone; only for non-PII objects on s3-public/ipfs/ar.
- **actor** — the owning actor (and their principal) via KYA signature challenge.
- **sponsor** — the campaign sponsor scope (`campaign:<UUID>` chain, AR-001 §5.1).
- **auditor** — time-boxed grant to counsel/regulator/SOC2 auditor; every auditor read is itself logged as an access event.

Encrypted objects are wrapped per-recipient (`EncryptionRef.wrapped_for: List[KYA_ID]`); revoking access = re-wrapping without that recipient (future reads) + key rotation if the object is sensitive.

---

## 7. Retention, erasure, and the append-only reconciliation

This is the load-bearing section — how to honor erasure without breaking immutability.

- **The chain keeps the hash forever.** `evidence_hash` is part of `self_hash` (AR-001 §5.2) and cannot be removed without breaking the chain. It is also **non-PII** (a hash of PII is not PII under the data-minimization posture, provided the input space isn't trivially brute-forceable; for low-entropy payloads, salt before hashing — see Open Questions).
- **The payload can be erased.** Deleting the payload sets `redacted = true` and replaces stored bytes with a **tombstone**: `{ erased_at, reason, erased_by, original_hash }`. Verification of the original hash is no longer possible (by design), but the event, its signatures, and its reward record remain intact and auditable.
- **Retention classes:**

| Class | Disposition | Example |
|---|---|---|
| `transient` | auto-delete at `disposition_at` (e.g. 30–90 d) | intermediate drafts, superseded evidence |
| `standard` | warm tier ~2 years, then cold or delete | routine validation reports |
| `compliance` | retained through the §404 / Reg A+ audit window + statutory tail | reward-bearing evidence, attestations |
| `legal_hold` | erasure **blocked** until hold lifts | anything under dispute (AIL-001) or counsel hold |

- **Erasure vs legal hold:** a GDPR erasure request on an object under `legal_hold` is deferred (not refused silently) and surfaced to counsel; the lawful-basis conflict is resolved by a human, logged as an access/decision event.
- **Right-to-erasure flow:** request → verify requester via KYA → check retention class / holds → if erasable, redact payload + write a `CORRECTION_ISSUED`(action=annotate) event noting the erasure → the reward record stands (the *fact* of the activity is preserved; the *personal data* is gone).

---

## 8. Failure modes

| Failure | Mitigation |
|---|---|
| Storage lost but hash on-chain | Multi-location replicas (`StoredLocation`); compliance-class objects ≥ 2 backends incl. one cold |
| Hash mismatch on fetch | Verification fails loudly; event flagged `evidence_invalid` → AR-001 `CORRECTION_ISSUED`; reward eligibility recomputed (RRC-001 §6) |
| PII accidentally pinned to IPFS/Arweave | Pre-store `contains_pii` gate blocks it; CI/policy check; if it happens, it is unrecoverable — treat as a reportable incident |
| Auditor over-retention | Auditor grants are time-boxed and logged; expire automatically |
| Low-entropy payload hash reverses to PII | Salt low-entropy payloads before hashing (store salt with the payload, not on-chain) |
| Encryption key lost | Object effectively erased; acceptable for transient/standard, a recovery-key (escrow) required for compliance/legal_hold classes |

---

## 9. Phased implementation

| Phase | Scope |
|---|---|
| **Phase 1 (pilot)** | scope per **PILOT-001**: `local` + `s3` only; SHA-256 hashing in SDK; `contains_pii` **actor-flagged, default true** (§5.1.1, no automated clearing); visibility public/actor; standard + compliance retention; daily S3 snapshot (matches AR-001 §6.3). |
| **Phase 2** | Encryption (aes-256-gcm / age) with per-KYA wrapping; sponsor/auditor scopes; retention automation + disposition jobs; tombstone/erasure flow. |
| **Phase 3** | `ipfs`/`ar` cold tier for public non-PII evidence with anchor proofs; multi-backend replication for compliance class; legal-hold workflow with counsel interface. |

---

## 10. Open questions

1. **Hash-of-PII risk.** For low-entropy evidence (e.g., a short structured form), is a salted hash sufficient, or should such payloads be excluded from anchoring entirely? Recommend: salt + exclude the raw value from any public scope.
2. **Recovery-key escrow** for compliance/legal_hold encrypted objects — held under the **Issuer Key ceremony / Navigator multi-party control** in the Issuer Key Runbook (to be promoted to `CFL-SPEC-KEY-001`, per D-7). The evidence recovery-key is a **subordinate key under that ceremony**, not a separate trust root. (Remaining detail: the M-of-N threshold for evidence recovery vs. issuer signing.)
3. **Cross-jurisdiction retention** — EU vs US statutory tails differ; per-object jurisdiction tag? Defer to counsel.
4. **Sponsor-paid permanence** — if a sponsor wants Arweave permanence for a report that *might* later need erasure, the two conflict. Recommend: permanence only after a PII-clearance review.

---

## 11. Next concrete implementation steps

1. Implement SDK-side hash + store + `evidence_uri` return for `local`/`s3`.
2. Build the `EvidenceRecord` index keyed on `evidence_hash` with the back-ref to `event_id`.
3. Implement `verify(evidence_hash, payload)` and wire it into AR-001 write-path step 5 and the auditor read path.
4. Implement the `contains_pii` gate that restricts storage class.
5. Implement the tombstone/redaction + retention-disposition jobs (Phase 2).

---

**Maintainer:** Cuttlefish Labs (Navigator) + collaborating Builder Stewards

**Companion documents:**
- `ACTIVITY_REGISTRY_V1.txt` (AR-001 §3.1, §6) — holds the hash; this holds the payload
- `KYA_SIGNATURE_SPEC.md` (KYA-001) — evidence access keyed to KYA identity
- `REWARD_ROUTER_CONTRACT.md` (RRC-001) — consumes events whose evidence this stores
- `AGENT_IDENTITY_AND_LIABILITY_FRAMEWORK.md` (AIL-001) — legal hold on disputed work
- Issuer Key Runbook (→ `CFL-SPEC-KEY-001`) — recovery-key custody (§10 Q2)
- `PILOT-001_PILOT_SCOPE.md` — Phase-1 scope this spec defers to
- `CUTTLEFISH_SOC2_READINESS.md` (SOC2-001) — confidentiality/processing-integrity controls
