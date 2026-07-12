# Sprint 1 — AR-001 enum extension (CFL-NARR-003 §5)

**Branch:** `feat/sprint-01-ar001-enum-extension` (stacked on `feat/sprint-005-workflow-docs`)
**Spec:** `canon/CFL-NARR-003_TWO-LAYER_TRUSTGRAPH_ARCHITECTURE.md` §5
**Status:** complete

## What was done
- Added 5 values to `ActivityType` in `services/cuttlefish-registry/storage.py`, per CFL-NARR-003 §5:
  `SOCIAL_ENGINEERING_DETECTED`, `IDENTITY_FISHING_DETECTED`, `COORDINATED_PROBING_DETECTED`, `TRUST_MANIPULATION_DETECTED`, `IDENTITY_INCONSISTENCY_DETECTED`.
- **Additive only.** No existing enum value changed/removed. **Not** wired to TG-001 score deltas (future Navigator ratification per CFL-NARR-003 §7.2).
- Used the SCREAMING_SNAKE value convention already in `storage.py` (e.g. `KYA_RENEWAL = "KYA_RENEWAL"`), which matches the Sprint 1 instruction. (Note: CFL-NARR-003 §5's illustrative snippet showed lowercase string values; the existing code convention is uppercase — followed the code + the sprint instruction. Flagged below.)
- Added a parametrized round-trip test in `tests/test_api.py` (5 items): each new type is accepted (201), and round-trips via GET and the `activity_type` list filter.

## Tests
`pytest -q` → **51 passed** (was 46; +5).

## Spec interpretations
- **Enum value casing:** CFL-NARR-003 §5 code block shows `= "social_engineering_detected"` (lowercase), but every existing `ActivityType` uses uppercase string values. Followed the existing-code convention + the Sprint 1 prompt (uppercase). If the canon intends lowercase wire values, that's a one-line change — but it would diverge from all other event types. → see placeholder.

## Placeholders & open decisions
- `TODO(NAVIGATOR)`: confirm enum **string-value casing** for the 5 detection types — uppercase (matches all existing `ActivityType` values, used here) vs. lowercase (matches the CFL-NARR-003 §5 illustrative snippet). Recommend uppercase for consistency.
- `TODO(NAVIGATOR)`: TG-001 score deltas for these 5 types are intentionally unassigned (CFL-NARR-003 §7.2) — ratify values when ready.
