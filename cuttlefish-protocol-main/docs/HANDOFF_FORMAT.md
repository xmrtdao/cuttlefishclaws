# Handoff Format — PR Template

Every PR in `cuttlefish-protocol` uses this structure so the Navigator and programmer can review fast.

```markdown
## What
<one sentence: what this change is>

## Spec
Implements: <CFL-SPEC reference, e.g. CFL-SPEC-KYA-001 §4.2 / CFL-NARR-003 §5>

## Scope
**In scope:**
- <what this PR actually does>

**Deferred:**
- <what was intentionally left out, and to which sprint/owner>

## Tests
- Added N tests in <file>.
- They verify: <one line per behaviour, or a short list>
- `pytest -q` → <P passed / F failed / S skipped>

## Placeholders
- `TODO(NAVIGATOR)`: <decision needed>
- `TODO(PROGRAMMER)`: <integration needed>
- (none) if clean.

## Run locally
```
cd services/<service>
python -m pytest -q
uvicorn main:app --port <port>
```

## Programmer: integrate next
- <the real external system this scaffolding expects: KYC vendor, settlement rail, infra, etc.>
```

## Notes

- **One spec concern per PR** where possible. Stacked PRs are fine for sequential sprints; note the base branch.
- **Never weaken an existing test** to make a PR pass. If a test must change (e.g. a new required field), add valid fixtures so it still verifies the same behaviour, and say so explicitly under `## Tests`.
- **Link the sprint log**: `docs/audit/sprint-NN-log.md`.
