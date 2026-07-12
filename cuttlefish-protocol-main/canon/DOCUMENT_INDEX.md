# Cuttlefish Labs — Document Index

**Earth 2.0 / CAC Protocol / $E2R — Master Reference**

---

**Last updated:** May 18, 2026
**Location:** `D:\CuttlefishLabs_Organized\00_Current_Work\`
**Maintainer:** David Elze, Navigator

> This index covers all strategic documents produced for Cuttlefish Labs as of this date. For source specs (CAC Canonical Spec v4, Activity Registry, Proposal-to-Reward Pipeline), see the `CAC_Frameworks/` subfolder. All documents are drafts unless marked otherwise.

---

## Tier 0: Master Narrative & Orientation

| ID | File | Purpose | Audience | Status |
|---|---|---|---|---|
| — | `BUILDER_AGENT_ONBOARDING.md` | Read-first orientation for any builder agent (Ceph, successors, siblings) working on Cuttlefish deliverables. Points to the narrative docs, current mission state, blocking decisions, and vocabulary discipline. | Builder agents | Maintained (last updated 2026-05-19) |
| CFL-NARR-000 | `NEW_PROTOCOL_FOR_CIVILIZATION.md` | The civilizational frame. Sits above the master narrative — says *why* the work exists ("Building the New Protocol for Civilization") in human, values-first terms before any mechanism or security. Source for website hero, partner/Steward recruiting, the team. | Everyone | v0.9 draft |
| CFL-NARR-001 | `CUTTLEFISH_MASTER_NARRATIVE.md` | Unified narrative: Brooklyn → Over-Under → Earth 2.0 → CAC → $E2R. Source document for decks, website, investor conversations. | Investors, partners, government, website | v0.9 draft |
| CFL-NARR-002 | `CUTTLEFISH_LABS_DEEP_DIVE_v1.md` | Deep-dive synthesis — "Where We Have Been, Where We Are, Where We Are Going." Point-in-time consolidation (as of 2026-05-18) of the full spec stack into one narrative. Predates NARR-000, CLA-001, the SOC2 docs, and the FACT memos — treat as a May-18 snapshot. | Internal | v1.0 draft |

---

## Tier 1: $E2R Securities Stack

*Requires securities counsel review before external use. Handle as confidential.*

| ID | File | Purpose | Audience | Status |
|---|---|---|---|---|
| CFL-SPEC-E2R-001 | `CAC_Frameworks/E2R_REG_A_FEASIBILITY.md` | Reg A+ feasibility analysis. Howey analysis, exemption comparison, two-track structure recommendation, counsel questions. | Securities counsel | v0.9 draft |
| CFL-SPEC-E2R-002 | `CAC_Frameworks/E2R_REG_A_OFFERING_CIRCULAR_OUTLINE.md` | Form 1-A content guide. Full SEC structure with drafting notes. Risk factors, disclosure issues, filing timeline. | Securities counsel | v0.8 draft |
| CFL-SPEC-E2R-003 | `CAC_Frameworks/E2R_COUNSEL_ENGAGEMENT_BRIEF.md` | One-pager for prospective securities counsel. Email to law firms for quotes and engagement scoping. | Prospective securities counsel | v0.9 draft |
| CFL-SPEC-E2R-004 | `CAC_Frameworks/E2R_BLOCKING_DECISIONS.md` | Six decisions blocking Form 1-A filing. Analysis and recommendations for each. Owner: David. | Internal | v0.9 draft |

---

## Tier 1.5: Counsel Factual Record

*Pre-counsel factual disclosure memos. Each resolves a specific question in CFL-SPEC-E2R-004. Treat as attorney work product once transmitted to counsel.*

| ID | File | Purpose | Resolves | Status |
|---|---|---|---|---|
| CFL-FACT-TRIB-001 | `CAC_Frameworks/FACT_TRIBUTARY_CAMPUS_STATUS.md` | Tributary Campus property status factual record. Fillable template — captures the company's actual relationship to the property for Form 1-A Item 8 disclosure. | E2R-004 Decision 1 | v0.1 template — awaiting completion |
| CFL-FACT-NAM-001 | `CAC_Frameworks/FACT_NAMIBIA_ENGAGEMENT_STATUS.md` | Namibia engagement factual record. Fillable template — captures all contact (or absence thereof) with Namibian government and affiliated entities. | E2R-004 Decision 6, Q1 | v0.1 template — awaiting completion |
| CFL-FACT-WAICW-001 | `CAC_Frameworks/FACT_WAICW_ENGAGEMENT_STATUS.md` | WA-ICW engagement factual record. Fillable template — per-jurisdiction matrix across 11 nations + regional bodies. | E2R-004 Decision 6, Q2 | v0.1 template — awaiting completion |

---

## Tier 2: CAC Protocol Specs

*Internal operating specs. Vocabulary discipline is critical on any external-facing version.*

| ID | File | Purpose | Status |
|---|---|---|---|
| CFL-SPEC-CLA-001 | `CAC_Frameworks/CAC_CLARITY_ACT_ALIGNMENT.md` | **The canonical CAC ↔ CLARITY Act §404 alignment document.** Consolidates the substantive alignment argument (previously scattered across PRP-001, AIL-001, NARR-001). Prohibition, permitted categories, element-by-element mapping, anti-evasion posture, the "stands on its own" contingency, rail separation. All legal claims marked [VERIFY] pending counsel. | v0.9 draft |
| CFL-SPEC-POS-001 | `CAC_Frameworks/CAC_SECTION_404_POSITIONING.md` | Vocabulary discipline standard. What to say / not say about CAC across all external surfaces. Protects the CLA-001 alignment from being undermined by wrong words. | v1.0 |
| CFL-SPEC-PRP-001 | `CAC_Frameworks/PROPOSAL_TO_REWARD_PIPELINE_v1.md` | 5-layer validation pipeline spec. Canonical architecture document. | v1.0 |
| CFL-SPEC-AR-001 | `CAC_Frameworks/ACTIVITY_REGISTRY_V1.txt` | Activity Registry spec. Append-only cryptographic audit trail for all rewards. | v1.0 |
| CFL-SPEC-AIL-001 | `CAC_Frameworks/AGENT_IDENTITY_AND_LIABILITY_FRAMEWORK.md` | Agent governance. Identity, liability, and accountability rules for AI Stewards. | v1.0 |
| CFL-SPEC-BSR-001 | `CAC_Frameworks/CEPH_V3_BUILDER_STEWARD_RUNTIME.md` | Bridge doc. Specifies how the Ceph V3 runtime code (`D:\CuttlefishLabs_Dev\Cuttlefish\ceph-v3\`) maps to PRP-001 / AR-001 / AIL-001 as the per-agent Builder Steward runtime substrate. | v0.9 draft |
| CFL-SPEC-CCSP-001 | `CAC_Frameworks/CAC_CARD_SPEND_PROTECTION.md` | CAC card anti-runaway feature. Two-layer cap (card-service policy + runtime enforcement) preventing agent compute waste. Member-facing spend protection. | v0.9 draft |
| CFL-SPEC-SRP-001 | `CAC_Frameworks/STEWARDSHIP_REVIEW_PROCEDURE.md` | Operational procedure for Stewardship Review proceedings — fills in AIL-001 §7. Panel formation, discovery, hearing, standard of proof, written findings, appeals, restoration. | v0.9 draft |
| CFL-SPEC-OUR-001 | `Over_Under_Case_Studies/NAMIB_DESIGN_LANGUAGE_v0_1.md` | Namib coastal-desert building design language. Parametric Oculus Ring grammar (T1-T6), climate-driven rules, BFRP/fog-cistern engineering spec, Path A (Rhino) + Path B (Three.js) integration. Maps current Namibia Cesium assets to the taxonomy. | v0.1 |
| CFL-SPEC-OUR-001-A | `Over_Under_Case_Studies/NAMIB_DESIGN_LANGUAGE_v0_5_CAMPUS_ADDENDUM.md` | Campus addendum — multi-ring siting (constellation / spine / radial), lee courts from offset rings, elevated link bridges, shared fog-cistern service spine. Cesium pipeline instantiation. | v0.5 |
| CFL-SPEC-OUS-001 | `OVER_UNDER_STUDIO_OUTPUT_SPEC.md` | Over/Under Studio output architecture. Locks the two-track split (Design Twin in Cesium / Hero Renders in Blender), with the buildability constraint engine as Track 1 lead and a required provenance handle across both. Anti-drift guardrail produced after the v3→v8.1 fidelity-loop reset. Read before iterating on the Studio. | v1 |
| CFL-SPEC-OUS-001-A | `OUS_BLOOMSTACK_MODULES.md` | Bloomstack module-type extension. Shifts Bloomstack from "Voronoi tessellation of identical planters" to "modular composition on a shared column grid" — stair / elevator / restroom / courtyard / planter modules per cell, with code-compliance dimensions (IBC stair rise/run, ADA elevator/restroom clearances, egress widths) automated by the constraint engine. Includes rule-based auto-placement with manual-override CSV. | v1 |
| — | `CAC_Frameworks/CAC_Canonical_Spec_v4.md` | Full CAC Canonical Spec v4. Membership model, tiers, smart contract architecture, constitutional model. | v4.0 |

---

## Tier 2.5: Operational Compliance & Trust Infrastructure

*Cross-cutting compliance and attestation docs. Subset transmittable to platform consultants and auditors with confidentiality preserved.*

| ID | File | Purpose | Status |
|---|---|---|---|
| CFL-SPEC-SOC2-001 | `CAC_Frameworks/CUTTLEFISH_SOC2_READINESS.md` | SOC 2 readiness spec. Scope (Security + Confidentiality + Processing Integrity), timing tied to Reg A+ window, spec-to-control crosswalk, gap inventory, three critical risk flags. Companion to entire CAC stack. | v0.9 draft |
| CFL-EXP-SOC2-001 | `SOC2_EXPLAINER.md` | SOC 2 explainer. Plain-language: what SOC 2 is, why it exists, the 5 TSCs, Type 1 vs Type 2, Cuttlefish's relationship to it (three pull forces, the audit-infrastructure-as-product reframe, what makes Cuttlefish unusual). Shareable with partners, contractors, Steward candidates. | v1.0 |

---

## Tier 3: Brooklyn / Physical Proof Case

| ID | File | Purpose | Status |
|---|---|---|---|
| — | `Brooklyn_Mega_Block/brooklyn_mega_block_master_development_program.md` | Master development program. 300–500 acre Newtown Creek industrial compression and regeneration platform. | Complete |
| — | `Brooklyn_Mega_Block/brooklyn_mega_block_existing_conditions_research.md` | Existing conditions research for the Mega Block influence district. | Complete |
| — | `Over_Under_Case_Studies/brooklyn_bqe_over_under_architecture_case_study.md` | BQE Over/Under proposal. Full case study: existing conditions, three-layer solution, precedents. | Complete |
| CFL-DECK-BQE-001 | `Over_Under_Case_Studies/BQE_PITCH_DECK_OUTLINE.md` | BQE pitch deck content brief. 18-slide outline for designer. Government, institutional, and investor versions. No securities content. | v0.9 draft |
| — | `Over_Under_Case_Studies/penn_dot_regional_proposal_liberty_riverfront_over_under_corridor.md` | Philadelphia Liberty Riverfront Over/Under corridor proposal. Regional expansion of the framework. | Complete |

---

## Tier 4: International Vision (Concept Stage)

*Vision papers only. No binding agreements. Handle carefully in any investor or public disclosure.*

| File | Description | Status |
|---|---|---|
| `International_Earth2/namibia_earth_2.md` | Namibia Earth 2.0 — first Earth 2.0 nation deployment concept. Dual energy, digital twin, DAO governance, basalt economy. | Vision paper — no government agreements |
| `International_Earth2/west_african_intercoastal_waterway_vision_paper.md` | West African Intercoastal Waterway — 4,500+ km maritime corridor, Walvis Bay to Abidjan, 8+ sovereign nations. | Vision paper — no sovereign commitments |

---

## Tier 5: Infrastructure Research

| File | Description | Status |
|---|---|---|
| `Infrastructure_Research/open_source_parametric_infrastructure_stack_research.md` | Open-source parametric infrastructure tool research. Available toolchains for Earth 2.0 design stack. | Complete |
| `Infrastructure_Research/earth_2_parametric_infrastructure_compiler_brief.md` | Parametric infrastructure compiler brief. AI-native design tool specification. | Complete |
| `Earth2_Compiler/earth_2_parametric_infrastructure_compiler_brief.md` | (Duplicate in Earth2_Compiler/ folder) | Complete |

---

## Tier 6: Engineering Specs (ITB / Immersed Tunnel)

| File | Description | Status |
|---|---|---|
| `ITB_CC_Briefs/CC_BRIEF_Phase_2.2_BFRP_Cage_Geometry_Nodes.md` | BFRP cage geometry nodes — Blender/Geometry Nodes spec | Complete |
| `ITB_CC_Briefs/CC_BRIEF_Phase_2.3a_PT_Tendon_Geometry.md` | Post-tensioned tendon geometry spec | Complete |
| `ITB_CC_Briefs/CC_BRIEF_Phase_2.6b_YJunctionGeometryFix.md` | Y-junction geometry fix | Complete |
| `ITB_CC_Briefs/CC_BRIEF_Phase_2.6_YJunctionBoolean.md` | Y-junction boolean operations | Complete |

---

## Tier 7: Website and Communications

| ID | File | Purpose | Status |
|---|---|---|---|
| CFL-SPEC-WEB-001 | `WEBSITE_REBUILD_SPEC.md` | cuttlefishlabs.io rebuild spec. Page-by-page content brief, vocabulary rules, launch sequencing, legal notices. | v0.9 draft |

---

## Document ID Registry

| Series | Description |
|---|---|
| CFL-NARR-### | Narrative and master overview documents |
| CFL-SPEC-E2R-### | $E2R securities offering documents |
| CFL-FACT-### | Counsel factual record memos (pre-Form 1-A disclosure templates) |
| CFL-SPEC-CLA-### | CLARITY Act / Section 404 alignment documents |
| CFL-SPEC-POS-### | Positioning and vocabulary standards |
| CFL-SPEC-PRP-### | Proposal-to-Reward Pipeline specs |
| CFL-SPEC-AR-### | Activity Registry specs |
| CFL-SPEC-AIL-### | Agent Identity and Liability docs |
| CFL-SPEC-BSR-### | Builder Steward Runtime bridge docs (Ceph V3 ↔ CAC stack) |
| CFL-SPEC-CCSP-### | CAC Card Spend Protection feature specs |
| CFL-SPEC-SRP-### | Stewardship Review procedural docs |
| CFL-SPEC-SOC2-### | SOC 2 readiness and operational compliance docs |
| CFL-EXP-### | Plain-language explainer documents (pedagogical / shareable) |
| CFL-SPEC-WEB-### | Website and communications specs |
| CFL-DECK-BQE-### | BQE pitch and presentation materials |
| CFL-DECK-E2R-### | Earth 2.0 general pitch materials (to be created) |

---

## Immediate Action Items (as of May 17, 2026)

*Derived from the document stack — not exhaustive. See CFL-SPEC-E2R-004 for the full decision memo.*

| Action | Owner | Prerequisite doc | Urgency |
|---|---|---|---|
| Email E2R Counsel Engagement Brief to 3 securities firms | David | CFL-SPEC-E2R-003 | This week |
| Document Tributary Campus actual property status | David | CFL-SPEC-E2R-004 (Decision 1) | Before counsel engagement |
| Initiate conversation with tZERO and Securitize Markets | David | CFL-SPEC-E2R-004 (Decision 4) | Within 30 days |
| Hire designer for BQE pitch deck | David | CFL-DECK-BQE-001 | This week |
| Commission Phase 1 website rebuild | David | CFL-SPEC-WEB-001 | This week |
| Launch Phase 1 website (no $E2R pages) | Web developer | CFL-SPEC-WEB-001 | After rebuild |
| Document Namibia/WA-ICW actual engagement status in writing | David | CFL-SPEC-E2R-004 (Decision 6) | Before counsel engagement |
| Resolve bridge round terms (SAFE structure, valuation cap) | David + counsel | CFL-SPEC-E2R-004 (Decision 5) | After counsel retained |

---

*Updated: May 17, 2026*
