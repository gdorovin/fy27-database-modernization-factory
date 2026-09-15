"""CSV inventory adapter.

The lowest-common-denominator input: a spreadsheet someone exported from a CMDB. It is
the most common starting point and the least trustworthy, so every value it produces is
marked ``user-provided`` unless the column explicitly says it was measured.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, ClassVar

from dbmodernize.adapters.base import EvidenceAdapter
from dbmodernize.models.base import Confidence, EvidenceClass
from dbmodernize.models.evidence import EvidenceRecord, EvidenceSource
from dbmodernize.utils.io import read_csv_rows

#: Accepted header spellings mapped to the normalized attribute key.
COLUMN_MAP: dict[str, str] = {
    "workload": "name",
    "workload_name": "name",
    "database": "name",
    "database_name": "name",
    "name": "name",
    "platform": "source_platform",
    "source_platform": "source_platform",
    "engine": "source_platform",
    "version": "source_version",
    "source_version": "source_version",
    "edition": "edition",
    "environment": "environment",
    "criticality": "criticality",
    "host": "host_alias",
    "host_alias": "host_alias",
    "size_gb": "data_size_gb",
    "data_size_gb": "data_size_gb",
    "largest_table_gb": "largest_table_gb",
    "cpu_cores": "cpu_cores",
    "memory_gb": "memory_gb",
    "peak_iops": "peak_iops",
    "peak_sessions": "peak_concurrent_sessions",
    "growth_percent": "annual_growth_percent",
    "rpo_minutes": "rpo_minutes",
    "rto_minutes": "rto_minutes",
    "max_downtime_minutes": "max_planned_downtime_minutes",
    "availability_target": "availability_target",
    "features": "instance_features",
    "instance_features": "instance_features",
    "extensions": "extensions",
    "dependencies": "dependency_names",
    "deps_confirmed": "dependency_discovery_complete",
    "dependency_discovery_complete": "dependency_discovery_complete",
    "sla_stated_by": "service_level_stated_by",
    "compliance": "compliance_scopes",
    "compliance_scopes": "compliance_scopes",
    "data_residency": "data_residency",
    "owner": "owner_role",
    "notes": "notes",
    "measured": "measured",
}

_LIST_FIELDS = frozenset(
    {"instance_features", "extensions", "dependency_names", "compliance_scopes"}
)
_FLOAT_FIELDS = frozenset(
    {"data_size_gb", "largest_table_gb", "memory_gb", "annual_growth_percent"}
)
_INT_FIELDS = frozenset(
    {
        "cpu_cores",
        "peak_iops",
        "peak_concurrent_sessions",
        "rpo_minutes",
        "rto_minutes",
        "max_planned_downtime_minutes",
    }
)
_TRUTHY = frozenset({"true", "yes", "y", "1"})
_BOOL_FIELDS = frozenset({"measured", "dependency_discovery_complete"})


class CsvInventoryAdapter(EvidenceAdapter):
    source: ClassVar[EvidenceSource] = EvidenceSource.CSV_INVENTORY
    name: ClassVar[str] = "csv-inventory"
    suffixes: ClassVar[tuple[str, ...]] = (".csv",)

    def extract(self, path: Path, engagement_id: str, collected_on: date) -> list[EvidenceRecord]:
        rows = read_csv_rows(path)
        records: list[EvidenceRecord] = []

        for index, row in enumerate(rows, start=2):  # row 1 is the header
            attributes = self._map_row(row)
            name = str(attributes.get("name", "")).strip()
            if not name:
                continue

            measured = bool(attributes.pop("measured", False))
            notes = attributes.pop("notes", None)
            records.append(
                self._record(
                    engagement_id=engagement_id,
                    subject_id=self.workload_id(name),
                    subject_type="workload",
                    source_ref=f"{path.name}#row={index}",
                    collected_on=collected_on,
                    attributes={**attributes, "measured": measured},
                    # A spreadsheet is what a human believes, not what a tool observed.
                    evidence_class=(
                        EvidenceClass.OBSERVED if measured else EvidenceClass.USER_PROVIDED
                    ),
                    confidence=Confidence.MEDIUM if measured else Confidence.LOW,
                    notes=str(notes) if notes else None,
                )
            )
        return self._guard_count(records, path)

    def _map_row(self, row: dict[str, str]) -> dict[str, Any]:
        attributes: dict[str, Any] = {}
        for raw_key, raw_value in row.items():
            key = COLUMN_MAP.get(raw_key.strip().lower())
            if key is None or raw_value == "":
                continue
            attributes[key] = self._coerce(key, raw_value)
        return attributes

    @staticmethod
    def _coerce(key: str, value: str) -> Any:
        if key in _LIST_FIELDS:
            return sorted({item.strip() for item in value.split(";") if item.strip()})
        if key in _BOOL_FIELDS:
            return value.strip().lower() in _TRUTHY
        if key in _FLOAT_FIELDS:
            try:
                return float(value)
            except ValueError:
                return value
        if key in _INT_FIELDS:
            try:
                return int(float(value))
            except ValueError:
                return value
        return value


__all__ = ["COLUMN_MAP", "CsvInventoryAdapter"]
