# Issuer Key Runbook v1.1

**Document ID:** CFL-SPEC-KEY-001
## Cuttlefish Labs Multi-Sig Issuer Key Operations

**Issuer:** Cuttlefish Labs
**Version:** 1.1 (promoted from the June-26 bundle v1.0 per CFL-DECISION-001 D-7; canon references updated)
**Status:** Draft
**Classification:** Internal — Restricted
**Date:** 2026-06-27
**Companion to:** `CAC_PROTOCOL_CANONICAL_SPEC_v5.md` (CFL-SPEC-CAC-005 §10 chains/keys), KYA-001 (signature keys), EVS-001 (evidence recovery-key custody)

---

## 0. Purpose

This runbook defines the operational procedure for the **Cuttlefish Labs Issuer Master Key** — the root of trust for all CAC credentials. Compromise of this key would invalidate the entire CAC Protocol's trust assumptions. This document specifies key generation, custody, signing ceremonies, rotation, and compromise response.

This is an internal operations document. It is referenced from the public CAC Protocol canonical spec (CAC-005) but its details are not for public distribution.

> **Scope note (v1.1):** the **evidence recovery-key** in EVS-001 §10 Q2 (for `compliance`/`legal_hold` encrypted evidence) is a **subordinate key under this ceremony**, not a separate trust root. Its M-of-N threshold for evidence recovery (vs. issuer signing) is an open item to be specified here as EVS reaches Phase 2.

---

## 1. Key Hierarchy

```
┌─────────────────────────────────────────────────────┐
│  Issuer Master Key (offline, multi-sig 3-of-5)      │
│  Purpose: signs operational subkeys ONLY             │
│  Use frequency: ≤2× per year (rotation events)       │
└──────────────────┬──────────────────────────────────┘
                   │ signs
                   ▼
┌─────────────────────────────────────────────────────┐
│  Issuer Operational Key (online HSM, 2-of-3)         │
│  Purpose: signs VCs, SCP03 master keys, attestations │
│  Use frequency: daily                                │
│  Rotation: every 90 days                             │
└──────────────────┬──────────────────────────────────┘
                   │ derives
                   ▼
┌─────────────────────────────────────────────────────┐
│  Per-card SCP03 keys (HSM-derived, per-card)         │
│  Purpose: secure channel to individual cards         │
│  Use frequency: at personalization + lifecycle ops   │
└─────────────────────────────────────────────────────┘
```

**Why two layers:** the Master Key is the slowest, highest-assurance key. It signs operational subkeys but is otherwise dormant. If the operational key is compromised, the master can revoke and re-issue without rebuilding the root of trust. If the master is compromised, the entire protocol must be re-anchored — this is the worst case and the layering exists precisely to make it almost impossible.

---

## 2. Master Key

### 2.1 Generation Ceremony

**Performed once at protocol genesis.** Re-performed only if Master Key is compromised or scheduled rotation occurs (every 5 years).

#### 2.1.1 Participants
- 5 Key Holders (one each):
  - CEO / Founder (David Hans Elze)
  - CTO or technical co-lead
  - Independent board director
  - External security advisor (not employed by Cuttlefish Labs)
  - Custodian agent (institutional partner — TBD)

#### 2.1.2 Geographic & Organizational Distribution
- No 2 Key Holders may reside in the same legal jurisdiction
- No 2 Key Holders may be employed by the same organization (except CEO + CTO exception during Phase 1)
- All 5 must be physically present at the genesis ceremony

#### 2.1.3 Hardware
- 5 × YubiHSM 2 (separate units, sequentially purchased from authorized resellers)
- 1 × air-gapped laptop (purchased anonymously, never connected to internet, destroyed after ceremony)
- 1 × printer for paper backups (no network capability)
- Faraday-bagged transport for HSMs

#### 2.1.4 Ceremony Steps
1. All 5 Holders verify YubiHSM 2 firmware version + serial numbers match procurement records
2. Air-gapped laptop boots from verified live-USB Debian image (SHA-256 verified by all 5)
3. EC P-384 key pair generated on-laptop using `openssl` with `/dev/urandom` + hardware entropy beacon
4. Public key recorded; private key split using Shamir's Secret Sharing (5 shares, 3-of-5 threshold)
5. Each share imported into one YubiHSM 2 under a Holder-chosen PIN
6. Each share also printed as QR code + numeric backup on paper (Holder-only access)
7. Air-gapped laptop wiped (full disk overwrite) and physically destroyed
8. Each Holder leaves with: 1 YubiHSM 2 + 1 paper backup, both in separate sealed evidence bags
9. Notarized ceremony log signed by all 5 Holders + independent witness

#### 2.1.5 Storage Requirements
- YubiHSM 2: in bank safe deposit box or equivalent (Holder's choice within insurance limits)
- Paper backup: in physically separate location from YubiHSM 2 (different city if possible)
- Annual proof-of-possession ceremony required from all 5 Holders

### 2.2 Master Key Signing Ceremony

Performed only for:
- Initial operational key issuance
- Operational key rotation (every 90 days)
- Operational key emergency revocation
- Master key rotation (every 5 years)

#### 2.2.1 Convening
- Minimum 3 of 5 Holders physically present
- Convening location decided ≤72 hours before by majority vote
- Independent witness present (not a Key Holder)

#### 2.2.2 Procedure
1. Each present Holder verifies their YubiHSM 2 has not been tampered with (serial, seal, expected challenge response)
2. Subject of signing (operational key public component or rotation payload) verified by all present Holders
3. Each Holder signs the payload using their share
4. Shares combined via Lagrange interpolation (requires 3 minimum)
5. Resulting signature verified against published Master public key
6. Signed payload published to:
   - cuttlefishlabs.io/issuer/master-signatures (timestamped)
   - On-chain anchor on Base (root hash of signature log)
7. Ceremony log notarized + signed

### 2.3 Master Key Loss Scenarios

| Lost / Compromised | Response |
|---|---|
| 1 share lost (Holder dies, share destroyed) | No immediate action. At next ceremony, reissue from recovered paper backup; if paper backup also lost, perform 3-of-4 ceremony and replace lost share |
| 2 shares lost | Emergency ceremony with remaining 3; one Holder elected to receive replacement share; full audit |
| 3 shares lost | **Worst case.** Master key cannot be reconstructed. Initiate full protocol re-anchoring: new genesis ceremony, publish migration plan, issue new credentials to all active CACs, deprecate old root after 90-day overlap period |
| 1 share compromised (key extracted) | Compromised Holder's share invalidated via Master signature; remaining 4 perform threshold operation; share regenerated |
| 3+ shares compromised | Assume full Master key compromised. Emergency protocol re-anchoring per procedure §5 |

---

## 3. Operational Key

### 3.1 Hardware
- 3 × AWS CloudHSM cluster nodes (us-east-1, us-west-2, eu-west-1)
- 2-of-3 threshold signing via AWS CloudHSM client SDK
- Backup of HSM keys is itself encrypted by Master Key (recoverable only via §2.2 ceremony)

### 3.2 Operational Use
| Operation | Authorization |
|---|---|
| Issue new VC | Automated (FastAPI service with mTLS to CloudHSM cluster) |
| Sign SCP03 master key | Automated per-card during personalization |
| Sign batch attestation | Manual approval by 1 engineer + automated rate limit |
| Update revocation list root | Automated when status list changes, with 5-minute delay window for review |

### 3.3 Rate Limits
- VC issuance: max 1,000 per hour (alert at 800)
- SCP03 derivation: max 100 per minute (alert at 80)
- Revocation list root update: max 4 per hour (alert at 3)

### 3.4 Rotation Schedule
- **Every 90 days** scheduled rotation
- Master Key ceremony signs new operational public key
- 7-day overlap window where both old and new operational keys are valid
- Old key revoked at end of overlap

### 3.5 Operational Key Logs
- Every signing operation logged to immutable append-only log (AWS QLDB)
- Log hash anchored to Base every hour
- Logs reviewed weekly by security lead

---

## 4. Per-Card SCP03 Keys

### 4.1 Derivation
- HKDF-SHA256 from operational key root + card serial number + role byte (ENC / MAC / DEK)
- Never stored at rest; derived on-demand during card lifecycle operations

### 4.2 Use
- Card personalization (initial provisioning)
- Lifecycle commands (SUSPEND, RESUME, KILL, ROTATE_KEY)
- Cached score updates

### 4.3 Compromise Impact
- Single-card compromise: revoke that card only via status list, mass-issue replacement to other affected scope (typically none — derivation per-card)
- Operational key compromise: all derived SCP03 keys compromised; replace via §5

---

## 5. Compromise Response Procedures

### 5.1 Operational Key Compromise (suspected)

**Severity:** High. Recoverable in <72 hours.

1. **T+0** Detection (anomalous signing pattern, HSM intrusion alert, insider report)
2. **T+15min** Security lead initiates incident: pause all automated VC issuance via kill switch
3. **T+1hr** Verify scope: which keys, which time window, which credentials potentially compromised
4. **T+4hr** Convene 3 Master Key Holders for emergency ceremony
5. **T+24hr** Master Key Holders sign revocation of compromised operational key + new operational key
6. **T+24hr** All credentials issued during suspected compromise window flagged in status list for re-verification
7. **T+48hr** Re-issuance ceremony for affected cards
8. **T+72hr** Post-mortem published (internal); public security advisory if customers affected

### 5.2 Master Key Share Compromise (1 share)

**Severity:** Medium. No immediate user-facing impact.

1. **T+0** Detection
2. **T+1hr** Affected Holder confirms compromise; remaining 4 notified
3. **T+1 week** Convene 3-of-4 remaining Holders; sign invalidation of compromised share
4. **T+2 weeks** Issue replacement share to a Holder (new Holder or replacement person for original)
5. **T+30 days** Annual proof-of-possession ceremony brought forward to verify all other shares uncompromised

### 5.3 Master Key Full Compromise (3+ shares)

**Severity:** Critical. Entire protocol re-anchoring.

1. **T+0** Detection
2. **T+1hr** Public communication: pause all new CAC issuance
3. **T+24hr** Genesis ceremony for new Master Key (§2.1)
4. **T+1 week** New operational key issued under new Master
5. **T+1 week** Migration plan published: all active CACs must re-onboard within 90 days
6. **T+30 days** Bridge service: old credentials and new credentials both honored during migration
7. **T+90 days** Old Master deprecated; legacy credentials no longer valid

---

## 6. Annual Audit Requirements

### 6.1 Proof-of-Possession Ceremony
- All 5 Master Key Holders demonstrate possession of YubiHSM 2 + paper backup
- Sign a known challenge as group; signature published
- Tamper seals on hardware verified
- Held annually, on anniversary of genesis ceremony

### 6.2 External Security Audit
- Independent firm audits operational key handling annually
- Scope: HSM configuration, signing logs, incident response procedures, access control
- Findings published in redacted form to cuttlefishlabs.io/security

### 6.3 Penetration Testing
- Quarterly tests against the operational signing service
- Red team rotation; no firm engaged 2 years in a row
- Findings drive operational key procedure updates

---

## 7. Access Control

### 7.1 Roles
| Role | Authority |
|---|---|
| Master Key Holder | One Master share; participates in §2.2 ceremonies |
| Security Lead | Approves §5 incident response; initiates emergency procedures |
| Operations Engineer | Operates online signing service; cannot initiate Master ceremonies |
| Auditor | Read-only access to signing logs; no signing authority |
| CEO | Has Master share + can declare incident; cannot unilaterally sign |

### 7.2 Separation of Duties
- No single person can issue a VC unilaterally (HSM requires mTLS auth + signed request from FastAPI service + within rate limit)
- No single person can rotate the Master Key (requires 3 Holders)
- No single person can authorize an emergency procedure (requires Security Lead + 1 other officer)

---

## 8. Insurance & Legal

### 8.1 Cyber Insurance
- Coverage minimum: $5M for cryptographic key incidents
- Reviewed annually; scales with active CAC count (target: $1 per active CAC, capped at $50M)

### 8.2 Legal Framework
- Master Key Holder Agreement signed by each Holder
- Specifies fiduciary duty, response obligations, indemnification scope
- Reviewed by counsel annually

### 8.3 Public Disclosure
- Security advisories published within 7 days of confirmed incidents
- Following responsible disclosure window for any reporter-found vulnerabilities (90 days standard)

---

## 9. Open Items

1. **Custodian agent (5th Key Holder).** Institutional partner not yet selected. Candidates: Coinbase Custody, BitGo, Fireblocks. Decision required before genesis ceremony.
2. **AWS CloudHSM vs YubiHSM cluster for operational.** Current spec uses AWS; reviewing self-hosted YubiHSM as alternative for lower vendor lock-in.
3. **Quantum-resistance plan.** P-384 chosen for compatibility. Migration plan to PQ signatures (Dilithium or equivalent) deferred to 2028 protocol upgrade.
4. **Geographic exclusions.** Whether to exclude specific jurisdictions for Holder residency (e.g., countries with key disclosure laws). Currently advisory; needs hard rule.
5. **Insurance coverage scaling.** Per-CAC insurance pricing model not yet negotiated.

---

*End of Issuer Key Runbook v1.0*
*This document is classified Internal — Restricted. Do not distribute externally.*
