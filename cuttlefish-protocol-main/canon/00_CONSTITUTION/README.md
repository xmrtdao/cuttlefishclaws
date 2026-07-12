# 00_CONSTITUTION — The Constitutional Layer (Canonical Copies)

These are the **canonical working copies** of Cuttlefish Labs' constitutional documents. They sit **above** the protocol specifications in `CANONICAL_CURRENT\` (PVP/KYA/CAC/TG/SS/SGQ/AR/RRC) — the protocol exists to serve the principles defined here.

## Source of truth

> The **Constitutional Archive** is the source of truth for constitutional documents:
> `D:\CuttlefishLabs_Organized\00_Current_Work\CONSTITUTIONAL_ARCHIVE\`

The files here are **byte-verbatim copies** of the archive's preserved holdings (chain of custody: original → `CONSTITUTIONAL_ARCHIVE\primary_sources\` → here, every hop SHA-256 verified). They carry no injected headers — provenance lives in this README and in the archive's `FINDING_AID.md` / `MANIFEST.sha256`, never inside the artifacts. To amend constitutional content, amend at the source under Navigator authority; these are not independently editable.

## Authority order (as the source declares it — DOCTRINE_INDEX)

1. **Constitution** — runtime-supreme.
2. **Agent Bill of Rights** — protections for agent continuity and governance.
3. **TrustGraph doctrine** — operational enforcement layer for adversarial handling and trust scoring.
4. **Sustainability Definitions** — canonical machine-usable kernel definition.
5. **Ethical Kernel lineage** — historical and philosophical reinforcement, *not higher authority than the Constitution*.
6. **Civilizational Narrative** — the mission frame ("why this exists").

## Holdings (SHA-256 truncated; full in `..\..\CONSTITUTIONAL_ARCHIVE\MANIFEST.sha256`)

| Your name for it | File | Version | Date | SHA-256 |
|---|---|---|---|---|
| **Constitution** | `constitution_cuttlefish_labs_ethical_kernel_v_1.md` | v1.2 | 2026-03-03 | `0F9885DB6BA5…` |
| **Agent Bill of Rights** | `agent_bill_of_rights.md` | v1.0 | 2026-03-03 | `BEADF96B8B95…` |
| **TrustGraph doctrine** | `TRUSTGRAPH.md` | — | 2026-02-08 | `C1166990BBD1…` |
| **Sustainability Definitions** | `cuttlefish_labs_ethical_kernel_and_sustainability_definitions_foundational_spec_v_1.md` | v1 | 2026-02-10 | `F4396581B0C9…` |
| **Ethical Kernel lineage (1)** | `ETHICAL_KERNEL.md` | — | 2026-03-10 | `A43CC0E51494…` |
| **Ethical Kernel lineage (2)** | `ethical_kernel_full.md` | — | 2026-03-10 | `9BE524593508…` |
| **Civilizational Narrative** | `NEW_PROTOCOL_FOR_CIVILIZATION.md` | CFL-NARR-000 v0.9 | 2026-05-19 | `507CCDFAC49A…` |

## Important: two TrustGraphs coexist in the canon (discrepancy D-1)

`TRUSTGRAPH.md` here is the **constitutional TrustGraph doctrine** (2026-02-08): bands Trusted 80 / Neutral 50 / Cautious 20 / **Adversarial** 0. It is **distinct from** `..\TG-001_TRUSTGRAPH_SPEC.md`, the implemented **engine spec** (bands Trusted 90 / Standard 70 / Monitored 50 / Cautious 20 / Suspended 10 / Revoked). The engine diverged from the doctrine. **Both are legitimately preserved as two layers of one system:** the Constitutional TrustGraph (runtime) and the TrustGraph engine (TG-001). The layering and the bridge rule connecting them are specified in **CFL-NARR-003**. See also **D-2** (three Bill-of-Rights variants) and **D-3** (two pillar framings), which remain open.

---

*Companion: `..\..\CONSTITUTIONAL_ARCHIVE\FINDING_AID.md` (full provenance, discrepancy register, the `J:`-drive lineage gap). These copies were placed per Navigator direction establishing the Constitutional Archive as source of truth.*
