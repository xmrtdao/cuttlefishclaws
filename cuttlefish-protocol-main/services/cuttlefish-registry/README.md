# cuttlefish-registry

**Phase 1 pilot Activity Registry service** per `CFL-SPEC-AR-001` §10.1.

Append-only, hash-chained event log. Sqlite-backed. Single-node. FastAPI HTTP API matching AR-001 §7.1. This service is the source of truth for every reward-eligible `ActivityEvent` in the Cuttlefish Labs ecosystem.

## Status

Phase 0 skeleton (May 2026). Implements the core write/read paths; does not yet implement:

- Cryptographic signatures (KYA registration flow blocked per `PRP-001` §12.2)
- Witness/consensus signatures for multi-validator events
- On-chain anchoring (AR-001 §5.3)
- Multi-storage evidence (currently just stores evidence hash; no IPFS/S3/Arweave integration)
- Multi-node consensus (Phase 3)
- Registry signing key (Phase 2)

What it **does** do:
- Accept `POST /registry/v1/events` with an unsigned event body, classify §404 category, compute self_hash, chain to previous event in scope, persist to sqlite.
- Serve `GET /registry/v1/events/{event_id}` and `GET /registry/v1/events` queries.
- Maintain scope chain heads per `AR-001` §5.1.
- Reject events that don't validate (missing fields, unrecognized activity_type, etc.).
- **Project the TrustGraph score** (`CFL-SPEC-TG-001`): `trustgraph.py` folds an agent's AR-001 events into a deterministic 0–100 behavioral score (seed at tier floor, asymmetric, decaying, daily-capped micro-positives, SUSPENDED/REVOKED bands). Read-only — the score changes **only** because events exist; it is behavioral, not financial (pays no reward).

## TrustGraph endpoints (TG-001 §7)

```
GET /trustgraph/v1/{actor_id}?tier=developer[&as_of=<epoch>]
    -> { score, band, status, tier, tier_floor, below_floor, last_positive_at, event_count }
GET /trustgraph/v1/{actor_id}/history?limit=100
    -> { agent, events: [ {event_id, activity_type, delta, at} ] }
```

`as_of` (epoch seconds) replays the score at a past time (deterministic). The §4 weight rubric is locked in TG-001; SGQ-001 (Standing Gate) reads this score alongside Stewardship Standing.

## Stewardship Standing endpoints (SS-001 §9)

The **competence axis** (sibling of TrustGraph). `standing.py` projects a per-`(agent, domain)` 0–100 Standing — a recency-weighted **quality average** (not a sum) of the agent's work events in that domain — with the value+time maturation ladder. **Cross-domain isolated** (SS-001 §3): each domain is computed only from its own events; a slash in `engineering_review` provably does not touch `arbitration_reliability`. Domain is carried in `work_unit.rubric_id`.

```
GET /standing/v1/{actor_id}                  -> { agent, domains: {<domain>: {standing, ladder_tier, provisional, ...}}, council_eligible }
GET /standing/v1/{actor_id}/{domain}         -> { standing, provisional, ladder_tier, time_in_domain_days, active_cap, council_eligible, ... }
GET /standing/v1/{actor_id}/{domain}/history -> { agent, domain, events: [...] }
```

Review/override events (SS-001 §6) carry `work_unit.unit ∈ {standing_cap, standing_set, standing_restore}` with `work_unit.quantity`.

## Standing Gate endpoints (SGQ-001)

The gate **composes both axes** and returns the AND — "may this actor be rewarded for this activity, now?". It computes nothing of its own; it reads the TrustGraph and Standing engines and decides. **Fail on either axis**: a perfect Standing with a SUSPENDED/REVOKED TrustGraph is blocked, and a healthy TrustGraph with no domain competence is blocked; every failing condition is listed (no silent denial). Lives at `/gate/v1` (the `/trustgraph/v1` and `/standing/v1` namespaces belong to the engines it composes).

```
POST /gate/v1/evaluate   {actor_kya_id, activity_type, domain, cac_tier, ial, as_of?, purpose?}
    -> { allowed, trustgraph:{...}, standing:{...}, cac_tier, ial, required:{...}, reasons:[...] }
GET  /gate/v1/thresholds ?activity_type=…&domain=…&tier=…   -> required.* the gate applies
```

## Quickstart

```powershell
# From this directory, using the ceph-v3 venv:
D:\CuttlefishLabs_Dev\Cuttlefish\ceph-v3\.venv\Scripts\python.exe -m uvicorn main:app --reload --port 8081
```

Service runs on `http://localhost:8081`. Open `http://localhost:8081/docs` for the auto-generated OpenAPI UI.

To point Ceph V3 at this service, set in its `.env`:

```
REGISTRY_BACKEND=http
REGISTRY_HTTP_ENDPOINT=http://localhost:8081
```

(Note: `HTTPRegistryClient` in ceph-v3 currently raises NotImplementedError — implementing it is a follow-up task once this service stabilizes.)

## Tests

```powershell
D:\CuttlefishLabs_Dev\Cuttlefish\ceph-v3\.venv\Scripts\python.exe -m pytest tests/
```

## Layout

```
main.py                   FastAPI app, route handlers (registry + trustgraph)
storage.py                Sqlite-backed event store (lifted from ceph-v3/observability/registry_client.py)
schema.py                 Pydantic request/response models
trustgraph.py             TrustGraph scoring engine (CFL-SPEC-TG-001) — behavioral axis
standing.py               Stewardship Standing engine (CFL-SPEC-SS-001) — competence axis (domain-bounded)
sgq.py                    Standing Gate (CFL-SPEC-SGQ-001) — composes both axes, the "fail on either" AND
tests/test_api.py         Endpoint tests using fastapi.testclient (13)
tests/test_trustgraph.py  TrustGraph engine test vectors (13)
tests/test_standing.py    Standing engine test vectors incl. cross-domain isolation (13)
tests/test_sgq.py         Standing Gate test vectors — fail-on-either-axis (7)
```

(46 tests total, all passing.)

## Companion documents

- `CFL-SPEC-AR-001` — Activity Registry specification (`ACTIVITY_REGISTRY_V1.txt`)
- `CFL-SPEC-TG-001` — TrustGraph (behavioral axis) — the model `trustgraph.py` implements
- `CFL-SPEC-SS-001` — Stewardship Standing (competence axis) — the model `standing.py` implements
- `CFL-SPEC-SGQ-001` — Standing Gate — `sgq.py` composes both axes (the "fail on either" AND)
- `CFL-SPEC-PRP-001` — Pipeline that consumes registry events
- `CFL-SPEC-BSR-001` — Bridge from Ceph V3 runtime to this service
- `CFL-SPEC-CCSP-001` — CAC card spend protection (consumes INFERENCE_CONSUMPTION events from this service)
