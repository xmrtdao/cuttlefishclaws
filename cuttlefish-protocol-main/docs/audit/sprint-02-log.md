# Sprint 2 — KYA-001 service module

**Branch:** `feat/sprint-02-kya-service` (stacked on `feat/sprint-01-ar001-enum-extension`)
**Spec:** `canon/KYA-001_KYA_SIGNATURE_SPEC.md`
**Status:** complete

## What was done
- `services/cuttlefish-registry/kya.py`:
  - **§2 data model**: `PublicKeyRef`, `PrincipalRef`, `KYABinding` (dataclasses matching the §2 `binding_document` / `PublicKeyRef`).
  - **§2 KYA_ID**: content-addressed — `kya:<actor_kind>:<multibase(SHA-256(canonical_json(binding_document)))>`.
  - **§4.1 signing**: `actor_signing_payload(event)` (event minus `{self_hash, registry_signature, witness_signatures}`), `sign_payload(key, algorithm, payload)` = Sign(key, SHA-256(canonical_json(payload))).
  - **§4.2 verification**: `verify_payload(key_ref, payload, signature)` for `ed25519`, `secp256k1`, `rsa-pss`.
  - **In-memory `KYARegistry`**: `register / get / get_key / rotate / revoke` + `verify_event_signature` enforcing §4.2 checks 1 & 5 (active key in current binding, signature verifies, `signed_at >= issued_at`).
- **Not wired into the AR-001 write path** — that is Sprint 3.
- `requirements.txt` added (fastapi, uvicorn, httpx, cryptography, pytest).
- Used the `cryptography` library. Test keypairs are generated at module load in `tests/test_kya.py` and are clearly named (`TEST_ED_PRIV`, …) — not protocol material.

## Tests
`tests/test_kya.py` — **11 vectors**: deterministic+namespaced KYA_ID; KYA_ID changes on binding change; ed25519 round-trip; secp256k1 round-trip; registry-added fields excluded; tampered payload rejected; wrong key rejected; revoked key rejected; rotated key rejected; algorithm mismatch rejected; unknown KYA_ID / key_id.
`pytest -q` → **62 passed** (was 51; +11).

## Spec interpretations
- **Signed bytes**: `sign(key, SHA-256(canonical_json(payload)))` — for all three algorithms the 32-byte SHA-256 digest is the signed message (ed25519 signs it directly; secp256k1/rsa-pss via `Prehashed(SHA256)`). Consistent and §4.1-literal.
- **rotate/revoke**: mutate key status in place under the registration-time KYA_ID. A full impl supersedes the binding via a `KYA_RENEWAL` event with a new content-addressed KYA_ID (KYA-001 §2 / AR-001 §5.4). Documented inline.

## Placeholders & open decisions
- `TODO(PROGRAMMER)`: `canonical_json` is a JCS-style approximation (sorted keys / compact separators), not a verified RFC 8785 JCS lib. Swap in a vetted JCS implementation for cross-impl signature interop (KYA-001 §4.1 / AR-001 §5.2).
- `TODO(NAVIGATOR)`: confirm the canonical **multibase** code for the KYA_ID subject (used base64url `u`; spec says `multibase(...)` without pinning — base58btc `z` is the common content-addressing choice).
- `TODO(NAVIGATOR/PROGRAMMER)`: KYA_RENEWAL supersession model for rotate/revoke (new KYA_ID per material change) vs. the in-place status model used here.
- `rsa-pss` is implemented but untested in Sprint 2 (vectors cover ed25519 + secp256k1, per the sprint brief).
