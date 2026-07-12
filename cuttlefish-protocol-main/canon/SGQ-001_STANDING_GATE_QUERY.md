# Standing Gate Query Service Specification v1.0

**Cuttlefish Labs — CAC Protocol**
**The single service that answers "may this actor be rewarded for this activity, now?"**

---

**Document ID:** CFL-SPEC-SGQ-001
**Version:** 1.0 (draft)
**Date:** 2026-06-27
**Status:** Architectural spec, pre-implementation
**Companion to:** CFL-SPEC-AIL-001 (Stewardship Standing), CFL-SPEC-AR-001 (write-path validation), CFL-SPEC-KYA-001 (§5 standing gate), CFL-SPEC-RRC-001 (§6 standing gate)
**Classification:** Internal + AI Ethics Group deliverable
**Conforms to:** CFL-DECISION-001 (Builder Stewards; §404 activity model; POS-001 vocabulary)

---

## 1. Why this exists

Three canonical docs reference a "standing gate" / "Standing is queried" but none defined the service:
- `CAC-005` §6 (Standing is queryable), `KYA-001` §5 ("Standing is queried, not stored in the signature"), `RRC-001` §6 ("Standing gate before any tier pays"), and the `AR-001` write-path step 5 ("actor has KYA standing required for activity_type").

This spec defines **one** service so those three call the same authority. The Standing Gate is the single point that answers, deterministically and against the *current* record:

> **Is actor `A` entitled — by Stewardship Standing, CAC tier, and identity assurance — to perform (and be rewarded for) `activity_type` in `domain`, as of time `T`?**

Standing lives in AIL-001; this is the **read interface** over it (plus CAC tier and IAL), not a new source of truth.

**Two-axis gate (reconciliation — this spec predates TG-001 and SS-001).** The gate now composes **both** governance axes and enforces the "fail on either axis" rule (TG-001 §1):
- **TrustGraph** (TG-001) — *behavioral*: may the agent act **at all**? A SUSPENDED/REVOKED or below-tier-floor score blocks, regardless of competence.
- **Stewardship Standing** (SS-001) — *competence*: is the agent **entitled in this domain** at the required ladder tier?

Both are read-only deterministic projections of AR-001 (live as `/trustgraph/v1/...` and `/standing/v1/.../{domain}` on the registry service). The gate reads both and **ANDs** them with the CAC-tier and IAL checks.

---

## 2. Inputs and decision

```
GateQuery {
    actor_kya_id:   KYA_ID
    activity_type:  ActivityType        // AR-001 §3.3
    domain:         string              // e.g. governance_review, engineering_review
    cac_tier:       enum[explorer, developer, studio, enterprise, anchor]
    ial:            enum[IAL2, IAL3]    // from the actor's KYA binding (KYA-001)
    as_of:          epoch | ISO-8601    // evaluate against the record at this time
    purpose:        enum[write, reward, attest]   // who is asking (AR-001 / RRC-001 / panel)
}

GateDecision {
    allowed:        bool
    trustgraph:     { score, band, status, below_floor }        // TG-001 — behavioral axis
    standing:       { domain, value, ladder_tier, provisional } // SS-001 — competence axis
    cac_tier, ial
    required:       { min_trust_status, min_trust_score,
                      min_standing, min_ladder_tier, min_cac_tier, min_ial }
    reasons:        List[string]        // EVERY failing/limiting condition (no silent denial)
    purpose
    evaluated_at, as_of
}
```

A request is `allowed` only if **ALL** hold (the AND):
1. **TrustGraph axis (TG-001):** `status ∉ {SUSPENDED, REVOKED}` **and** not `below_floor` for the agent's tier **and** `score ≥ required.min_trust_score`.
2. **Standing axis (SS-001):** `standing.value ≥ required.min_standing` in `domain` **and** `ladder_tier ≥ required.min_ladder_tier` **and** (not `provisional` where a non-provisional tier is required).
3. **Tier:** `cac_tier ≥ required.min_cac_tier`.
4. **Identity:** `ial ≥ required.min_ial`.
5. No active Stewardship Review/suspension (AIL-001 §6, SRP-001) — surfaced via the TrustGraph status and a Standing cap.

A failure on **any** axis sets `allowed=false` and `reasons` lists **every** failing condition (so a caller sees the full picture, not the first failure).

---

## 3. Evaluation rules

1. **Current-record evaluation.** Standing is read live; a Steward whose Standing was slashed cannot earn on new events (KYA-001 §5). For `as_of` in the past (audit), the service replays the Standing snapshot at that time from AR-001 Standing-adjustment events.
2. **Domain-bounded.** Standing is per-domain (AIL-001 §4); a query in a domain where the actor has no Standing returns the floor (Contributor) for that domain.
3. **Thresholds come from the rubric.** `required.*` is resolved from the domain rubric + tier table (CAC-005 §4) + the activity-type minimums; thresholds are governed config (Council/DAO), never hard-coded here.
4. **Suspension overrides.** An active Stewardship Review or suspension forces `allowed=false` regardless of accumulated Standing — surfaced via the TrustGraph `status` (SUSPENDED/REVOKED) and/or a Standing cap (SS-001 §6).
5. **Two-axis read.** The gate reads the **TrustGraph** projection (TG-001) and the per-domain **Standing** projection (SS-001) for the same `as_of`, plus the actor's `cac_tier` and `ial`, and returns the AND of §2. Both projections are deterministic over the event snapshot (TG-001 §5.4 / SS-001 §7.2), so the gate decision is reproducible for a pinned snapshot + `as_of`. The gate **computes no trust/standing of its own** — it composes the two engines.

---

## 4. Interface

The gate lives at the **`/gate/v1`** namespace (the `/standing/v1` and `/trustgraph/v1` namespaces belong to the SS-001 and TG-001 engines it composes — kept separate to avoid the route collision):

```
POST /gate/v1/evaluate       Body: GateQuery                       → GateDecision
GET  /gate/v1/thresholds     ?activity_type=…&domain=…&tier=…      → required.* (config snapshot)
GET  /gate/v1/health                                               → freshness, version
```

(Per-domain Standing and the TrustGraph score are read directly from `/standing/v1/.../{domain}` and `/trustgraph/v1/...`; the gate does not duplicate those reads as endpoints.)

- **Read-only.** SGQ never *writes* trust or Standing; both change only via AR-001 events produced elsewhere (Review outcomes, attestations). SGQ only reads the two projections and decides.
- **Callers:** AR-001 write path (`purpose=write`), RRC-001 before each tier pays (`purpose=reward`), review/attestation panels (`purpose=attest`).
- **Caching:** decisions may be cached briefly but MUST carry `record_version`; a Standing change invalidates prior decisions for affected actors.

---

## 5. §404 / vocabulary posture

The Standing Gate is what makes "rewarded only for entitled, verified activity" enforceable — there is no path to reward an actor without a passing decision. It evaluates **earned Stewardship Standing**, never stake or balance. Output language is POS-001-compliant (no "validator score," no "stake"); the ladder tiers are Contributor / Builder Steward / Senior / Council.

---

## 6. Failure modes

| Failure | Mitigation |
|---|---|
| Stale Standing read pays a slashed Steward | `record_version` + cache invalidation on Standing change |
| Threshold drift between callers | Single `/thresholds` source; callers never hard-code minimums |
| Service down blocks all rewards | Fail-closed for `write`/`reward` (no event/no pay), with alerting; never fail-open |
| Past-time audit mismatch | Snapshot replay from AR-001 Standing events, deterministic |

---

## 7. Phased implementation

| Phase | Scope |
|---|---|
| **Phase 1 (pilot)** | **Scope binds to PILOT-001 §3.** Compose the TG-001 + SS-001 engines in-process; `POST /gate/v1/evaluate` + `GET /gate/v1/thresholds`; config-default thresholds; fail-closed. |
| **Phase 2** | Snapshot replay for audit `as_of`; cache + invalidation; rubric-driven thresholds wired to Council governance. |
| **Phase 3** | High-availability, signed decisions (so a caller can prove the gate's answer), cross-node consistency. |

**Reference implementation — IMPLEMENTED.** `cuttlefish-registry/sgq.py` composes the TrustGraph and Standing engines into the §2 AND, exposed at `/gate/v1/evaluate` + `/gate/v1/thresholds`. **7 test vectors** (`tests/test_sgq.py`) pin "fail on either axis": a perfect Standing with a REVOKED TrustGraph is blocked; a healthy TrustGraph with no domain competence is blocked; tier/IAL failures are caught; and every failing reason is surfaced (no silent denial). Still to do: snapshot-replay caching (Phase 2), signed decisions (Phase 3), Council-governed thresholds.

---

## 8. Open questions

1. **Signed decisions** — should SGQ sign its `StandingDecision` so RRC-001/AR-001 can prove the gate authorized a payout? Recommend yes by Phase 3.
2. **Domain taxonomy ownership** — where is the canonical domain list (governance_review, engineering_review, …) maintained? Recommend: Council-governed registry, referenced here.
3. **Threshold-change timelock** — Council changes to `required.*` should respect the CC-001 §4 supermajority + timelock; confirm SGQ reads only ratified thresholds.

---

**Maintainer:** Cuttlefish Labs (Navigator) + collaborating Builder Stewards
**Companion documents:** `TG-001` (behavioral axis it reads), `SS-001` (competence axis it reads), AIL-001 (Standing model), AR-001 (write-path), KYA-001 (§5 — supplies `cac_tier`/`ial`), RRC-001 (§6 caller), `RATECARD-001` (reward thresholds vocabulary), CC-001 (threshold governance), POS-001 (vocabulary).
