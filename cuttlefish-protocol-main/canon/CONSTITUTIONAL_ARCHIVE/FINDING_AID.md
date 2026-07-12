# Cuttlefish Labs — Constitutional Archive · Finding Aid

**Archive ID:** CFL-ARCHIVE-CONST-001
**Compiled:** 2026-06-28 (capture date of preservation copies)
**Compiled by:** Claude (digital-archivist role), under Navigator direction
**Status:** Preservation archive — primary-source holdings. NOT a synthesis. (The synthesis layer, EK-001, is a separate document that cites *into* this archive.)

---

## 1. What this archive is

This is a **preservation copy** of the primary constitutional / ethical-kernel source documents of Cuttlefish Labs, gathered from volatile development and archive locations into one stable fonds.

**Archival principles applied:**
- **Verbatim.** Every copy is byte-identical to its original. No headers were injected, no wording changed, no formatting normalized. Provenance lives *here* (in this Finding Aid and `MANIFEST.sha256`), never inside the artifacts.
- **Originals untouched.** Source files remain in place at their original paths (recorded below). This archive is additive; nothing was moved, renamed, or deleted at source.
- **Fixity.** Each copy carries a SHA-256 hash, captured at preservation and recorded in `MANIFEST.sha256`. Re-running the hashes detects any future tampering.
- **Preserve, don't adjudicate.** Where sources disagree (see §5), both/all are preserved and the discrepancy is *recorded*, not resolved. Reconciliation is a Navigator decision, not an archival one.
- **Record the gaps.** Known-missing lineage (see §6) is documented rather than papered over.

To verify integrity at any time: hash the files in `primary_sources/` and compare against `MANIFEST.sha256`.

---

## 2. Fonds structure

```
CONSTITUTIONAL_ARCHIVE/
  FINDING_AID.md          <- this file
  MANIFEST.sha256         <- fixity hashes (full SHA-256, 11 entries)
  primary_sources/
    doctrine/             <- the ceph-v3 doctrine/ corpus (7 holdings)
    mission/              <- the civilizational mission frame (1)
    soul_documents/       <- per-agent constitutions / SOULs (3), in subfolders that preserve original parent context
```

---

## 3. The original authority order (as the source itself declares it)

`doctrine/DOCTRINE_INDEX.md` (dated 2026-04-19) states the source's own interpretation rules **verbatim**:

> - Treat the Constitution as runtime-supreme.
> - Treat the Bill of Rights as protections for agent continuity and governance.
> - Treat TrustGraph as the operational enforcement layer for adversarial handling and trust scoring.
> - Treat the sustainability definitions file as the canonical machine-usable kernel definition.
> - Treat the two ethical kernel files as historical and philosophical reinforcement, not higher authority than the Constitution.

Its declared **canonical load order**: (1) constitution_…_v_1.md · (2) agent_bill_of_rights.md · (3) TRUSTGRAPH.md · (4) …sustainability_definitions…_v_1.md. Supplemental lineage: ETHICAL_KERNEL.md, ethical_kernel_full.md.

*This ordering is honored by EK-001; it was not invented for this task.*

---

## 4. Catalog of holdings

SHA-256 shown truncated; full hashes in `MANIFEST.sha256`. "Original date" = filesystem last-modified at capture.

### 4.1 doctrine/ — the constitutional corpus

| # | Archive path | Original source path | Version | Original date | Role (per DOCTRINE_INDEX) | SHA-256 | Scope |
|---|---|---|---|---|---|---|---|
| 1 | `doctrine/DOCTRINE_INDEX.md` | `D:\CuttlefishLabs_Organized\04_Products\Ceph_Agent_Platform\ceph-v3\doctrine\DOCTRINE_INDEX.md` | — | 2026-04-19 | The index / authority-order artifact | `EAB857C7…` | Full |
| 2 | `doctrine/constitution_cuttlefish_labs_ethical_kernel_v_1.md` | (same dir) | **v1.2** | 2026-03-03 | **Constitution — runtime-supreme** (8 Articles) | `0F9885DB…` | Full |
| 3 | `doctrine/agent_bill_of_rights.md` | (same dir) | **v1.0** | 2026-03-03 | Bill of Rights — agent continuity & governance (7 articles) | `BEADF96B…` | Full |
| 4 | `doctrine/TRUSTGRAPH.md` | (same dir) | — | 2026-02-08 | TrustGraph — operational enforcement (the **earlier** TrustGraph) | `C1166990…` | Full |
| 5 | `doctrine/cuttlefish_labs_ethical_kernel_and_sustainability_definitions_foundational_spec_v_1.md` | (same dir) | **v1** | 2026-02-10 | Sustainability definitions — canonical machine-usable kernel | `F4396581…` | Full |
| 6 | `doctrine/ETHICAL_KERNEL.md` | (same dir) | — | 2026-03-10 | Ethical kernel — historical/philosophical reinforcement | `A43CC0E5…` | Full |
| 7 | `doctrine/ethical_kernel_full.md` | (same dir) | — | 2026-03-10 | Ethical kernel (full) — historical/philosophical reinforcement | `9BE52459…` | Full |

### 4.2 mission/

| # | Archive path | Original source path | Doc ID | Version | Original date | SHA-256 | Scope |
|---|---|---|---|---|---|---|---|
| 8 | `mission/NEW_PROTOCOL_FOR_CIVILIZATION.md` | `D:\CuttlefishLabs_Organized\00_Current_Work\NEW_PROTOCOL_FOR_CIVILIZATION.md` | CFL-NARR-000 | v0.9 | 2026-05-19 | `507CCDFA…` | Full |

*The civilizational mission frame — "Safety, Regeneration, Stewardship, Integrity." Serves the "manifesto" role (no document titled "Manifesto" exists; see §6).*

### 4.3 soul_documents/ — per-agent constitutions

| # | Archive path | Original source path | Version | Original date | SHA-256 | Scope |
|---|---|---|---|---|---|---|
| 9 | `soul_documents/Architeuthis_Core/SOUL.md` | `D:\CuttlefishLabs_Dev\Desktop_Archive\Agents\Architeuthis_Core\SOUL.md` | v3.0 | 2026-03-27 | `8B740902…` | Full |
| 10 | `soul_documents/ceph-v3/ceph-v3--SOUL.md` | `D:\CuttlefishLabs_Dev\Desktop_Archive\07_Patents_and_IP_References\ceph-v3--SOUL.md` | v3 | 2026-04-19 | `E2C9390E…` | Full |
| 11 | `soul_documents/global-communicator/SOUL.md` | `D:\CuttlefishLabs_Dev\repo_review\repo\cuttlefishclaws-main\src\agents\global-communicator\SOUL.md` | — | 2026-06-26 | `8BF67902…` | Full |

---

## 5. Discrepancy register (preserved, NOT resolved)

These are recorded for the Navigator's decision. The archive takes no position; all variants are preserved intact.

**D-1 · Two TrustGraphs.** The constitutional TrustGraph — `doctrine/TRUSTGRAPH.md` (2026-02-08) and Article III of the Constitution v1.2 — uses bands **Trusted 80 / Neutral 50 / Cautious 20 / Adversarial 0**, with named injection/probing signals and −2/week decay. The *implemented* engine **CFL-SPEC-TG-001 / `trustgraph.py`** (2026-06) uses bands **Trusted 90 / Standard 70 / Monitored 50 / Cautious 20 / Suspended 10 / Revoked**, tier-seeded floors, and a different signal rubric. The implemented TrustGraph **diverged from the constitutional original**. Both are preserved. **Status: RESOLVED** — see **CFL-NARR-003** (The Two-Layer TrustGraph Architecture). D-1 reframed: not a discrepancy; two layers of one system, stacked and bridged.

**D-2 · Three Bills of Rights.** (a) `doctrine/agent_bill_of_rights.md` — **v1.0, 7 articles** (2026-03-03); (b) the website `AgentBillOfRights.tsx` — **8 articles**; (c) AIL-001 references an **"Agent Bill of Rights v2.0."** Three variants coexist; none is collapsed.

**D-3 · Two pillar framings.** The Constitution v1.2 Article VII names the three pillars **Economic / Social (Human) / Ecological**, with the **Social Pillar holding priority authority when pillars conflict**. `ETHICAL_KERNEL.md` is reported to also use a **Life / Liberty / Happiness** framing. Exact wording of each to be transcribed during EK-001 assembly; the framings are preserved side by side, not merged.

---

## 6. Provenance gaps & negative findings

- **`J:` drive lineage (inaccessible).** `DOCTRINE_INDEX.md` names earlier sources not present on this workstation: `J:\Strategic-Documents-2026-03-03` (Constitution + Bill of Rights), `J:\Cuttlefish-Constitutional-Framework` (TrustGraph), `J:\Nautiloid_Core` and `J:\cuttlefish stack transfer files\CuttlefishLabs` (ethical-kernel lineage). **Earlier or parallel constitutional versions may exist there.** This archive does not claim to be the complete lineage.
- **"Ocean Covenant" — not found.** No document, folder, or section by this name exists anywhere searched.
- **"Manifesto" — not found** as a titled document. `NEW_PROTOCOL_FOR_CIVILIZATION.md` (CFL-NARR-000) serves that function.

---

## 7. Related constitutional material referenced in place (NOT copied)

Held in active, version-controlled repositories and therefore referenced rather than duplicated:

- **Runtime constitution-as-code:** `D:\CuttlefishLabs_Dev\Cuttlefish\ceph-v3\agent\constitutional\` (`hard_limits.py`, `guard.py`, `token_burn.py`, `fabrication_detector.py`) + `ceph-v3\docs\constitutional-framework.md`.
- **Canon specs carrying constitutional language:** AIL-001, CC-001, SS-001, TG-001, POS-001 (in `CAC_Frameworks\` and `CANONICAL_CURRENT\`).
- **Site constitutional content:** `cuttlefishclaws-main\src\components\sections\AgentBillOfRights.tsx` (the 8-article variant — see D-2).

---

*This Finding Aid is a living archival record. When EK-001 (the synthesis) is assembled, it cites holdings by their archive path and SHA-256 so every constitutional claim is traceable to a verbatim, fixity-checked source.*
