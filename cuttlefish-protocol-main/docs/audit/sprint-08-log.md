# Sprint 8 — CC-001 Council anti-faction panel composition

**Branch:** `feat/sprint-08-council-panels` (stacked on `feat/sprint-07-ratecard`)
**Spec:** `canon/CC-001_COUNCIL_CHARTER.md`
**Status:** complete

## What was done
- `services/cuttlefish-registry/council.py` — the load-bearing anti-faction governance mechanics:
  - **`eligible_pool`** (§4 + §6): Senior+ Standing in the matter's domain, good standing, no active Stewardship Review, and not conflicted with any matter party (mandatory recusal).
  - **`compose_panel`** (§4/§5.1): **verifiable random draw** seeded by an AR-001 anchor hash — `random.Random(int(sha256(anchor_seed:matter_id), 16))` — uniform among the qualified pool, **not election**. No member chooses their panel. Principal-diversity cap prevents packing. Returns a `composition_hash` so anyone can re-run the draw and verify it (§7 / anti-seed-manipulation §107).
  - **`is_supermajority`** (§5.2.6): yes / (seated − recused) ≥ 2/3 (configurable fraction).
  - **`timelock_satisfied` / `takes_effect_at`** (§5.2.6): the 14–30 day window before a sensitive action takes effect (Navigator-veto window).

## Tests
`tests/test_council.py` — **12 vectors**: pool requires Senior+; excludes under-review/bad-standing; excludes conflicted (recusal); composition deterministic+verifiable; different matter → different draw; principal cap prevents packing; cap raisable; conflicted never selected; incomplete when pool too small; supermajority 2/3 (incl. recusal + no-effective-members); custom fraction; timelock window.
- `services/cuttlefish-registry` → **93 passed** (was 81; +12). pvp 13 / rrc 13 unchanged. **119 total.**

## Placeholders & open decisions
- `TODO(PROGRAMMER)`: read the candidate pool's Standing **live from the SS-001 engine** (taken as input here); seed `anchor_seed` from a real AR-001 §5.3 on-chain anchor hash; write panel composition + recusals to AR-001 (§7 transparency).
- `TODO(NAVIGATOR)`: confirm CC-001 §8 open questions — uniform vs Standing-weighted draw (uniform used, per §8 Q2 recommendation), cross-domain one-seat rule, principal-cap default (1 used), emergency-action expedited timelock, DAO-axis precedence.
- No-permanent-pairing (§5.2.1) is satisfied probabilistically by the random draw; explicit recent-pairing limits are not yet enforced — `TODO(NAVIGATOR)`.
