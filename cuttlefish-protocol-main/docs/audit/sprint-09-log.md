# Sprint 9 — SRP-001 Stewardship Review lifecycle

**Branch:** `feat/sprint-09-srp-review-lifecycle` (stacked on `feat/sprint-08-council-panels`)
**Spec:** `CAC_Frameworks/STEWARDSHIP_REVIEW_PROCEDURE.md` (SRP-001, fills AIL-001 §7)
**Status:** complete

## What was done
- `services/cuttlefish-registry/srp.py` — the review-proceeding **state machine**:
  `filed → initiated (intake §3) → panel_formed → deliberation_open → deliberation_closed → concluded`, with a `dismissed_at_intake` branch for frivolous/incomplete filings.
- Each transition emits the matching AR-001 event: `STEWARDSHIP_REVIEW_INITIATED / _PANEL_FORMED / _DELIBERATION_OPENED / _DELIBERATION_CLOSED / _OUTCOME`, and `STANDING_ADJUSTED` when a defect is found.
- **Integrates Sprint 8:** `form_panel` staffs the panel via `council.compose_panel` (verifiable random draw), with the **respondent as a matter party** so conflicted candidates recuse.
- Findings: **preponderance** (simple majority) default; **heightened** (unanimous-affirm skeleton) for alleged fraud. Standing adjustment takes effect on issuance (SRP-001 §10.2). Vocabulary kept to the spec's professional-peer-review posture ("Finding", "Proceeding").

## Tests
`tests/test_srp.py` — **14 vectors**: valid intake; each of 4 incomplete-filing dismissals (parametrized); panel formed via council + event; insufficient pool raises; respondent-conflicted candidate excluded; full lifecycle defect → all 6 events in order; no-defect → no STANDING_ADJUSTED; preponderance majority; heightened unanimity; invalid transition; unknown proceeding.
- `services/cuttlefish-registry` → **107 passed** (was 93; +14). pvp 13 / rrc 13 unchanged. **133 total.**

## Placeholders & open decisions
- `TODO(PROGRAMMER)`: wire `_emit` to the signed AR-001 write path; persist proceedings; 72h panel-acceptance window + deemed-recusal; full hearing phases (response, discovery, rebuttal) and appeal-to-Council (SRP-001 §11/§12).
- `TODO(NAVIGATOR)`: exact panel composition (2 Senior + 1 Council + roles, AIL-001 §7.2) vs. the generic `size` used here; heightened-standard per-member affirmation mechanics.
