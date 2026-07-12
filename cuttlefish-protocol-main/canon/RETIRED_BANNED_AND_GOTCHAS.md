# Retired Names, Banned Vocabulary & Naming Gotchas

Companion to `NAME_REGISTRY.md`. This file exists to stop two failure modes:
1. Someone re-introduces a **retired/banned** name ("correcting" back to an old term).
2. Someone sees a name that *resembles* a retired term and **renames a perfectly valid name** because of the resemblance — exactly the error that occurred on 2026-06-27.

**Rule for everything below: flag, don't change. Only the Navigator renames.**

---

## 1. Retired names (do not reuse for their old purpose)

| Retired name | Was | Now / replacement | Authority |
|---|---|---|---|
| **Resident / Builder / Sovereign** *(as TIER names)* | old CAC tier names | **Developer / Studio / Enterprise** tiers | ratified — CFL-DECISION-001 D-6 |
| **"TRIB"** *(as a token)* | a proposed equity ticker | **never adopted** — the security is **$E2R** | CFL-DECISION-001 D-1 |
| **"Constitutional Agent License"** *(as the CAC expansion)* | a wrong expansion of "CAC" | **Compute Access Certificate** | canon (CAC-005) |
| **"validator" / "staker" / "node operator"** *(as the actor)* | crypto-finance framing | **Builder Steward** | AIL-001, POS-001, D-2 |

> Retiring a name **as a tier** does not retire the same word everywhere. See §3.

---

## 2. Banned external vocabulary (POS-001 — §404 compliance)

These are not "names" but they are **never** to be attached to CAC in external-facing copy (regulatory exposure). Full standard: `../CAC_Frameworks/CAC_SECTION_404_POSITIONING.md`.

**Never (for CAC):** yield · APY · APR · interest · savings account / savings rate · "earn while you hold" · passive income · DeFi · dividend.
**Never (for the actor):** validator · staker · node operator · patronage dividend.
**Use instead:** activity reward · validation payment · compute access certificate · contribution credit · Stewardship Standing · Builder Steward.

(Reward/yield language **is** allowed on the $E2R / DAO-REIT *security* side, which is a separate rail — never mix it with CAC.)

---

## 3. GOTCHAS — homonyms that are INTENTIONAL (do not collapse or "fix")

The same word legitimately names different things. **A name being related to a retired term is NOT grounds to rename it.** These are the traps:

### "Builder"
- ✅ **Builder Steward** — the actor type. KEEP.
- ✅ **Builder Agent** — the investor-persona agent (version `CAC Builder`). KEEP. **This is the name renamed in error on 2026-06-27; it was reverted. Do not rename it again.**
- ⛔ **"Builder tier"** — RETIRED as a tier name (now "Studio").
- **Rule:** the tier retirement does **not** touch Builder Steward or Builder Agent. Never rename those because "Builder" was retired as a tier.

### "Sovereign"
- ✅ **Sovereign Agent** — the investor-persona agent (version `CAC Sovereign`). KEEP. **Also renamed in error on 2026-06-27; reverted. Do not rename it again.**
- ✅ **"Right to Sovereign Identity"** — an Agent Bill of Rights article name. KEEP.
- ✅ **Navigator Sovereignty** — the human-authority principle. KEEP.
- ⛔ **"Sovereign tier"** — RETIRED as a tier name (now "Enterprise").
- **Rule:** only the *tier* usage is retired. The persona, the right, and the sovereignty principle stay.

### "Anchor"
- ✅ **Anchor** — the top CAC membership **tier** (current, not retired).
- ✅ **anchor** (lowercase) — Ethereum "settlement & anchor" role, on-chain "anchoring" of the registry. Different meaning; KEEP both.
- **Rule:** don't assume "Anchor" means only the tier, or only the chain role — context decides; both are valid.

### "Trib" vs "Tributary" vs "TRIB"
- ✅ **Trib** — the governance agent (name-locked).
- ✅ **Tributary AI Campus** — the property/campus.
- ⛔ **"TRIB"** — a rejected token ticker (never use as a token; the security is $E2R).
- **Rule:** these are three different things. Don't merge them or rename Trib/Tributary because the token "TRIB" was rejected.

### "TrustGraph"
- ✅ **TrustGraph** — one word, camelCase. KEEP exactly. Never "Trust Graph" / "trust-graph" / "Trustgraph."

### "CAC"
- ✅ Always **Compute Access Certificate**. Never re-expand it to anything else.

---

## 4. The meta-lesson (encode this in any agent's instructions)

> **Resemblance is not grounds for renaming.** If a name looks like it "should" change because it resembles a retired tier, a banned word, or another name — that is precisely when you must **stop and ask the Navigator**, not edit. Most of these homonyms are deliberate. The cost of a wrong rename (broken identities, investor docs, on-chain refs, site copy) is far higher than the cost of asking.

---

*If anything here is wrong, the Navigator corrects it; the correction is then locked.*
