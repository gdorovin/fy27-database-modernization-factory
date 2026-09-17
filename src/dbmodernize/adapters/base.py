"""Adapter interface for third-party assessment exports.

Adapters are the only place untrusted input enters the system. They are deliberately
narrow: read a file, emit normalized evidence records, refuse anything oversized or
malformed. They never interpret text as instructions and never execute anything.
"""

from __future__ import annotations

import abc
from datetime import date
from pathlib import Path
from typing import Any, ClassVar

from dbmodernize.errors import UsageError
from dbmodernize.evidence.injection import scan_mapping
from dbmodernize.models.base import Classification, Confidence, EvidenceClass
from dbmodernize.models.evidence import EvidenceRecord, EvidenceSource
from dbmodernize.utils.hashing import slugify, stable_id

#: Hard ceiling on records produced from one file. A larger export should be split and
#: discussed, not silently absorbed.
MAX_RECORDS_PER_FILE = 5_000

#: Attribute naming input an adapter could not interpret. Set only when non-empty.
#:
#: Every adapter reads a documented subset of its format and ignores the rest. Ignoring is
#: fine; ignoring *invisibly* is not, because a field we failed to read is indistinguishable
#: downstream from a field the customer never provided. The assessment then reports a gap in
#: the estate that is really a gap in the adapter.
UNMAPPED_ATTRIBUTE = "unmapped_fields"


class EvidenceAdapter(abc.ABC):
    """Convert one export format into normalized evidence records."""

    source: ClassVar[EvidenceSource]
    name: ClassVar[str]
    #: File suffixes this adapter can read.
    suffixes: ClassVar[tuple[str, ...]] = ()

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in self.suffixes

    @abc.abstractmethod
    def extract(
        self,
        path: Path,
        engagement_id: str,
        collected_on: date,
    ) -> list[EvidenceRecord]:
        """Read ``path`` and return evidence records. Must not mutate anything."""

    def _record(
        self,
        *,
        engagement_id: str,
        subject_id: str,
        subject_type: str,
        source_ref: str,
        collected_on: date,
        attributes: dict[str, Any],
        evidence_class: EvidenceClass = EvidenceClass.OBSERVED,
        confidence: Confidence = Confidence.MEDIUM,
        notes: str | None = None,
    ) -> EvidenceRecord:
        """Build a record, scanning free text for directive-like content on the way in."""
        injection = scan_mapping(attributes)
        if notes:
            injection.extend(scan_mapping({"notes": notes}))
        return EvidenceRecord(
            id=stable_id("ev", self.name, subject_id, source_ref),
            engagement_id=engagement_id,
            subject_type=subject_type,
            subject_id=subject_id,
            source=self.source,
            source_ref=source_ref,
            collected_on=collected_on,
            evidence_class=evidence_class,
            classification=Classification.INTERNAL,
            confidence=confidence,
            attributes=attributes,
            notes=notes,
            injection_findings=injection,
        )

    @staticmethod
    def workload_id(name: str) -> str:
        return f"wl-{slugify(name)}"

    @staticmethod
    def unrecognised_keys(mapping: Any, known: frozenset[str], prefix: str = "") -> set[str]:
        """Keys present in the input that this adapter does not read.

        ``prefix`` names the nesting level (``"performance."``), so a reader can find the
        field in the source document rather than guessing which object it came from.
        """
        if not isinstance(mapping, dict):
            return set()
        return {f"{prefix}{key}" for key in mapping if key not in known}

    @staticmethod
    def _as_list(value: Any) -> list[Any]:
        """A list, or an empty list. ``"databases": null`` is malformed, not fatal."""
        return value if isinstance(value, list) else []

    @staticmethod
    def _as_dict(value: Any) -> dict[str, Any]:
        """A mapping, or an empty mapping. ``"performance": []`` must not crash the run."""
        return value if isinstance(value, dict) else {}

    @staticmethod
    def _as_int(value: Any, default: int = 0) -> int:
        """An integer, or ``default``. Untrusted input never earns a traceback."""
        if isinstance(value, bool):
            return int(value)
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
        if isinstance(value, str) and value.strip().lstrip("-").isdigit():
            return int(value.strip())
        return default

    @staticmethod
    def _guard_count(records: list[EvidenceRecord], path: Path) -> list[EvidenceRecord]:
        if len(records) > MAX_RECORDS_PER_FILE:
            raise UsageError(
                f"{path} produced {len(records)} records, above the "
                f"{MAX_RECORDS_PER_FILE} limit. Split the export."
            )
        return records


class AdapterRegistry:
    """Resolves a file to an adapter by explicit name or by suffix."""

    def __init__(self, adapters: list[EvidenceAdapter]) -> None:
        self._adapters = adapters

    @property
    def names(self) -> list[str]:
        return sorted(adapter.name for adapter in self._adapters)

    def by_name(self, name: str) -> EvidenceAdapter:
        for adapter in self._adapters:
            if adapter.name == name:
                return adapter
        raise UsageError(f"Unknown adapter {name!r}. Available: {', '.join(self.names)}")

    def for_path(self, path: Path) -> EvidenceAdapter | None:
        return next((a for a in self._adapters if a.supports(path)), None)


def default_registry() -> AdapterRegistry:
    from dbmodernize.adapters.arc_sql_adapter import ArcSqlAdapter
    from dbmodernize.adapters.azure_migrate_adapter import AzureMigrateAdapter
    from dbmodernize.adapters.csv_adapter import CsvInventoryAdapter
    from dbmodernize.adapters.dms_adapter import DmsAdapter
    from dbmodernize.adapters.ssma_adapter import SsmaAdapter

    return AdapterRegistry(
        [
            CsvInventoryAdapter(),
            AzureMigrateAdapter(),
            ArcSqlAdapter(),
            DmsAdapter(),
            SsmaAdapter(),
        ]
    )


__all__ = [
    "MAX_RECORDS_PER_FILE",
    "UNMAPPED_ATTRIBUTE",
    "AdapterRegistry",
    "EvidenceAdapter",
    "default_registry",
]
