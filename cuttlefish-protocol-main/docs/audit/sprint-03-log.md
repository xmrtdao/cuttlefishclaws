# Sprint 3 — Wire KYA-001 signature verification into the AR-001 write path

**Branch:** `feat/sprint-03-kya-wire-writepath` (stacked on `feat/sprint-02-kya-service`)
**Spec:** `canon/KYA-001_KYA_SIGNATURE_SPEC.md` §4.2
**Status:** complete

## What was done
- **`schema.py`** — `EventWriteRequest` gains 4 optional fields: `actor_kya_id`, `actor_signature` (hex), `key_id`, `signed_at` (epoch). Optional so the handler returns precise 400/401/404 rather than pydantic 422.
- **`main.py`**:
  - Module-level `kya_registry = kya.KYARegistry()`.
  - `event_request_signing_payload(req)` — the canonical dict the actor signs (KYA-001 §4.1), built identically by client and server (excludes `actor_signature`).
  - `POST /registry/v1/events` now verifies before writing: `actor_kya_id` present (else **400**) → binding resolves (else **404**) → `actor_signature`+`key_id` present, hex-decodable, key active, `signed_at ≥ issued_at`, signature verifies (else **401** with reason) → existing write path.

## Existing tests modified (signature fixtures added — what & how)
The new requirement is satisfied **centrally**, not by rewriting each test body:
- The **`client` fixture** now registers a test KYA binding (test ed25519 key, clearly named, not protocol material) into `main.kya_registry` and exposes `test_kya_id` / `test_key_id`.
- The **`_write_event` helper** now signs every event with that key (computing the same `event_request_signing_payload` the server uses) unless the caller overrides a signer field.

Because every existing event-writing test goes through `_write_event`, all of them now send a valid signature **without changing what they assert**. Affected (now signed) tests: `test_write_event_returns_event_id_and_hash`, `test_write_event_unknown_activity_type_is_400`, `test_write_event_requires_evidence_hash_or_payload`, `test_write_event_accepts_provided_evidence_hash`, `test_get_event_round_trip`, `test_list_events_filters_by_actor`, `test_list_events_filters_by_activity_type`, `test_list_events_filters_by_section_404`, `test_chain_head_advances`, `test_second_event_chains_from_first`, `test_compliance_report_counts_categories`, and `test_narr003_detection_event_round_trips[*]`. **No assertion was weakened.**

## New tests (6)
`test_kya_valid_signature_accepted` (201), `test_kya_invalid_signature_rejected_401`, `test_kya_missing_actor_kya_id_400`, `test_kya_unknown_actor_kya_id_404`, `test_kya_revoked_key_rejected_401`, `test_kya_signed_at_before_key_issued_at_401`.

## Tests
`pytest -q` → **68 passed** (was 62; +6).

## Placeholders & open decisions
- `TODO(NAVIGATOR)`: decide whether the actor signature must cover `evidence_hash` (it is out of the Sprint-3 signed payload to keep client/server symmetric before server-side evidence hashing). Recommend yes once the evidence flow is fixed.
- `TODO(PROGRAMMER)`: `kya_registry` is process-local in-memory — back it with persistent KYA storage and the PVP-issued bindings (Sprint 4).
- `TODO(NAVIGATOR)`: §4.2 checks 2 (principal `binding_proof` verifies) and 3 (witness signatures for consensus events) are **not** enforced on the write path yet — only check 1 (actor key) + check 5 (signed_at). Sequence the remaining checks.
