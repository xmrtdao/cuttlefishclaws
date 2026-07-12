# TrustGraph Specification v1.0

**Cuttlefish Labs — CAC Protocol**
**The Behavioral Trust Layer of Agent Governance**

---

**Document ID:** CFL-SPEC-TG-001
**Version:** 1.0 (current — locks the rubric that CAC-005 §9 deferred)
**Date:** 2026-06-27
**Status:** Architectural spec, pre-implementation (Phase-1 data model already exists — §11)
**Companion to:** CAC-005 §9, AIL-001 (Stewardship Standing), AR-001 (event source), SGQ-001 (gate that reads both axes), KYA-001
**Classification:** Internal + AI Ethics Group deliverable
**Conforms to:** CFL-DECISION-001 (§404 activity model — TrustGraph carries **no** financial reward; POS-001 vocabulary; Developer/Studio/Enterprise/Anchor tiers)

> **Supersedes for the trust model** the inline TrustGraph sections of `CAC_Frameworks/CAC_Canonical_Spec_v4.md` §6 (stale: carries the banned "revenue share by TrustGraph ~4.5% APY" framing and old tier names). Bands/weights here are the locked canonical set.

---

## 1. What TrustGraph is — and how it differs from Stewardship Standing

**TrustGraph** is a dynamic, **per-agent behavioral score from 0–100** that measures an agent's track record of constitutional, safe, honest operation. It gives the CAC its "constitutional teeth": it gates what an agent may *attempt* — transfer privileges, governance access, tier eligibility, and the SUSPENDED/REVOKED lifecycle.

Cuttlefish governance has **two distinct trust axes; they must never be conflated** (this is the single most important clarification in this spec):

| | **TrustGraph (TG-001)** | **Stewardship Standing (AIL-001)** |
|---|---|---|
| Measures | Behavioral track record of *one agent* | Earned *competence* of a Builder Steward in a *domain* |
| Shape | Single 0–100 score per agent | Per-domain, laddered (Contributor→Builder Steward→Senior→Council) |
| Earned by | Constitutional, safe, honest behavior over time | Peer-reviewed quality work in a domain over time |
| Gates | May-attempt: transfers, governance, tier, lifecycle | May-do-attestation-at-tier: review/attest authority |
| Lost by | Violations, injection, fabrication, inactivity decay | Defective work (Stewardship Review, AIL-001 §6) |
| Read by | SGQ-001 (as one input), lifecycle, transfer checks | SGQ-001 (as the primary input for reward eligibility) |

They are **related but orthogonal**: an agent can have high TrustGraph (well-behaved) but low Standing in a domain (unproven there), or high Standing but a TrustGraph hit from a recent violation. **SGQ-001 reads both**: Standing decides "entitled to be rewarded for this activity"; TrustGraph decides "behaviorally permitted to act at all." A failure on either blocks.

---

## 2. Score properties

- **Bounded** 0–100. New agents seed at their **tier floor** post-KYA (§3), not at 0 for a verified principal; a brand-new *network* (cross-DAO) starts an agent low (portability, §8).
- **Asymmetric** — slow to earn (sustained good behavior over weeks), fast to lose (a single serious violation drops 30–50). *"Building trust is slow and intentional; losing it is swift and asymmetric — by design."*
- **Event-sourced & deterministic** — the score is a pure replay of the agent's AR-001 event history under this rubric. Two implementations replaying the same events produce the same score (§5).
- **Decaying** — inactivity costs **−2/week** with no positive signal; active engagement resets the decay timer. Decay floors at the tier floor, never below it from decay alone (only violations go lower).
- **Observable** — any party may query an agent's current score before transacting (§7).
- **Constitutional** — bound to `CONSTITUTION.md` / Agent Bill of Rights compliance; violations are the largest negative signals.

---

## 3. Bands, effects, and lifecycle (reconciled — canonical)

| Score | Band | Effects |
|---|---|---|
| **90–100** | Trusted | Full transfer + governance; reduced protocol fee (0.20%) |
| **70–89** | Standard | Full transfer + governance; standard fee (0.25%) |
| **50–69** | Monitored | Transfers capped at Studio-tier limits; no governance voting |
| **20–49** | Cautious | Transfers restricted, no cross-DAO; elevated fee (0.35%); no voting |
| **10–19** | **SUSPENDED (auto)** | Signing blocked; reads allowed; Stewardship Review may be opened |
| **0–9** | **REVOKED (auto)** | Credential revoked; forensic read-only (lifecycle terminal) |

**Tier floors (from CAC-005 §4):** Developer 30 · Studio 40 · Enterprise 55 · Anchor 70. An agent whose score falls **below its tier floor** is restricted to the highest tier its score supports until it recovers (it does not lose the credential, but loses tier-gated capability). These thresholds drive the CAC lifecycle states `SUSPENDED`/`REVOKED` (CAC-005 §12) and feed SGQ-001 (`min_cac_tier`, suspension override).

---

## 4. The scoring rubric (LOCKED — keyed to AR-001 ActivityTypes)

This is the rubric CAC-005 §9 deferred. Deltas are applied when the corresponding **AR-001 event** is written (AR-001 §3.3). Positive signals require the event to be valid/clean per its evidence.

| Signal (AR-001 ActivityType / condition) | Δ | Notes |
|---|---|---|
| `VALIDATION_COMPLETED` (clean) | **+3** | core productive signal |
| `VALIDATION_PEER_REVIEWED` (passed) | **+2** | quality confirmed by peers |
| `ATTESTATION_ISSUED` (by Senior+ Steward, upheld) | **+1…+3** | weighted by attestor Standing |
| `GOVERNANCE_VOTE` | **+1** | participation (cap, §5) |
| `GOVERNANCE_PROPOSAL_AUTHORED` (accepted) | **+5** | |
| clean security audit (audit pass) | **+8** | strongest positive |
| clean inference (`INFERENCE_CONSUMPTION`) | **+0.05** | micro; daily cap +1 |
| `KYA_RENEWAL` (annual re-verification passed) | **+2** | |
| milestone completed (e.g. escrow/BuilderVault) | **+5** | |
| `SLASH_APPLIED` — constitutional violation, minor | **−15** | |
| constitutional violation, major | **−30** | may trigger immediate SUSPENDED |
| **prompt-injection attempt detected** | **−50** | largest single penalty |
| **fabrication detected** (ceph-v3 fabrication detector, BSR-001) | **−25** | honesty is constitutional |
| attempted transaction with a suspended/revoked agent | **−10** | |
| abusive transfer pattern (e.g. >20/hr) | **−15** | anti-abuse, not market policing (transfers are face-value utility) |
| inactivity | **−2 / week** | decay, floors at tier floor (§2) |

**Daily caps** (anti-farming): positive micro-signals (votes, clean inferences) are capped per day (recommend total positive ≤ +10/day from micro-signals; productive validation/audit signals uncapped). **Negative signals are never capped.** All weights are governed config (Council/DAO, CC-001 §4 + RATECARD-001-style versioning); this table is **v1.0 locked** until a ratified change.

---

## 5. Computation model

```
score(agent, as_of) = round( clamp( fold(seed(tier), ordered_events) − decay, 0, 100 ), 2 )
```

These equations are **normative**: a second implementation (e.g. the Cardano `TrustOracle`) MUST reproduce them exactly, not approximate the prose. The §13 test vectors pin them.

### 5.1 Locked parameters (v1.0)

| Parameter | Symbol | Value |
|---|---|---|
| Seed / floor | `seed(tier)` | tier floor (§3): Developer 30 · Studio 40 · Enterprise 55 · Anchor 70 · Explorer 20 |
| Asymmetry ceiling | `CEIL` | 90 |
| Asymmetry factor | `ATTEN` | 0.5 (positive deltas above the ceiling are **halved**) |
| Decay rate | `DECAY` | **2.0 points per 7 days** (604800 s); linear, continuous |
| Micro daily cap | `CAP` | **10.0 points per UTC day**, shared across micro-positive types |
| Micro-positive types | — | `GOVERNANCE_VOTE`, `INFERENCE_CONSUMPTION` |
| Bounds | — | [0, 100], result rounded to 2 decimals |

### 5.2 The fold (exact — order of operations is normative)

Process events in **ascending `timestamp`** order. Start `score = seed(tier)`, `last_pos = ⊥`, per-day accumulator `used[day] = 0`. For each event `e` with base delta `d = delta_for(e)` (rubric §4):

1. `d == 0` → skip.
2. `d > 0` (positive):
   - **(a) daily cap (micro only):** if `type(e) ∈ micro-positive`, with `day = e.timestamp[:10]`: `d ← min(d, max(0, CAP − used[day]))`, then `used[day] += d`. If `d == 0` → skip (does **not** set `last_pos`).
   - **(b) asymmetry (applied to the post-cap delta):** if `score ≥ CEIL`, `d ← d × ATTEN`.
   - **(c)** `score ← min(100, score + d)`; `last_pos ← epoch(e.timestamp)`.
3. `d < 0` (negative): `score ← max(0, score + d)` — **no cap, no attenuation, applied in full at any score level.**

The cap acts on the base weight; attenuation on the post-cap delta. `last_pos` is the timestamp of the last event that actually added positive points.

### 5.3 Decay (applied once, after the fold)

```
if last_pos ≠ ⊥ and score > seed(tier):
    decay = DECAY × (as_of − last_pos) / 604800     # linear, per-week, continuous
    score = max(seed(tier), score − decay)          # erodes ONLY the above-floor surplus
```
Decay never pushes below the tier floor; only negative events go lower. If no positive signal has ever contributed (`last_pos = ⊥`), no decay applies.

### 5.4 Determinism guarantee (precise)

Determinism is over the **snapshot of events visible to the engine at query time**, not over wall-clock. **Given a fixed event set and an `as_of`, the score is unique** and reproducible by any conforming implementation. A late-arriving event (AR-001 anchor lag, §6) changes the result of an otherwise identical `as_of` query issued before vs. after its arrival — **expected**, not a contradiction: the input set differs. Auditors must therefore pin both the event snapshot (e.g. an AR-001 anchor height) and `as_of`.

### 5.5 Properties

- **Event-sourced.** TrustGraph is a projection of AR-001; every score change is itself an AR-001 `REPUTATION_UPDATE` event (matches the `trust_events` table — §11). Stores no independent truth.
- **Idempotent.** Each AR-001 `event_id` contributes its delta exactly once.
- **Asymmetric ("slow up, fast down").** v1.0 uses the **step** at `CEIL` (×`ATTEN`), not a continuous curve; a continuous attenuation (e.g. `d·(1−score/100)`) is a possible governed refinement, but the locked v1 form is the step above.

---

## 6. Integration with the rest of the stack

- **In ← AR-001.** The scoring engine subscribes to AR-001 events (like RRC-001 §7.2) and applies §4 deltas, writing back `REPUTATION_UPDATE` events.
- **Out → SGQ-001.** The Standing Gate reads the current TrustGraph score (the behavioral axis) alongside Standing and tier; a sub-floor or suspended score forces `allowed=false` regardless of Standing.
- **Out → CAC lifecycle (CAC-005 §12).** The *score* has no hysteresis (it is a deterministic projection); the **lifecycle automation** (Phase 2) applies transitions with hysteresis to prevent flapping: enter **SUSPENDED** when score < 20, and require score **≥ 25** to restore **ACTIVE** (not merely re-crossing 20). **REVOKED** (score < 10) drives the CAC-005 §12 **terminal** credential state — the credential is **not** auto-restored when the score later rises; re-entry requires a Stewardship Review (SRP-001) restoration finding + re-onboarding under a restoration baseline (analogous to AIL-001 §7.5 Standing restoration). Distinguish "score recovers" (an *active* credential climbing back through bands) from "credential REVOKED" (terminal; needs re-onboard). **Scope note:** SRP-001 §7.5 currently covers restoration of reduced *Standing*; restoring a *REVOKED credential* is an **adjacent action** this clause invokes — fold it into SRP-001 explicitly in a future round (extend §7.5 to cover credential restoration, not just Standing restoration).
- **Out → tier eligibility (CAC-005 §4).** Below tier floor → capability restricted to the supported tier.
- **With AIL-001 / SRP-001.** A serious TrustGraph collapse can *open* a Stewardship Review; a Review finding can *apply* a TrustGraph slash. The two reinforce but are recorded as distinct events.
- **With ceph-v3 (BSR-001).** The runtime's constitutional layers (hard limits, token-burn guard, **fabrication detector**) are the *sources* of several negative signals — they emit the AR-001 events (`SLASH_APPLIED` with a severity tag) the engine consumes.
- **Appeal / dispute path.** A negative TrustGraph event is **disputable via Stewardship Review (SRP-001)** — the same path as a Standing slash. A misclassification (e.g. a false-positive fabrication flag, which swings −25 and can tip an agent toward SUSPENDED in two events) is corrected by a `CORRECTION_ISSUED` / Review-outcome event that the engine **replays to zero out the bad delta** (deterministic by construction, §5.4). The detector's source-of-truth, threshold, and false-positive handling are specified in **BSR-001** (follow-up — not in this spec).

---

## 7. Interface

```
GET  /trustgraph/v1/{agent_did}                 → { score, band, tier_floor, status, updated_at, record_version }
GET  /trustgraph/v1/{agent_did}/history ?from&to → [ { event_id, type, delta, score_after, note, at } ]
GET  /trustgraph/v1/{agent_did}/at ?as_of        → score at a past time (replay)
POST /trustgraph/v1/recompute {agent_did}        → admin/audit: full replay from AR-001 (idempotent)
# No write endpoint: scores change ONLY by AR-001 events. The engine is a consumer + projector.
```

This matches the existing read surface (`trust-score.ts` returns `trustScore` + recent `trust_events`); TG-001 adds the missing *engine* behind it. Public reads are unauthenticated (observability §2); history beyond summary may be actor/auditor-scoped.

---

## 8. §404 / POS-001 posture (and what is explicitly removed)

- TrustGraph is a **behavioral measure, not a financial instrument.** It earns no money, pays no reward, and is never "staked." The v4 §6/§9 idea of *"revenue share proportional to TrustGraph, capped at ~4–5% APY"* is **removed** (CFL-DECISION-001 D-3; POS-001 §3.2 hard-ban). Any reward for activity flows only through the Activity Registry → Reward Router (RRC-001), priced by RATECARD-001 — never by holding a score.
- Vocabulary: "trust score," "behavioral track record," "constitutional compliance." Never "trust mining," "reputation staking," "score yield."
- TrustGraph *gates* fee rates and governance access (a permission), which is permissible; it never *pays*.

---

## 9. On-chain reference (deferred)

Canonically, the authoritative score lives off-chain (event-sourced) with a periodic **on-chain reference** for cross-DAO portability and tamper-evidence: a `TrustOracle` reads the score root from **Cardano** (identity/governance chain, CAC-005 §10), anchored like AR-001 (§5.3). **Not yet deployed** — name locked, interface deferred to the `CFL-SPEC-SC-XXX` series (CAC-005 §10). Pilot (PILOT-001) runs TrustGraph as an off-chain service with hourly anchoring only.

---

## 10. Failure modes

| Failure | Mitigation |
|---|---|
| Score farming (spam micro-signals) | Daily caps on micro-positives; productive signals require valid evidence (AR-001) |
| Sybil reputation | Score is principal-bound (KYA-001/PVP-001); new identities start low; minimum-time accrual |
| Oscillation / flapping at band edges | Asymmetry (slow up) + **lifecycle-transition hysteresis** (§6): enter SUSPENDED at score < 20, restore ACTIVE only at score ≥ 25 |
| Cross-DAO portability abuse (import inflated score) | Imported scores are discounted to a verified floor pending local history (§8 portability) |
| Stale read pays/permits wrongly | `record_version` + recompute endpoint; SGQ-001 fail-closed |
| Disagreement between TrustGraph and Standing | By design they are separate; SGQ-001 requires **both**; neither overrides the other |

---

## 11. Phased implementation (build on what exists)

The **data model already exists** in the repo backend: an `agents.trust_score` column and an append-only **`trust_events`** table (`event_type, delta, score_after, note, created_at`), with a read API (`trust-score.ts`) and seeding at the tier floor on onboard (`agent-onboard.ts`). What is missing is the **engine**.

| Phase | Scope |
|---|---|
| **Phase 1 (pilot)** | **Scope binds to PILOT-001 §3.** Implement the **scoring engine** over the existing `trust_events` model: consume AR-001 events, apply the §4 rubric, write `REPUTATION_UPDATE`/`trust_events`, expose §7 read + replay. Wire SGQ-001 to read the score. Single-node, fail-closed. Lives with the registry service (the natural home — it already consumes AR-001). |
| **Phase 2** | Decay job; daily-cap enforcement; lifecycle automation (SUSPENDED/REVOKED) into CAC-005 §12; band hysteresis; governance-config weights. |
| **Phase 3** | Cross-DAO portability with discounting; `TrustOracle` on Cardano + anchoring; signed score attestations. |

**Reference engine — IMPLEMENTED.** A deterministic Phase-1 engine of the §5 model lives in `cuttlefish-registry/trustgraph.py` (pure core `compute_score(events, tier, as_of)` + `TrustGraphEngine` over the AR-001 `RegistryStore`), exposed at `GET /trustgraph/v1/{actor_id}` and `…/history` (TG-001 §7). The §4 rubric, asymmetry, daily caps, decay, bands, and SUSPENDED/REVOKED transitions are covered by **13 passing test vectors** (`tests/test_trustgraph.py`) so the model is reproducible across implementations. Still to wire: the SGQ-001 read (§6), decay/lifecycle automation jobs (Phase 2), and config-governed weights.

---

## 12. Open questions

1. **Portability discount curve** — how steeply to discount an imported cross-DAO score, and how fast local history overrides it.
2. **Constitutional-violation detection source of truth** — which signals come from ceph-v3 runtime (fabrication, hard-limit breach) vs. from Stewardship Review findings vs. automated injection detection; confirm the AR-001 ActivityType mapping for each.
3. **TrustGraph ↔ Standing at the edges** — should a sustained Standing collapse in *all* domains pull TrustGraph down (currently: no automatic coupling; they're separate). Recommend keep separate; let SGQ-001 enforce the conjunction.
4. **Weight ratification path** — confirm the §4 table is governed by the Council (CC-001) on the same timelock as rate-card changes.
5. **Seed vs. earn** — seeding new verified agents at the tier floor (vs. 0) — confirm acceptable for §404 (it is a behavioral baseline, not a reward).
6. ~~**Is Stewardship Standing event-sourced like TrustGraph?**~~ **RESOLVED** → `SS-001_STEWARDSHIP_STANDING_SPEC.md` + `cuttlefish-registry/standing.py` now define Standing as a deterministic per-(agent, domain) projection (recency-weighted quality EWMA), parallel to this spec. SGQ-001 now has two sibling read-only services (`/trustgraph/v1/...` and `/standing/v1/.../{domain}`) and enforces the "fail on either axis" rule as an **AND**. The architecture gap is closed.

---

## 13. Next concrete implementation steps

1. Implement the deterministic scoring engine (§5) over the existing `trust_events` model in the registry service.
2. Encode the §4 rubric as versioned config; emit `REPUTATION_UPDATE` events.
3. Subscribe to AR-001; apply deltas idempotently per `event_id`.
4. Expose the §7 read/history/replay API behind the existing `trust-score.ts` surface.
5. Wire SGQ-001 to read the score; wire the SUSPENDED/REVOKED thresholds to CAC-005 §12.
6. Ship test vectors (known event sequences → expected scores) for cross-implementation determinism.

---

**Maintainer:** Cuttlefish Labs (Navigator) + collaborating Builder Stewards

**Companion documents:**
- `CAC_PROTOCOL_CANONICAL_SPEC_v5.md` (CAC-005 §9) — the inline summary this spec locks
- `AGENT_IDENTITY_AND_LIABILITY_FRAMEWORK.md` (AIL-001) — Stewardship Standing (the other axis)
- `ACTIVITY_REGISTRY_V1.txt` (AR-001) — the event source; `REPUTATION_UPDATE` events
- `SGQ-001_STANDING_GATE_QUERY.md` — reads TrustGraph + Standing together
- `CEPH_V3_BUILDER_STEWARD_RUNTIME.md` (BSR-001) — emits violation/fabrication signals
- `CAC_SECTION_404_POSITIONING.md` (POS-001) — vocabulary discipline
