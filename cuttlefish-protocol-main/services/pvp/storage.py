"""PVP-001 — in-memory store of verified principals (Phase-0).

TODO(PROGRAMMER): back with persistent storage; PII stays out of the registry (PVP-001 §7),
only verification_hash is anchored.
"""

from __future__ import annotations

from typing import Optional


class PrincipalStore:
    def __init__(self) -> None:
        self._records: dict[str, dict] = {}

    def put(self, principal_id: str, chain_dump: dict, result: dict) -> None:
        self._records[principal_id] = {
            "principal_chain": chain_dump,
            "verification_hash": result["verification_hash"],
            "ial_level": result["ial_level"],
            "attested_at": result["attested_at"],
            "jurisdiction": result["jurisdiction"],
            "status": "verified",
        }

    def get(self, principal_id: str) -> Optional[dict]:
        return self._records.get(principal_id)

    def revoke(self, principal_id: str) -> bool:
        rec = self._records.get(principal_id)
        if rec is None:
            return False
        rec["status"] = "lapsed"
        return True
