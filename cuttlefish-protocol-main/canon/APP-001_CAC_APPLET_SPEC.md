# CAC Applet Specification v1.1

**Document ID:** CFL-SPEC-APP-001
## Java Card Applet — Contractor Brief

**Issuer:** Cuttlefish Labs
**Version:** 1.1 (promoted from the June-26 bundle v1.0 per CFL-DECISION-001 D-7; tier names + credential fields aligned to canon)
**Status:** Ready for RFQ
**Date:** 2026-06-27
**Companion to:** `CAC_PROTOCOL_CANONICAL_SPEC_v5.md` (CFL-SPEC-CAC-005 §8, credential schema), KYA-001, KEY-001
**Conforms to:** CFL-DECISION-001 (tiers Developer/Studio/Enterprise/Anchor; snake_case credential fields; `did:cardano` agent DID; dual `soul_hash`/`constitution_hash` binding)

> **v1.1 alignment note:** on-card persistent-object labels and the personalization example below use the canonical **snake_case** credential field names of CAC-005 §8 (`agent_did`, `operator`, `constitution_hash`, `soul_hash`), the **did:cardano** agent DID method, and the **Developer/Studio/Enterprise/Anchor** tier enum. The v1.0 (camelCase / `did:key` / Resident-Builder-Sovereign-Anchor) forms are superseded.

---

## 0. Purpose

This document is the contractor brief for the **custom CAC Java Card applet** that runs on NXP JCOP 4 SECID cards. It is suitable for circulation to applet development houses (Fime, Intercede, Bell ID, IDEMIA, or equivalent) for fixed-price quotation.

Pilot 100 cards will use a preloaded PIV applet. This document defines the v1.0 applet for the 500-card production run and all subsequent batches.

---

## 1. Target Platform

| Item | Spec |
|---|---|
| Chip | NXP JCOP 4 SECID |
| Java Card version | 3.0.5 Classic |
| GlobalPlatform | 2.3 |
| Card OS | NXP JCOP 4 (P71D321) |
| Interface | Dual (ISO 14443 Type A + ISO 7816 contact) |
| Crypto | ECDSA P-256 (NIST), SHA-256, AES-128/256, HMAC |
| Available EEPROM | ≥80 KB (applet must fit in ≤32 KB) |
| Card vendor | CardLogix (https://www.cardlogix.com/product/nxp-jcop-4-java-card-3-0-5-classic/) |

---

## 2. Applet Identification

| Item | Value |
|---|---|
| Applet AID | `A0 00 00 06 47 75 74 74 6C 65 66 69 73 68 01` (proposed — "Cuttlefish" in ASCII with version byte) |
| Package AID | `A0 00 00 06 47 75 74 74 6C 65 66 69 73 68` |
| RID | `A0 00 00 06 47` (Cuttlefish Labs registration pending — placeholder) |
| Application name | `CAC` |

> **Open item:** Register RID with ISO 7816-5 authority before mainnet launch. Placeholder RID acceptable for pilot.

---

## 3. Persistent Data Objects

All objects are written during personalization (post-issuance update via secure channel, GlobalPlatform SCP03).

| Tag | Object | Type | Size | Mutability |
|---|---|---|---|---|
| `01` | `agent_did` | UTF-8 (`did:cardano:<hash>`) | ≤256 bytes | issuer-write, read-public |
| `02` | `operator` | UTF-8 (Ethereum address) | ≤256 bytes | issuer-write, read-public |
| `03` | `tier` | uint8 enum | 1 byte | issuer-write, read-public |
| `04` | `constitution_hash` | bytes32 | 32 bytes | issuer-write, read-public |
| `09` | `soul_hash` | bytes32 | 32 bytes | issuer-write, read-public |
| `05` | `issued` | uint32 (unix) | 4 bytes | issuer-write, read-public |
| `06` | `expires` | uint32 (unix) | 4 bytes | issuer-write, read-public |
| `07` | `issuer_signature` | DER ECDSA P-256 | ≤72 bytes | issuer-write, read-public |
| `08` | `status` | UTF-8 URL + uint32 | ≤512 bytes | issuer-write, read-public |
| `10` | `agentPrivKey` | EC P-256 private key | 32 bytes | on-card-generated, **non-exportable** |
| `11` | `agentPubKey` | EC P-256 public key | 65 bytes uncompressed | derived, read-public |
| `20` | `cachedTrustScore` | uint8 | 1 byte | backend-write via SCP03 |
| `21` | `cachedScoreTimestamp` | uint32 (unix) | 4 bytes | backend-write via SCP03 |
| `30` | `pinTryCounter` | uint8 | 1 byte | applet-managed |
| `31` | `pinValue` | hashed bytes | 32 bytes | operator-set (Enterprise+ only) |
| `40` | `lifecycleState` | uint8 enum | 1 byte | applet-managed |
| `41` | `signatureCounter` | uint32 | 4 bytes | applet-managed |

### 3.1 Tier Enum (object `03`)
- `0x01` Developer
- `0x02` Studio
- `0x03` Enterprise
- `0x04` Anchor

### 3.2 Lifecycle State Enum (object `40`)
- `0x01` ISSUED — provisioned but not activated
- `0x02` ACTIVE — operational
- `0x03` SUSPENDED — score below threshold; signing blocked, read still allowed
- `0x04` TERMINATED — irreversible; all crypto operations blocked

---

## 4. APDU Command Set

All commands use CLA = `0x80` (proprietary). All responses follow ISO 7816-4 status word conventions.

### 4.1 SELECT
| Field | Value |
|---|---|
| CLA / INS / P1 / P2 | `00 A4 04 00` |
| Data | Applet AID |
| Response | FCI template + `9000` |

Standard Java Card SELECT — included for completeness.

### 4.2 GET_DID
| Field | Value |
|---|---|
| CLA / INS / P1 / P2 | `80 B0 00 00` |
| Lc | `00` |
| Data | (none) |
| Le | `00` |
| Response | TLV: `01 LL <agent_did> 02 LL <operator>` + `9000` |
| Lifecycle | ACTIVE, SUSPENDED |

### 4.3 GET_TIER
| Field | Value |
|---|---|
| CLA / INS / P1 / P2 | `80 B1 00 00` |
| Response | 1 byte tier enum + `9000` |
| Lifecycle | any |

### 4.4 GET_RULESET_HASH
| Field | Value |
|---|---|
| CLA / INS / P1 / P2 | `80 B2 00 00` |
| Response | 32 bytes + `9000` |
| Lifecycle | any |

### 4.5 GET_PUBLIC_CREDENTIAL
| Field | Value |
|---|---|
| CLA / INS / P1 / P2 | `80 B3 00 00` |
| Response | Concatenated TLV of objects `01`–`08`, `11` + `9000` |
| Lifecycle | any |

Returns the full public credential payload for off-card verification.

### 4.6 SIGN_CHALLENGE
| Field | Value |
|---|---|
| CLA / INS / P1 / P2 | `80 B4 P1 00` where P1 = `0x00` (no PIN) or `0x01` (PIN required) |
| Lc | length of challenge |
| Data | reader-supplied nonce (16–64 bytes) |
| Le | `00` |
| Response | DER-encoded ECDSA P-256 signature over `SHA256(agent_did ‖ challenge ‖ signatureCounter)` + 4-byte counter value + `9000` |
| Lifecycle | ACTIVE only |
| Errors | `6982` PIN required, `6983` PIN blocked, `6986` lifecycle not ACTIVE, `6A88` no challenge |

Signature counter increments and is returned with every signature. Replay prevention is enforced backend-side by rejecting non-monotonic counters per DID.

**For Enterprise and Anchor tier cards:** P1 = `0x01` is mandatory. PIN must have been verified via VERIFY_PIN in the current session.

### 4.7 VERIFY_PIN
| Field | Value |
|---|---|
| CLA / INS / P1 / P2 | `80 20 00 00` |
| Lc | length of PIN |
| Data | PIN (4–8 digits, ASCII) |
| Response | `9000` on success; `63CX` on failure where X is remaining tries; `6983` if blocked |
| Lifecycle | ACTIVE, SUSPENDED |

Try counter: 5 attempts. Block on exhaustion. Unblock requires SCP03 issuer command (§4.11).

### 4.8 GET_CACHED_SCORE
| Field | Value |
|---|---|
| CLA / INS / P1 / P2 | `80 B6 00 00` |
| Response | 1 byte score + 4 byte timestamp + `9000` |
| Lifecycle | any |

### 4.9 UPDATE_CACHED_SCORE (SCP03-protected)
| Field | Value |
|---|---|
| CLA / INS / P1 / P2 | `84 B7 00 00` (CLA `0x84` = secure messaging) |
| Lc | varies |
| Data | SCP03-encrypted: 1 byte score + 4 byte timestamp |
| Response | `9000` |
| Lifecycle | ACTIVE, SUSPENDED |

Requires established GlobalPlatform SCP03 secure channel with backend issuer key.

### 4.10 ROTATE_KEY (SCP03-protected)
| Field | Value |
|---|---|
| CLA / INS / P1 / P2 | `84 C0 00 00` |
| Data | SCP03-encrypted rotation request |
| Response | new public key (65 bytes uncompressed) + `9000` |
| Lifecycle | ACTIVE only |

Card generates new EC P-256 key pair on-card. Old private key is overwritten. New public key returned for off-card VC re-issuance.

### 4.11 KILL (SCP03-protected)
| Field | Value |
|---|---|
| CLA / INS / P1 / P2 | `84 CE 00 00` |
| Response | `9000` |
| Lifecycle | any → TERMINATED |

Irreversible. All subsequent signing operations return `6986`. Read operations on public objects (`01`–`08`, `11`) still succeed for forensics.

### 4.12 SUSPEND / RESUME (SCP03-protected)
| Field | Value |
|---|---|
| SUSPEND CLA / INS / P1 / P2 | `84 CC 00 00` |
| RESUME CLA / INS / P1 / P2 | `84 CD 00 00` |

Transitions between ACTIVE and SUSPENDED.

---

## 5. Security Model

### 5.1 Key Hierarchy
```
Issuer Master Key (off-card, HSM-backed, multi-sig 3-of-5)
   ├── SCP03 static keys (ENC, MAC, DEK) — per card
   └── Issuer signature key (signs issuerSignature object 07)

Card-resident keys:
   ├── agentPrivKey (object 10) — non-exportable
   └── SCP03 derived session keys — ephemeral
```

### 5.2 Access Control Matrix
| Object | Read | Write |
|---|---|---|
| Public credential (01–08, 11) | any reader | issuer SCP03 |
| Private key (10) | NEVER | on-card generation only |
| Cached score (20, 21) | any reader | issuer SCP03 |
| PIN value (31) | NEVER | operator (with current PIN or issuer SCP03 reset) |
| Lifecycle (40) | any reader | applet-managed + issuer SCP03 |

### 5.3 Side-Channel Resistance
- Constant-time ECDSA implementation required (Java Card platform provides this; verify in test)
- Power-analysis countermeasures inherited from JCOP 4 hardware
- No optimization paths that branch on key material

---

## 6. Personalization Data Format

Contractor must provide a personalization script (GlobalPlatform Pro / `gp.exe` compatible) that consumes a per-card JSON payload:

```json
{
  "serial": "CAC-2026-000001",
  "agent_did": "did:cardano:1a3b...",
  "operator": "0xAbC1...",
  "tier": "studio",
  "constitution_hash": "0x3a7f...",
  "soul_hash": "0x9e2d...",
  "issued": 1735689600,
  "expires": 1767225600,
  "issuer_signature": "0x304502...",
  "statusListUrl": "https://cuttlefishlabs.io/status/2026-q1",
  "statusListIndex": 42,
  "pinRequired": true,
  "initialPin": "0000"
}
```

Script must:
1. Establish SCP03 with the card
2. Install and select the CAC applet
3. Write all persistent objects from JSON
4. Trigger on-card EC P-256 key generation
5. Read back `agentPubKey`, append to a personalization audit log
6. Set lifecycle to ISSUED
7. Output success/failure + audit hash

---

## 7. Performance Requirements

| Operation | Max latency |
|---|---|
| SELECT + GET_PUBLIC_CREDENTIAL | 200 ms |
| SIGN_CHALLENGE (no PIN) | 300 ms |
| SIGN_CHALLENGE (PIN-gated, post-VERIFY) | 350 ms |
| VERIFY_PIN | 100 ms |
| Full personalization | ≤30 seconds per card |

NFC range: card must complete SIGN_CHALLENGE within ISO 14443 stable field at 5–8 cm from reader.

---

## 8. Test Vectors

Contractor must deliver test vectors covering:
- Known-answer ECDSA P-256 signatures (RFC 6979 deterministic mode preferred for testability)
- Round-trip personalization → read-back → verify
- Lifecycle transitions (ISSUED → ACTIVE → SUSPENDED → ACTIVE; ACTIVE → TERMINATED)
- PIN block / unblock
- SCP03 session establishment with NXP default keys + custom keys
- Replay rejection (counter regression)
- Boundary cases: empty challenge, oversized challenge, expired credential

---

## 9. Deliverables

| # | Item |
|---|---|
| 1 | CAP file (applet binary) for JCOP 4 P71D321 |
| 2 | Source code (Java) with build instructions, MIT or contractor-default license |
| 3 | Personalization script (GP Pro / Python with pyscard) |
| 4 | Test harness + test vector results |
| 5 | API documentation (every APDU command, error codes, examples) |
| 6 | Security review document (threat model, side-channel analysis, code audit notes) |
| 7 | One-week support window post-delivery for integration questions |
| 8 | Reference reader integration code (Python pyscard + Node.js nfc-pcsc) |

---

## 10. Acceptance Criteria

Applet ships when all of the following hold:

1. All APDU commands from §4 pass test vectors from §8 on real JCOP 4 hardware (not simulator)
2. Personalization completes in ≤30 seconds per card on ACR122U
3. Lifecycle transitions are correct and irreversible where specified
4. Non-exportable private key verified by attempting GET_DATA on object `10` (must return `6A88`)
5. SCP03 session establishment works with backend test harness using Cuttlefish issuer keys
6. Side-channel review passes (independent reviewer acceptable)
7. CAP file size ≤32 KB

---

## 11. Timeline & Pricing Expectations

| Phase | Duration | Notes |
|---|---|---|
| Spec review + Q&A | 1 week | Contractor reviews this doc, sends clarifying questions |
| Development | 4–6 weeks | Includes unit tests + KAT vectors |
| Integration testing | 1 week | Against Cuttlefish backend |
| Security review | 1 week | Can run parallel to integration |
| **Total** | **6–9 weeks** | |

Fixed-price quote requested. Hourly fallback acceptable with capped not-to-exceed.

---

## 12. Contractor Candidates

| Vendor | Strengths | Notes |
|---|---|---|
| Fime | GlobalPlatform expertise; large-scale issuance | Likely most expensive |
| Intercede | MyID platform; PIV experience | PIV familiarity helps |
| Bell ID | Card lifecycle management background | Now part of Rambus |
| IDEMIA | Tier-1 issuer; deep applet bench | Overkill for pilot |
| Smaller specialists | Faster, cheaper | Higher delivery risk |

RFQ will be sent to top 3 plus 1 smaller specialist. Selection criteria: price, prior JCOP 4 work, willingness to deliver source code under non-restrictive license.

---

## 13. Open Items

1. RID registration with ISO 7816-5 authority
2. PIN policy finalization (currently: required for Enterprise + Anchor only)
3. Whether to include FIDO2/WebAuthn applet alongside CAC applet on same card (deferred to v1.1)
4. Offline operation: should card cache a recent attestation that allows local authorization without backend reachability? (deferred to v2.0)

---

*End of CAC Applet Specification v1.0*
