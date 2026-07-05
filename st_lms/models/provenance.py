from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(slots=True, frozen=True)
class Provenance:
    """Data lineage — melacak asal-usul snapshot."""

    source_layer: str          # Observe / Measure / Engine / dsb
    source_timestamp: int
    parent_snapshots: List[str]  # ID snapshot yang menjadi input
    pipeline_version: str = "1.0"

    def __post_init__(self) -> None:
        if self.source_timestamp < 0:
            raise ValueError("source_timestamp must be >= 0")
