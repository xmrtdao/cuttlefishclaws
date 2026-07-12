# Sprint 0 — Monorepo setup (backfilled)

**Branch:** committed to `main` (initial commit `86c242b`)
**Status:** complete

## What was done
- Created `cuttlefish-protocol` monorepo at `D:\CuttlefishLabs_Dev\cuttlefish-protocol`.
- `canon/` — 45 canonical docs copied from `00_Current_Work` (CANONICAL_CURRENT spec stack, naming discipline + glossary, `00_CONSTITUTION/`, `CONSTITUTIONAL_ARCHIVE/` with fixity manifest, `CFL-NARR-003`, narrative docs).
- `services/cuttlefish-registry/` — AR-001 service + `trustgraph.py` / `standing.py` / `sgq.py` engines and tests (code only; venv, `*.db`, `__pycache__` gitignored).
- Scaffold: `README.md`, `CODEOWNERS` (`@HansElze`), `.gitignore`.
- Created **private** GitHub repo `Cuttlefish-Labs/cuttlefish-protocol`, pushed `main`.
- 60 files, 10,229 insertions. Tests: 46 passed.

## Environment discovered (Sprint 0 Item 1)
- GitHub CLI authenticated as `HansElze`, admin on `Cuttlefish-Labs`.
- git identity set: David Hans Elze / dvdelze@gmail.com.
- Google Drive: fixed (was signed into a full FrameInfill account; reset + re-signed into the account with space). Working docs synced to `F:\My Drive\Cuttlefish Labs\`.
- Registry + canon source paths confirmed.

## Placeholders & open decisions
- `TODO(NAVIGATOR)`: the monorepo structure (`canon/` + `services/`) was CC's fill-in — the Sprint 0 Item 2 tree was truncated in the prompt. Reorganize if a specific layout was intended.
- `TODO(NAVIGATOR)`: the canon now exists in three places (`D:\…\CANONICAL_CURRENT`, the Drive backup, this repo). Decide the single source of truth before canon is edited again (recommended: the repo).
- Repo is **private**; flip to public only if intended (it holds constitutional + securities-prep-adjacent material).
