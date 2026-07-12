"""RRC-001 — idempotency + distribution log (in-memory, Phase-0).

Idempotency keyed on event_id (RRC-001 §4). TODO(PROGRAMMER): durable table (Postgres, §10 Phase 2).
"""

from __future__ import annotations

from typing import Optional


class RouterStore:
    def __init__(self) -> None:
        self._records: dict[str, list[dict]] = {}   # event_id -> distribution dicts

    def seen(self, event_id: str) -> bool:
        return event_id in self._records

    def record(self, event_id: str, distributions) -> None:
        self._records[event_id] = [d.model_dump() for d in distributions]

    def distributions(self, event_id: str) -> Optional[list[dict]]:
        return self._records.get(event_id)

    def size(self) -> int:
        return len(self._records)
