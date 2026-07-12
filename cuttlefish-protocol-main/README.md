# Cuttlefish Protocol

The canonical monorepo for the Cuttlefish Labs protocol stack — governance, identity, and the agent‑economy services.

## Layout

```
cuttlefish-protocol/
├── canon/                     # the canonical documentation stack (source of truth)
│   ├── 00_CANON_INDEX.md      # front door to the canon
│   ├── 00_NAMING_CONVENTIONS_INDEX.md, NAME_REGISTRY.md,
│   │   CFL-GLOSSARY-001_CANONICAL_GLOSSARY.md, RETIRED_BANNED_AND_GOTCHAS.md   # naming discipline
│   ├── CAC_PROTOCOL_CANONICAL_SPEC_v5.md (CAC-005), TG-001, SS-001, SGQ-001,
│   │   RRC-001, KYA-001, PVP-001, CC-001, EVS-001, RATECARD-001, PILOT-001,
│   │   KEY-001, APP-001, CFL-DECISION-001                                       # protocol specs
│   ├── CFL-NARR-003_TWO-LAYER_TRUSTGRAPH_ARCHITECTURE.md                        # runtime+engine TrustGraph stack
│   ├── 00_CONSTITUTION/        # constitutional layer (Constitution, Bill of Rights, TrustGraph doctrine, Ethical Kernel…)
│   └── CONSTITUTIONAL_ARCHIVE/ # verbatim, fixity-checked primary sources + finding aid
└── services/
    └── cuttlefish-registry/    # Activity Registry (AR-001) FastAPI service + engines
```

## Services — `cuttlefish-registry`

The append‑only Activity Registry (AR‑001) plus the deterministic engines it projects:

- `trustgraph.py` — **TrustGraph** (TG‑001): per‑agent behavioral 0–100 score.
- `standing.py` — **Stewardship Standing** (SS‑001): per‑(agent, domain) earned competence.
- `sgq.py` — **Standing Gate** (SGQ‑001): composes both axes — "may this actor be rewarded for this activity, now?" (fail on either axis).

46 tests. Requires `fastapi`, `uvicorn`, `pytest` in a virtualenv:

```
cd services/cuttlefish-registry
python -m pytest -q
uvicorn main:app --port 8081
```

## Naming discipline (read before editing any name)

Canonical names are **name‑locked**. See `canon/00_NAMING_CONVENTIONS_INDEX.md` and `canon/CFL-GLOSSARY-001_CANONICAL_GLOSSARY.md`. Do not rename, "align," or "clean up" a canonical name without Navigator direction.

---

**Navigator:** David Hans Elze · Cuttlefish Labs
