# Stewardship Standing Specification v1.0

**Cuttlefish Labs — CAC Protocol**
**The Earned-Competence Axis of Agent Governance**

---

**Document ID:** CFL-SPEC-SS-001
**Version:** 1.0 (current — locks the AIL-001 §4.3 "recommend, not prescribed" derivation)
**Date:** 2026-06-27
**Status:** Architectural spec, pre-implementation (Phase-1 engine accompanies — §12)
**Companion to:** AIL-001 §4 (the model this engine projects), TG-001 (the sibling axis), AR-001 (event source), SGQ-001 (reads both axes), SRP-001 (review outcomes / overrides)
**Classification:** Internal + AI Ethics Group deliverable
**Conforms to:** CFL-DECISION-001 (§404 activity model; POS-001 vocabulary; Builder Stewards)

> **Sibling of TG-001.** TrustGraph (TG-001) is the *behavioral* axis: one 0–100 score per agent. **Stewardship Standing is the *competence* axis: an N-of-domains, 0–100 score per (agent, domain).** SGQ-001 reads both and requires **both** to pass ("fail on either axis"). This spec closes TG-001 §12 Q6 — the architecture gap where Standing was referenced but undefined as an engine.

---

## 1. What Stewardship Standing is

**Stewardship Standing** is the accumulated, **domain-bounded** record of *competent participation* that grants a Builder Steward authority to perform attestation work at progressively higher tiers (AIL-001 §4.1). It is **the primary non-financial bond** — what is at stake when work is defective.

Standing is (AIL-001 §4.1): **earned, not granted** (no purchase, no transfer); **domain-specific**; **time-mediated**; **quality-mediated** (from peer-review outcomes, not volume); **appealable**; **visible**; **recoverable**.

| | **Stewardship Standing (SS-001)** | **TrustGraph (TG-001)** |
|---|---|---|
| Keyspace | **(agent, domain)** — N scores | agent — 1 score |
| Measures | earned competence in a domain | behavioral track record |
| Model | recency-weighted **quality average** (§7) | cumulative signal **sum** with decay |
| Gates | may-do-attestation-at-tier (the ladder) | may-attempt (transfers, governance, lifecycle) |
| Lowered by | defective work / Review (per domain) | violations / injection / inactivity (per agent) |

---

## 2. The domain set (AIL-001 §4.2)

Standing is tracked per validation domain. Initial set (**extensible** via Council charter):

```
engineering_review        materials_science        environmental_assessment
financial_modeling        governance_review        compliance_review
arbitration_reliability   attestation_integrity
```

A Steward may hold high Standing in `engineering_review` and low Standing in `environmental_assessment`, and is **routed only to work in domains where they have earned authority** (AIL-001 §4.2). The canonical domain registry is Council-governed (CC-001); the engine treats domains as opaque keys.

---

## 3. Cross-domain isolation (load-bearing — enforced in the engine, not just the spec)

> **"Each domain is its own accreditation"** (AIL-001 §4.2). A Steward whose `engineering_review` Standing is reduced does **not** lose `arbitration_reliability` Standing.

This is a **structural** requirement, not a policy one. The engine **must have no code path** that updates Standing in domain B from an event tagged to domain A. Each domain's Standing is computed **only** from that domain's events. The §13 test vectors verify this explicitly (an `engineering_review` slash must provably leave `arbitration_reliability` unchanged). An implementation that computes a single cross-domain aggregate and slices it is **non-conforming**.

---

## 4. What Standing includes and excludes (AIL-001 §4.3)

**Inputs** (per domain, from AR-001 events): completed attestations, peer-review outcomes, appeal outcomes, consensus alignment, time-in-domain, recency-weighted quality.

**Standing must NOT include** (AIL-001 §4.3): token holdings; CAC reserve / capital balance; social popularity or political alignment; off-protocol behavior (except the narrow §6 exception); endorsements unrelated to work product. **The engine has no access to balances or social signals by construction** — it reads only AR-001 quality-scored work events.

---

## 5. Maturation ladder (AIL-001 §4.4 — value AND time gates)

The ladder tier is the **highest** tier whose **both** gates pass (anti-sybil minimum time *and* domain Standing):

| Tier | Min time in domain | Domain Standing | Authority |
|---|---|---|---|
| **Participant** | 0–7 d | n/a | read-only; comment without weight |
| **Contributor** | ≥ 7 d | ≥ 30 | low-impact attestations; peer review |
| **Builder Steward** | ≥ 30 d | ≥ 60 | weighted review; multi-domain attestation |
| **Senior Steward** | ≥ 90 d | ≥ 80 | consensus authority; arbitration; review of others |
| **Council-eligible** | ≥ 180 d | ≥ 90 **in ≥ 2 domains** | constitutional governance (seating is CC-001 random selection + election, not derived here) |

Time gates are **anti-sybil, not anti-skill** (AIL-001 §4.4): a brilliant newcomer still spends the minimum time accruing peer-reviewed quality before weighted routing. Tier upgrades are AR-001 `TIER_UPGRADE` events; downgrades are `STEWARDSHIP_REVIEW_OUTCOME` events (§6). The engine **reports** the eligible ladder tier; *seating* a Council Steward is CC-001's job (the engine emits a `council_eligible` flag only).

---

## 6. Review outcomes, downgrades, and the §4.5 off-protocol exception

Two adjustment paths beyond organic quality (§7):

1. **Stewardship Review outcomes (SRP-001).** A defective-work finding enters as an AR-001 `STEWARDSHIP_REVIEW_OUTCOME` (or `STANDING_ADJUSTED`) event carrying a **domain** and an effect. Effects: a **cap** (`standing_cap:<v>` — Standing in that domain may not exceed `v` until lifted), a **set** (`standing_set:<v>`), or a **restore** (`standing_restore` — lifts a prior cap). Caps are the Council/Review's hard lever, distinct from the running quality average.
2. **Off-protocol exception (AIL-001 §4.5 — narrow).** Convictions for fraud, professional malpractice, or deliberate misrepresentation *substantively similar to the domain* may ground a **Council-level** Review. This reaches the engine **only** as a Council-authored `STEWARDSHIP_REVIEW_OUTCOME` event (a cap/set in the affected domain) — the conviction itself is off-protocol evidence behind that event, never a direct input. **Explicitly out of scope:** political disagreement, social-media controversy, unrelated misdemeanors, employment changes, opinions. *The framework is not social credit and must not become it* (AIL-001 §4.5).

The engine stays purely event-sourced: every adjustment, organic or Council, is an AR-001 event it replays.

---

## 7. Computation model (LOCKED — normative)

Per domain, Standing is a **recency-weighted quality average** (AIL-001 §4.3 "exponentially time-weighted moving average of quality-scored events, normalized 0–100"), then bounded by any active cap.

### 7.1 Locked parameters (v1.0)

| Parameter | Symbol | Value |
|---|---|---|
| Quality half-life | `H` | **90 days** (7 776 000 s) — recent work weighs more |
| Default quality | `q₀` | **1.0** for a clean positive work event lacking an explicit `quality_score` |
| Min events for a non-provisional score | `N_min` | **3** in the domain |
| Bounds | — | [0, 100], rounded to 2 decimals |
| Quality-scored event types | — | `VALIDATION_COMPLETED`, `VALIDATION_PEER_REVIEWED`, `ATTESTATION_ISSUED`, `DISPUTE_RESOLUTION` |

`q(e) ∈ [0,1]` is `work_unit.quality_score` if present, else `q₀`. An appeal-overturned negative (a `CORRECTION_ISSUED` referencing the event) removes it from the average (replayed to zero weight).

### 7.2 The per-domain equation (exact)

For domain `d`, with quality events `e_i` at times `t_i` ≤ `as_of`:

```
w_i      = 2 ^ ( -(as_of - t_i) / H )                  # recency weight, half-life H
raw      = Σ_i (w_i · q(e_i)) / Σ_i (w_i)              # in [0,1];  raw = 0 if no events
standing = round( 100 · raw , 2 )
standing = min( standing, active_cap(d, as_of) )       # §6 cap (default cap = 100)
```

- **No events in `d` → Standing 0, tier Participant** (unproven, not penalised).
- **Fewer than `N_min` events → `provisional = true`** (the value is shown but ladder tier is capped at Contributor until `N_min` is reached — anti-sybil).
- **Determinism (same guarantee as TG-001 §5.4):** over the **event snapshot visible at query time** + `as_of`, the per-domain Standing is unique and reproducible. Late events change a prior `as_of` result (expected). Auditors pin the AR-001 anchor height and `as_of`.
- **Cross-domain isolation (§3):** `raw` for domain `d` sums **only** events tagged `d`. There is no term that reads another domain.

The half-life and thresholds are **governed config** (Council, CC-001 timelock); v1.0 values above are locked and pinned by the §13 test vectors.

---

## 8. Integration

- **In ← AR-001.** The engine reads each domain's quality events + review-outcome events. Each Standing change is itself recorded as a `STANDING_ADJUSTED` event (auditable history).
- **Out → SGQ-001.** SGQ-001 reads **per-(agent, domain) Standing + ladder tier** as the *primary* input for "entitled to be rewarded for this activity in this domain," alongside the TG-001 score. **Both must pass.** After SS-001 ships, SGQ-001 has two parallel read-only services (`/trustgraph/v1/...` and `/standing/v1/.../{domain}`) and the gate is an **AND**.
- **Out → routing (AIL-001 §4.2).** The ladder tier per domain determines what work a Steward may be routed to and the weight their attestations carry.
- **With the reserve (AIL-001 §5).** The CAC operational reserve is anti-spam friction, **not** the bond and **not** an input to Standing — the engine never reads it (POS-001: "operational reserve," never "stake/bond/deposit").

---

## 9. Interface

```
GET /standing/v1/{agent_did}/{domain}  [?as_of=<epoch>]
    -> { agent, domain, standing, provisional, ladder_tier, time_in_domain_days,
         event_count, active_cap, council_eligible, updated_at }
GET /standing/v1/{agent_did}            [?as_of=<epoch>]
    -> { agent, domains: { <domain>: {standing, ladder_tier, ...}, ... }, council_eligible }
GET /standing/v1/{agent_did}/{domain}/history ?limit=100
    -> { agent, domain, events: [ {event_id, activity_type, quality, weight_at_query, at} ] }
# No write endpoint: Standing changes ONLY via AR-001 events (consumer + projector).
```

`council_eligible` is true when ≥ 90 Standing in ≥ 2 domains and ≥ 180 d — a *flag for CC-001*, not a seating.

---

## 10. §404 / POS-001 posture

Standing is **earned competence, not capital and not a financial instrument.** It is never bought, staked, or transferred, and it pays no reward (rewards flow only via RRC-001, gated by SGQ-001 reading Standing). Vocabulary: "Stewardship Standing," "Builder Steward," "earned credentialing." Never "validator score," "stake," "bond," "reputation token," "social credit." The §4.5 exception is **narrow by design** so the framework cannot become social credit.

---

## 11. Failure modes

| Failure | Mitigation |
|---|---|
| Cross-domain leakage (bug) | Structural per-domain computation (§3); explicit isolation test vector (§13) |
| Sybil / fast competence | `N_min` + ladder time gates (anti-sybil); principal-bound via KYA-001/PVP-001 |
| Volume gaming (many low-quality events) | Quality **average**, not sum — low-q events drag the mean down, not up |
| Staleness (old high score persists) | Recency half-life `H`; old events decay in weight |
| Council overreach via §4.5 | Narrow exception; Council-authority-only review-outcome events; appealable; audit trail |
| Capital creeping into Standing | Engine has no access to balances/reserve (§4); POS-001 vocabulary guard |
| Disagreement with TrustGraph | By design separate axes; SGQ-001 requires both; neither overrides the other |

---

## 12. Phased implementation

**Scope binds to PILOT-001 §3.** Build on the AR-001 registry (the events already exist: `STANDING_ADJUSTED`, `STEWARDSHIP_REVIEW_OUTCOME`, `ATTESTATION_ISSUED`, `VALIDATION_*`).

| Phase | Scope |
|---|---|
| **Phase 1 (pilot)** | `standing.py` engine in the registry service: per-(agent, domain) recency-weighted quality projection + ladder + caps + provisional flag; `/standing/v1/...` reads; cross-domain isolation enforced + tested. Single-node, fail-closed. |
| **Phase 2** | Appeal/correction replay; council-eligibility surfacing to CC-001; governance-config half-life/thresholds; consensus-alignment input. |
| **Phase 3** | Cross-DAO portability (per-domain, discounted); on-chain Standing reference (Cardano, with TG-001 §9 `TrustOracle` sibling); signed decisions. |

---

## 13. Open questions

1. **Consensus alignment & appeal weighting** — AIL-001 §4.3 lists `consensus_alignment` and `appeal_outcomes`; their exact contribution to `q(e)` vs. as separate terms needs pilot tuning (recommend: fold into the per-event quality score so the average stays one clean equation).
2. **Council-eligibility "≥ 2 domains"** — confirm whether the two domains must be related, and whether election (CC-001) consumes this flag directly.
3. **Half-life per domain** — single `H = 90 d` for all domains, or per-domain (fast-moving fields decay faster)? Recommend single for v1; per-domain via governed config later.
4. **Provisional handling in SGQ-001** — does a provisional (< `N_min`) Standing block reward-eligibility outright, or permit only Contributor-tier work? Recommend the latter.
5. **Reserve sufficiency check** — AIL-001 §5 ties a min reserve per tier; that check lives in the CAC-card service (CCSP-001), not here — confirm SGQ-001 composes it.

---

## 14. Next concrete implementation steps

1. Implement the pure core `compute_standing(domain_events, as_of, cap)` (§7.2) and `ladder_tier(standing, time_in_domain, provisional)` (§5).
2. Implement `StandingEngine` over the registry store: per-domain event grouping with **structural** isolation; `STANDING_ADJUSTED`/review-outcome cap handling.
3. Expose `/standing/v1/...` (§9) read/list/history.
4. Ship test vectors incl. the **cross-domain isolation** case and recency/ladder/cap cases.
5. Wire SGQ-001 to read this alongside TG-001 (the "fail on either axis" AND).

---

**Maintainer:** Cuttlefish Labs (Navigator) + collaborating Builder Stewards

**Companion documents:**
- `AGENT_IDENTITY_AND_LIABILITY_FRAMEWORK.md` (AIL-001 §4) — the model this projects
- `TG-001_TRUSTGRAPH_SPEC.md` — the sibling (behavioral) axis
- `ACTIVITY_REGISTRY_V1.txt` (AR-001) — event source; `STANDING_ADJUSTED` events
- `SGQ-001_STANDING_GATE_QUERY.md` — reads Standing + TrustGraph (the AND)
- `STEWARDSHIP_REVIEW_PROCEDURE.md` (SRP-001) — review outcomes / caps / appeals
- `CC-001_COUNCIL_CHARTER.md` — Council eligibility / seating; domain registry governance
- `CAC_SECTION_404_POSITIONING.md` (POS-001) — vocabulary discipline
