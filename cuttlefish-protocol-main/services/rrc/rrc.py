"""RRC-001 — Reward Router routing logic (Phase-1: Tiers 1-2 mocked, 3-4 stubbed).

Design invariant (RRC-001 §2, §6, §9):
  A reward is produced ONLY as a pure function of a discrete, classified activity event.
  There is intentionally NO balance read, NO elapsed-time computation, and NO scheduled job
  anywhere in this module — structurally incapable of §404(a)-prohibited yield.
  TODO(PROGRAMMER): add the CI static-analysis check that asserts this (RRC-001 §6).

Distribution is RECORD-ONLY in this skeleton — no funds move. Write-backs to the registry
are emitted through a mockable hook. TODO(PROGRAMMER): real settlement rails + SGQ-001 gate.
"""

from __future__ import annotations

from typing import Callable, Optional

from schema import DistributionRecord, InboundEvent, RouteResponse

# RRC-001 §5.1/§5.2 read these from RATECARD-001 (governed, versioned config). Mock values here.
# TODO(NAVIGATOR): replace with the real RATECARD-001 Appendix A values.
import ratecard

# RATECARD-001 — RRC reads the governed, versioned, timestamp-pinned card; it never invents
# amounts (RRC-001 §5.1). Values are placeholder until Council-ratified (RATECARD-001 §3).
RATE_CARD_REGISTRY = ratecard.DEFAULT_REGISTRY


def compute_usdc_amount(event: InboundEvent, card: ratecard.RateCard) -> float:
    rate = card.tier1_rate(event.activity_type)
    raw = rate.base * float(event.work_unit.quantity) * card.quality_multiplier(event.work_unit.quality_score)
    return round(max(rate.min, min(rate.per_event_cap, raw)), 6)


def compute_cac_units(event: InboundEvent, card: ratecard.RateCard) -> float:
    return float(card.tier2_credit_units(event.activity_type))


# --------------------------------------------------------------- registry write-back (mockable)

import os


REGISTRY_ENDPOINT = os.environ.get("REGISTRY_ENDPOINT", "http://localhost:8081")


def _default_emit(payload: dict) -> dict:
    import httpx
    resp = httpx.post(f"{REGISTRY_ENDPOINT}/registry/v1/events", json=payload, timeout=5.0)
    return {"status_code": resp.status_code}


emit_hook: Callable[[dict], dict] = _default_emit   # tests replace this


def emit_writeback(event_type: str, event: InboundEvent, detail: dict) -> dict:
    """RRC-001 §5/§7 — write the distribution back to AR-001 so the audit trail is closed-loop.

    TODO(PROGRAMMER): the write-back must itself be KYA-signed now that the registry write
    path requires signatures (Sprint 3), via a Router/registry system key."""
    payload = {
        "activity_type": event_type,
        "primary_actor_id": event.primary_actor_id,
        "activity_subject": {"type": "reward", "id": event.event_id},
        "work_unit": {"quantity": 1, "unit": "distribution"},
        "evidence_payload": {"source_event_id": event.event_id, **detail},
        "reward_eligibility": {},
    }
    return emit_hook(payload)


# --------------------------------------------------------------- routing (§4, §5)

def route(event: InboundEvent, store) -> RouteResponse:
    """RRC-001 §4 intake + idempotency gate, §5 per-tier routing. Pure + idempotent."""
    if store.seen(event.event_id):
        return RouteResponse(event_id=event.event_id, status="duplicate", distributions=[])

    dists: list[DistributionRecord] = []
    elig = event.reward_eligibility
    # RATECARD-001 §2 / RRC-001 §8 — pin the card version live at the event timestamp.
    card = RATE_CARD_REGISTRY.for_timestamp(event.timestamp)

    # Tier 1 — USDC activity reward (requires a non-null §404 category, §5.1)
    if elig.tier_1_usdc and event.section_404_category != "null":
        amount = compute_usdc_amount(event, card)
        emit_writeback("PAYMENT_SETTLEMENT", event, {"amount_usdc": amount})
        dists.append(DistributionRecord(
            tier="tier_1_usdc", kind="usdc_activity_reward", rail="utility", status="recorded",
            amount_usdc=amount, writeback_event_type="PAYMENT_SETTLEMENT",
            ratecard_version=card.version,
        ))

    # Tier 2 — CAC compute-credit top-up (§5.2)
    if elig.tier_2_cac:
        units = compute_cac_units(event, card)
        emit_writeback("CAC_TOPUP", event, {"credit_units": units})
        dists.append(DistributionRecord(
            tier="tier_2_cac", kind="cac_topup", rail="utility", status="recorded",
            credit_units=units, writeback_event_type="CAC_TOPUP",
            ratecard_version=card.version,
        ))

    # Tier 3 — governance upgrade: STUBBED, record-only (RRC-001 §10 Phase-1)
    if elig.tier_3_governance:
        dists.append(DistributionRecord(
            tier="tier_3_governance", kind="governance_upgrade_intent", rail="none", status="stubbed",
        ))

    # Tier 4 — $E2R contribution credit: STUBBED, SECURITIES rail, never the utility payment path (§5.4)
    if elig.tier_4_e2r:
        dists.append(DistributionRecord(
            tier="tier_4_e2r", kind="e2r_contribution_credit_intent", rail="securities", status="stubbed",
        ))

    store.record(event.event_id, dists)
    return RouteResponse(
        event_id=event.event_id,
        status="routed" if dists else "no_reward",
        distributions=dists,
    )
