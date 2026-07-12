# Sprint 0.5 — Backfill workflow docs

**Branch:** `feat/sprint-005-workflow-docs` (from `main`)
**Spec:** workflow/process (no protocol spec)
**Status:** complete

## What was done
- `docs/CONTRIBUTING.md` — roles (Navigator / Programmer `xmrtsolutions` / CC), hard rules (canon read-only, feature-branch+PR, main protected, Navigator-only merge, name-lock), division of labour, placeholder convention (`TODO(NAVIGATOR)` / `TODO(PROGRAMMER)`).
- `docs/HANDOFF_FORMAT.md` — the PR template (what / spec / scope / tests / placeholders / run / programmer-next).
- `docs/ARCHITECTURE.md` — one-page protocol stack from CFL-NARR-003 + per-service folder table.
- `docs/audit/sprint-00-log.md` — backfilled Sprint 0.
- `docs/audit/overnight-pass-summary.md` — created; checkpoints appended through the pass.

## Tests
- No code changed. `pytest -q` in `services/cuttlefish-registry` → **46 passed** (baseline preserved).

## Placeholders & open decisions
- `TODO(NAVIGATOR)`: confirm the programmer GitHub handle is `xmrtsolutions` and grant review access on the repo (CC cannot add collaborators without it being intended).
- `TODO(PROGRAMMER)`: enable branch protection on `main` (no direct pushes, require PR + approval) — CC documented the rule but did not change repo settings.

## Notes
- Branch protection and collaborator access are repo-settings changes left for the Navigator/programmer; CC only documented the intended rules.
