"""Sqlite-backed Activity Registry store.

Implements AR-001 §6.3 Phase 1 pilot storage: single sqlite database with WAL mode,
append-only events table with indices. Hash chain per scope.

The core logic here mirrors `ceph-v3/observability/registry_client.py:LocalRegistryClient`
since both are Phase 0 stubs targeting the same schema. Once this service stabilizes,
ceph-v3 will switch to the HTTP client and remove its local copy.
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import time
import uuid
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


SCHEMA_VERSION = "1.0.0-stub"
DEFAULT_SCOPE = "cfl-main"


# ---------------------------------------------------------------- enums


class ActivityType(str, Enum):
    """AR-001 §3.3 ActivityType enum. Add new values here as they become
    reachable from runtime code."""

    # §404(iii) — use of service, governance, validation
    INFERENCE_CONSUMPTION = "INFERENCE_CONSUMPTION"
    GOVERNANCE_VOTE = "GOVERNANCE_VOTE"
    GOVERNANCE_PROPOSAL_AUTHORED = "GOVERNANCE_PROPOSAL_AUTHORED"
    GOVERNANCE_PROPOSAL_AMENDED = "GOVERNANCE_PROPOSAL_AMENDED"
    VALIDATION_COMPLETED = "VALIDATION_COMPLETED"
    VALIDATION_PEER_REVIEWED = "VALIDATION_PEER_REVIEWED"
    ATTESTATION_ISSUED = "ATTESTATION_ISSUED"
    ATTESTATION_REVOKED = "ATTESTATION_REVOKED"
    DISPUTE_RESOLUTION = "DISPUTE_RESOLUTION"
    KYA_RENEWAL = "KYA_RENEWAL"

    # §404(ii) — liquidity, collateral, risk-bearing
    LIQUIDITY_PROVISION = "LIQUIDITY_PROVISION"
    COLLATERAL_POSTED = "COLLATERAL_POSTED"
    COLLATERAL_RELEASED = "COLLATERAL_RELEASED"

    # §404(i) — payment, transfer, settlement
    PAYMENT_SETTLEMENT = "PAYMENT_SETTLEMENT"
    INTER_AGENT_TRANSFER = "INTER_AGENT_TRANSFER"

    # Internal protocol events
    CAC_ISSUANCE = "CAC_ISSUANCE"
    CAC_TOPUP = "CAC_TOPUP"
    CAC_BURN_INFERENCE = "CAC_BURN_INFERENCE"
    TIER_UPGRADE = "TIER_UPGRADE"
    REPUTATION_UPDATE = "REPUTATION_UPDATE"
    SLASH_APPLIED = "SLASH_APPLIED"
    CONTRIBUTION_CREDIT_ACCRUED = "CONTRIBUTION_CREDIT_ACCRUED"
    CONTRIBUTION_CREDIT_CONVERTED = "CONTRIBUTION_CREDIT_CONVERTED"

    # System events
    SCHEMA_MIGRATION = "SCHEMA_MIGRATION"
    REGISTRY_ANCHOR = "REGISTRY_ANCHOR"
    CORRECTION_ISSUED = "CORRECTION_ISSUED"

    # CCSP-001 spend protection events (proposed AR-001 revision)
    BUDGET_ENVELOPE_REFUSED = "BUDGET_ENVELOPE_REFUSED"
    BUDGET_OVERRIDE_REQUESTED = "BUDGET_OVERRIDE_REQUESTED"
    BUDGET_OVERRIDE_APPROVED = "BUDGET_OVERRIDE_APPROVED"
    BUDGET_HALT = "BUDGET_HALT"
    VELOCITY_HALT = "VELOCITY_HALT"

    # SRP-001 stewardship events
    STEWARDSHIP_REVIEW_INITIATED = "STEWARDSHIP_REVIEW_INITIATED"
    STEWARDSHIP_REVIEW_PANEL_FORMED = "STEWARDSHIP_REVIEW_PANEL_FORMED"
    STEWARDSHIP_REVIEW_DELIBERATION_OPENED = "STEWARDSHIP_REVIEW_DELIBERATION_OPENED"
    STEWARDSHIP_REVIEW_DELIBERATION_CLOSED = "STEWARDSHIP_REVIEW_DELIBERATION_CLOSED"
    STEWARDSHIP_REVIEW_OUTCOME = "STEWARDSHIP_REVIEW_OUTCOME"
    STANDING_ADJUSTED = "STANDING_ADJUSTED"
    DISCLOSURE_ISSUED = "DISCLOSURE_ISSUED"

    # CFL-NARR-003 §5 — Constitutional TrustGraph runtime detections.
    # Additive only: NOT wired to TG-001 score deltas (future Navigator ratification).
    SOCIAL_ENGINEERING_DETECTED = "SOCIAL_ENGINEERING_DETECTED"
    IDENTITY_FISHING_DETECTED = "IDENTITY_FISHING_DETECTED"
    COORDINATED_PROBING_DETECTED = "COORDINATED_PROBING_DETECTED"
    TRUST_MANIPULATION_DETECTED = "TRUST_MANIPULATION_DETECTED"
    IDENTITY_INCONSISTENCY_DETECTED = "IDENTITY_INCONSISTENCY_DETECTED"


class Section404Category(str, Enum):
    I = "i"
    II = "ii"
    III = "iii"
    NULL = "null"


# Mapping from AR-001 §3.4 + CCSP-001 / SRP-001 extensions
_S404_MAPPING: dict[ActivityType, tuple[Section404Category, str]] = {
    # §404(iii)
    ActivityType.INFERENCE_CONSUMPTION: (Section404Category.III, "use of any product or service"),
    ActivityType.GOVERNANCE_VOTE: (Section404Category.III, "participation in governance"),
    ActivityType.GOVERNANCE_PROPOSAL_AUTHORED: (Section404Category.III, "participation in governance"),
    ActivityType.GOVERNANCE_PROPOSAL_AMENDED: (Section404Category.III, "participation in governance"),
    ActivityType.VALIDATION_COMPLETED: (Section404Category.III, "validation … or other ecosystem participation"),
    ActivityType.VALIDATION_PEER_REVIEWED: (Section404Category.III, "validation … or other ecosystem participation"),
    ActivityType.ATTESTATION_ISSUED: (Section404Category.III, "validation … or other ecosystem participation"),
    ActivityType.ATTESTATION_REVOKED: (Section404Category.III, "validation … or other ecosystem participation"),
    ActivityType.DISPUTE_RESOLUTION: (Section404Category.III, "use of any product or service"),
    ActivityType.KYA_RENEWAL: (Section404Category.III, "loyalty, promotional, subscription, or incentive program"),
    # §404(ii)
    ActivityType.LIQUIDITY_PROVISION: (Section404Category.II, "providing liquidity for market-making activity"),
    ActivityType.COLLATERAL_POSTED: (Section404Category.II, "posting of collateral in connection with trading"),
    ActivityType.COLLATERAL_RELEASED: (Section404Category.II, "posting of collateral in connection with trading"),
    # §404(i)
    ActivityType.PAYMENT_SETTLEMENT: (Section404Category.I, "transaction, payment, transfer … in connection with the acceptance or use of a payment stablecoin"),
    ActivityType.INTER_AGENT_TRANSFER: (Section404Category.I, "transaction, payment, transfer …"),
}


def classify_404(activity_type: ActivityType) -> tuple[Section404Category, str]:
    return _S404_MAPPING.get(activity_type, (Section404Category.NULL, ""))


# ---------------------------------------------------------- canonical hash


def _canonical_json(payload: dict) -> str:
    """Phase 0 canonical JSON. TODO: replace with RFC 8785 per AR-001 §5.2."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def hash_evidence(payload: str | bytes | dict) -> str:
    if isinstance(payload, dict):
        return _sha256_hex(_canonical_json(payload))
    if isinstance(payload, bytes):
        return hashlib.sha256(payload).hexdigest()
    return _sha256_hex(str(payload))


# ----------------------------------------------------------- sqlite schema


_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS events (
    event_id              TEXT PRIMARY KEY,
    schema_version        TEXT NOT NULL,
    registry_scope        TEXT NOT NULL,
    prev_event_hash       TEXT NOT NULL,
    self_hash             TEXT NOT NULL,
    timestamp             TEXT NOT NULL,
    primary_actor_id      TEXT NOT NULL,
    activity_type         TEXT NOT NULL,
    section_404_category  TEXT NOT NULL,
    full_event_json       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_actor    ON events(primary_actor_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_events_type     ON events(activity_type, timestamp);
CREATE INDEX IF NOT EXISTS idx_events_scope    ON events(registry_scope, timestamp);
CREATE INDEX IF NOT EXISTS idx_events_404      ON events(section_404_category, timestamp);
"""


# -------------------------------------------------------------- store


def _iso_utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


class RegistryStore:
    """Sqlite-backed event store."""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self._db_path))
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(_SCHEMA_SQL)

    # ----------- writes

    def append_event(
        self,
        activity_type: ActivityType,
        primary_actor_id: str,
        activity_subject: dict,
        work_unit: dict,
        evidence_hash: str,
        evidence_uri: Optional[str],
        reward_eligibility: dict,
        registry_scope: str = DEFAULT_SCOPE,
        evidence_storage: str = "external",
    ) -> dict:
        event_id = str(uuid.uuid4())
        timestamp = _iso_utc_now()
        prev_hash = self.get_chain_head(registry_scope) or ""

        category, anchor = classify_404(activity_type)

        hashable_payload = {
            "event_id": event_id,
            "schema_version": SCHEMA_VERSION,
            "registry_scope": registry_scope,
            "prev_event_hash": prev_hash,
            "timestamp": timestamp,
            "primary_actor_id": primary_actor_id,
            "activity_type": activity_type.value,
            "activity_subject": activity_subject,
            "work_unit": work_unit,
            "evidence_hash": evidence_hash,
            "evidence_uri": evidence_uri,
            "evidence_storage": evidence_storage,
            "section_404_category": category.value,
            "statutory_anchor": anchor,
            "reward_eligibility": reward_eligibility,
        }
        self_hash = _sha256_hex(_canonical_json(hashable_payload))
        full_event = {**hashable_payload, "self_hash": self_hash}

        with self._conn() as conn:
            conn.execute(
                """
                INSERT INTO events (
                    event_id, schema_version, registry_scope,
                    prev_event_hash, self_hash, timestamp,
                    primary_actor_id, activity_type,
                    section_404_category, full_event_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id, SCHEMA_VERSION, registry_scope,
                    prev_hash, self_hash, timestamp,
                    primary_actor_id, activity_type.value,
                    category.value, json.dumps(full_event),
                ),
            )

        return full_event

    # ----------- reads

    def get_event(self, event_id: str) -> Optional[dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT full_event_json FROM events WHERE event_id = ?",
                (event_id,),
            ).fetchone()
        if not row:
            return None
        return json.loads(row[0])

    def list_events(
        self,
        actor_id: Optional[str] = None,
        activity_type: Optional[str] = None,
        scope: Optional[str] = None,
        section_404: Optional[str] = None,
        limit: int = 100,
    ) -> list[dict]:
        where = []
        params: list = []
        if actor_id:
            where.append("primary_actor_id = ?")
            params.append(actor_id)
        if activity_type:
            where.append("activity_type = ?")
            params.append(activity_type)
        if scope:
            where.append("registry_scope = ?")
            params.append(scope)
        if section_404:
            where.append("section_404_category = ?")
            params.append(section_404)
        where_clause = ("WHERE " + " AND ".join(where)) if where else ""
        params.append(limit)
        with self._conn() as conn:
            rows = conn.execute(
                f"""
                SELECT full_event_json FROM events
                {where_clause}
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                params,
            ).fetchall()
        return [json.loads(r[0]) for r in rows]

    def get_chain_head(self, scope: str = DEFAULT_SCOPE) -> str:
        with self._conn() as conn:
            row = conn.execute(
                """
                SELECT self_hash FROM events
                WHERE registry_scope = ?
                ORDER BY timestamp DESC
                LIMIT 1
                """,
                (scope,),
            ).fetchone()
        return row[0] if row else ""

    def compliance_report(
        self, actor_id: Optional[str], frm: str, to: str
    ) -> dict:
        """Per AR-001 §8.1 ComplianceReport — Phase 0 subset."""
        where = ["timestamp BETWEEN ? AND ?"]
        params: list = [frm, to]
        if actor_id:
            where.append("primary_actor_id = ?")
            params.append(actor_id)
        where_clause = " AND ".join(where)
        with self._conn() as conn:
            rows = conn.execute(
                f"""
                SELECT section_404_category, COUNT(*)
                FROM events
                WHERE {where_clause}
                GROUP BY section_404_category
                """,
                params,
            ).fetchall()
        counts = {"i": 0, "ii": 0, "iii": 0, "null": 0}
        for cat, n in rows:
            counts[cat] = n
        return {
            "period": {"from": frm, "to": to},
            "actor_scope": actor_id or "all",
            "event_counts_by_category": counts,
            "phase": "0-stub",
        }
