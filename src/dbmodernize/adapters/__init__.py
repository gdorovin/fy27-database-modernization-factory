"""Evidence adapters.

Each adapter converts one third-party export into normalized evidence records. Adapters
are the system's only ingestion point for untrusted data and are therefore the only place
that enforces size limits, path containment, and prompt-injection scanning.
"""

from __future__ import annotations

from dbmodernize.adapters.arc_sql_adapter import ArcSqlAdapter
from dbmodernize.adapters.azure_migrate_adapter import AzureMigrateAdapter
from dbmodernize.adapters.base import (
    MAX_RECORDS_PER_FILE,
    AdapterRegistry,
    EvidenceAdapter,
    default_registry,
)
from dbmodernize.adapters.csv_adapter import CsvInventoryAdapter
from dbmodernize.adapters.dms_adapter import DmsAdapter
from dbmodernize.adapters.ssma_adapter import SsmaAdapter

__all__ = [
    "MAX_RECORDS_PER_FILE",
    "AdapterRegistry",
    "ArcSqlAdapter",
    "AzureMigrateAdapter",
    "CsvInventoryAdapter",
    "DmsAdapter",
    "EvidenceAdapter",
    "SsmaAdapter",
    "default_registry",
]
