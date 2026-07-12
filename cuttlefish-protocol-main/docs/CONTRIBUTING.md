# Contributing — Cuttlefish Protocol

Workflow rules for the `cuttlefish-protocol` monorepo.

## Roles

| Role | Who | Responsibility |
|---|---|---|
| **Navigator** | David Hans Elze | Owns the canon. Sole merge authority. Resolves placeholders and naming decisions. |
| **Programmer** | `xmrtsolutions` | Review access. Integrates external systems, infra, frontend, settlement rails. |
| **CC** | Claude Code | Drafts spec-aligned scaffolding and tests on feature branches. Never merges. |

## Hard rules

1. **`/canon/` is read-only** except by explicit Navigator instruction. It is the source of truth; code conforms to it, not the other way around.
2. **Every code change goes through a feature branch + PR.** No direct commits to `main`.
3. **`main` is protected.** No direct pushes. (Enable branch protection in repo settings once review access is set.)
4. **PRs require Navigator approval to merge.** The programmer (`xmrtsolutions`) has review access; **only the Navigator merges.**
5. **Naming follows `canon/NAME_REGISTRY.md` and `canon/CFL-GLOSSARY-001_CANONICAL_GLOSSARY.md` exactly.** Canonical names are name-locked. Do not rename, "align," or "clean up" a canonical name. If a name looks wrong, flag it — do not edit it.
6. **No new canonical vocabulary** is introduced in code without Navigator ratification.

## Division of labour

- **CC** produces: spec-aligned service skeletons, deterministic engines, test vectors, scaffolding, audit logs. CC builds against the canon and flags every assumption.
- **Programmer** produces: real external integrations (KYC/IDV, settlement, on-chain), infrastructure (deploy, CI/CD, secrets), frontend, and anything touching production money or PII.

## Placeholders

Every placeholder, stub, or assumption is flagged inline and logged:

- `TODO(NAVIGATOR)` — needs a Navigator decision (naming, threshold values, offering structure, policy).
- `TODO(PROGRAMMER)` — needs the programmer to integrate a real external system (KYC vendor, settlement, infra).

Every placeholder is **also** listed in that sprint's audit log under `## Placeholders & open decisions`, and consolidated in `docs/audit/overnight-pass-summary.md`.

## Branch naming

`feat/sprint-NN-<short>` for sprint work; `feat/sprint-NN-<short>-partial` if committed incomplete (Navigator decides whether to continue).

## Definition of done (per sprint)

- Code matches the cited `CFL-SPEC` / canon section.
- Tests pass (`pytest -q`) — existing tests unchanged unless the sprint explicitly authorizes it.
- Sprint audit log written, placeholders flagged.
- Branch pushed, PR opened (not merged).
