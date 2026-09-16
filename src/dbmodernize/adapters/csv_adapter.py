"""CSV inventory adapter.

The lowest-common-denominator input: a spreadsheet someone exported from a CMDB. It is
the most common starting point and the least trustworthy, so every value it produces is
marked ``user-provided`` unless the column explicitly says it was measured.

A column this adapter cannot map is reported, never dropped in silence. Silently dropping
``Recovery Point Objective (min)`` would make the assessment say "no recovery objective
stated", which reads as a finding about the customer's estate when it is really a finding
about this file.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any, ClassVar

from dbmodernize.adapters.base import UNMAPPED_ATTRIBUTE, EvidenceAdapter
from dbmodernize.models.base import Confidence, EvidenceClass
from dbmodernize.models.evidence import EvidenceRecord, EvidenceSource
from dbmodernize.utils.io import read_csv_rows

#: Accepted header spellings mapped to the normalized attribute key. Headers are
#: normalized before lookup, so ``Data Size (GB)``, ``data-size-gb`` and ``DATA_SIZE_GB``
#: all reach one entry, and only genuinely unknown columns need listing here.
COLUMN_MAP: dict[str, str] = {
    "workload": "name",
    "workload_name": "name",
    "database": "name",
    "database_name": "name",
    "db_name": "name",
    "name": "name",
    "platform": "source_platform",
    "source_platform": "source_platform",
    "engine": "source_platform",
    "dbms": "source_platform",
    "version": "source_version",
    "source_version": "source_version",
    "engine_version": "source_version",
    "edition": "edition",
    "environment": "environment",
    "env": "environment",
    "criticality": "criticality",
    "business_criticality": "criticality",
    "host": "host_alias",
    "host_alias": "host_alias",
    "hostname": "host_alias",
    "server": "host_alias",
    "size_gb": "data_size_gb",
    "data_size_gb": "data_size_gb",
    "database_size_gb": "data_size_gb",
    "largest_table_gb": "largest_table_gb",
    "cpu_cores": "cpu_cores",
    "cores": "cpu_cores",
    "vcpu": "cpu_cores",
    "memory_gb": "memory_gb",
    "ram_gb": "memory_gb",
    "peak_iops": "peak_iops",
    "iops": "peak_iops",
    "peak_sessions": "peak_concurrent_sessions",
    "peak_concurrent_sessions": "peak_concurrent_sessions",
    "growth_percent": "annual_growth_percent",
    "annual_growth_percent": "annual_growth_percent",
    "rpo_minutes": "rpo_minutes",
    "rpo_min": "rpo_minutes",
    "recovery_point_objective_min": "rpo_minutes",
    "rto_minutes": "rto_minutes",
    "rto_min": "rto_minutes",
    "recovery_time_objective_min": "rto_minutes",
    "max_downtime_minutes": "max_planned_downtime_minutes",
    "max_planned_downtime_minutes": "max_planned_downtime_minutes",
    "availability_target": "availability_target",
    "sla": "availability_target",
    "features": "instance_features",
    "instance_features": "instance_features",
    "extensions": "extensions",
    "dependencies": "dependency_names",
    "dependency_names": "dependency_names",
    "deps_confirmed": "dependency_discovery_complete",
    "dependency_discovery_complete": "dependency_discovery_complete",
    "sla_stated_by": "service_level_stated_by",
    "service_level_stated_by": "service_level_stated_by",
    "compliance": "compliance_scopes",
    "compliance_scopes": "compliance_scopes",
    "data_residency": "data_residency",
    "owner": "owner_role",
    "owner_role": "owner_role",
    "notes": "notes",
    "measured": "measured",
}

#: Columns that are common in CMDB exports and carry no decision value. Discarding these
#: on purpose is a different act from failing to recognise a column, and only the second
#: is worth anyone's attention.
IGNORED_COLUMNS: frozenset[str] = frozenset(
    {
        "row",
        "id",
        "row_id",
        "cmdb_id",
        "asset_tag",
        "ticket",
        "last_updated",
        "updated_by",
        "cost_centre",
        "cost_center",
    }
)

_NON_ALPHANUMERIC = re.compile(r"[^a-z0-9]+")

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
        unmapped = self._unmapped_headers(rows)

        for index, row in enumerate(rows, start=2):  # row 1 is the header
            attributes = self._map_row(row)
            name = str(attributes.get("name", "")).strip()
            if not name:
                continue

            measured = bool(attributes.pop("measured", False))
            notes = attributes.pop("notes", None)
            if unmapped:
                attributes[UNMAPPED_ATTRIBUTE] = unmapped
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

    def _unmapped_headers(self, rows: list[dict[str, str]]) -> list[str]:
        """Headers this adapter did not recognise, in the spelling the author used."""
        if not rows:
            return []
        unmapped = {
            header
            for header in rows[0]
            if (normalized := self._normalize_header(header))
            and normalized not in COLUMN_MAP
            and normalized not in IGNORED_COLUMNS
        }
        return sorted(unmapped)

    def _map_row(self, row: dict[str, str]) -> dict[str, Any]:
        attributes: dict[str, Any] = {}
        for raw_key, raw_value in row.items():
            key = COLUMN_MAP.get(self._normalize_header(raw_key))
            if key is None or raw_value == "":
                continue
            attributes[key] = self._coerce(key, raw_value)
        return attributes

    @staticmethod
    def _normalize_header(header: str) -> str:
        """Fold spelling variations so only genuinely unknown columns look unknown."""
        return _NON_ALPHANUMERIC.sub("_", header.strip().lower()).strip("_")

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


__all__ = ["COLUMN_MAP", "IGNORED_COLUMNS", "CsvInventoryAdapter"]
