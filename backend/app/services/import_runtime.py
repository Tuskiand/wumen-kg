from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PendingImport:
    source: str
    source_case: str
    schema: str | None
    host_csv_path: str
    load_csv_uri: str
    node_count: int
    edge_count: int
    warnings: list[str]


PENDING_IMPORTS: dict[str, PendingImport] = {}
