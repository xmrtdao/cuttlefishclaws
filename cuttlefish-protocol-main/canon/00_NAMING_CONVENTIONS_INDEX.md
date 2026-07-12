# Cuttlefish Labs — Naming Conventions

**Status:** AUTHORITATIVE. This folder is the source of truth for what things are named.
**Owner:** David Hans Elze, Navigator. **Only the Navigator changes a canonical name.**
**Created:** 2026-06-27 (after an agent renamed locked persona names without authorization — see §3).

---

## 1. THE PRIME DIRECTIVE (read this first, every time)

> **Names in this folder are NAME-LOCKED. Do not rename, "align," "modernize," "clean up," "fix," or "improve" any canonical name — ever — without explicit, in-the-moment direction from the Navigator.**

This applies to every agent, contractor, programmer, and AI assistant (Claude included). If a name *looks* inconsistent, wrong, retired, or redundant: **flag it and ask. Do not change it.** Years of brand, product, and identity work live in these names. A "tidy-up" rename can silently break investor docs, agent identities, on-chain references, and the site.

When in doubt: **the name stays. You ask.**

---

## 2. The files in this folder

| File | What it is |
|---|---|
| **`CFL-GLOSSARY-001_CANONICAL_GLOSSARY.md`** | **THE SINGLE SOURCE OF TRUTH** — the Navigator's authored canonical glossary of every term, with its Reserved Words list and Glossary Governance Rule. Read this first. |
| `00_NAMING_CONVENTIONS_INDEX.md` | This file — the prime directive + change control |
| `NAME_REGISTRY.md` | Operational companion: locked names grouped by category (defers to the glossary where they overlap) |
| `RETIRED_BANNED_AND_GOTCHAS.md` | Operational companion: retired/banned names + the homonym traps (e.g. why "Builder" appears in 3 legit places and must never be collapsed) |

Where any companion file and `CFL-GLOSSARY-001` differ, **the glossary wins.**

Related (not naming-locks, but adjacent): `../CAC_Frameworks/CAC_SECTION_404_POSITIONING.md` (POS-001) governs *external vocabulary* for §404 compliance; `../CANONICAL_CURRENT/CFL-DECISION-001_RECONCILIATION.md` records the only *ratified* name changes to date.

---

## 3. Why this folder exists (the cautionary case)

On 2026-06-27, during a polish pass on the cuttlefishclaws.com repo, an AI assistant renamed the investor-persona agents **"Builder Agent" → "Studio Investor Agent"** and **"Sovereign Agent" → "Enterprise Investor Agent"** (and their `CAC Builder` / `CAC Sovereign` version labels) — reasoning that the names "embed retired tier names." That reasoning was wrong: those are **locked persona names**, not tier names. The change was reverted on Navigator direction (`git revert caa6dce`). This folder exists so that never happens again.

**Lesson encoded as a rule:** a name being *related to* a retired or banned term is **not** grounds to rename it. Homonyms are intentional and must be preserved (see `RETIRED_BANNED_AND_GOTCHAS.md`).

---

## 4. Change control — how a canonical name *does* change

A canonical name changes **only** by this path:

1. The **Navigator** decides the change (no one else initiates it).
2. It is recorded as a ratified decision (e.g. a `CFL-DECISION-###` entry, as the tier rename was — see `NAME_REGISTRY.md` tiers).
3. `NAME_REGISTRY.md` is updated; the old name is moved to `RETIRED_BANNED_AND_GOTCHAS.md` with its replacement and the decision reference.
4. Downstream artifacts (repo, site, specs, decks) are updated to match — **after** steps 1–3, never before.

The **only** ratified name change so far is the CAC tier names (D-6). Everything else in `NAME_REGISTRY.md` is original and stays.

---

## 5. If you are an AI assistant or programmer working on Cuttlefish material

- Read `NAME_REGISTRY.md` before editing any user-facing copy, persona, token, tier, or component name.
- Treat every name there as locked. Match it exactly (spelling, casing, spacing — e.g. `TrustGraph` is one word).
- Found something that looks off? **Write it down and ask the Navigator. Do not edit.**
- Adding a *new* name (a new agent, product, spec)? Propose it; the Navigator confirms; then it's added here and locked.

---

*This folder is additive. It documents the Navigator's existing naming system; it does not invent or impose names. Anything below that is inaccurate is the Navigator's to correct — and once corrected, it is locked.*
