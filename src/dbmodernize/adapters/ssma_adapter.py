"""SQL Server Migration Assistant adapter for heterogeneous migrations.

SSMA reports conversion statistics per schema. The number that matters is not how much
converted automatically but how much did not: manual conversion and error counts are the
real signal, and they are what this adapter surfaces.

A high automatic-conversion percentage is never sufficient grounds to call a migration
compatible. Conversion is a code change, and code changes require application testing.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, ClassVar

from dbmodernize.adapters.base import EvidenceAdapter
from dbmodernize.errors import UsageError
from dbmodernize.models.base import Confidence, EvidenceClass
from dbmodernize.models.evidence import EvidenceRecord, EvidenceSource
from dbmodernize.utils.io import read_json


class SsmaAdapter(EvidenceAdapter):
    source: ClassVar[EvidenceSource] = EvidenceSource.SSMA
    name: ClassVar[str] = "ssma"
    suffixes: ClassVar[tuple[str, ...]] = (".json",)

    def supports(self, path: Path) -> bool:
        if path.suffix.lower() not in self.suffixes:
            return False
        try:
            document = read_json(path)
        except UsageError:
            return False
        return isinstance(document, dict) and "schemas" in document

    def extract(self, path: Path, engagement_id: str, collected_on: date) -> list[EvidenceRecord]:
        document = read_json(path)
        if not isinstance(document, dict):
            raise UsageError(f"{path}: expected a JSON object at the document root")

        converted_on = self._parse_date(document.get("convertedOn"), collected_on)
        project = str(document.get("project", path.stem))
        records: list[EvidenceRecord] = []

        for index, schema in enumerate(document.get("schemas", [])):
            if not isinstance(schema, dict):
                continue
            name = str(schema.get("workloadName") or schema.get("sourceSchema") or "").strip()
            if not name:
                continue

            summary = schema.get("conversionSummary") or {}
            automatic = int(summary.get("automatic", 0))
            manual = int(summary.get("manual", 0))
            errors = int(summary.get("errors", 0))
            total = automatic + manual + errors

            attributes: dict[str, Any] = {
                "name": name,
                "source_platform": schema.get("sourcePlatform", "oracle"),
                "source_schema": schema.get("sourceSchema"),
                "assessed_target": schema.get("targetPlatform"),
                "object_counts": schema.get("objects", {}),
                "conversion_automatic": automatic,
                "conversion_manual": manual,
                "conversion_errors": errors,
                "conversion_total": total,
                # Reported for transparency. It is not a compatibility verdict.
                "conversion_automatic_percent": (
                    round(100.0 * automatic / total, 1) if total else None
                ),
                "manual_effort_hours": schema.get("manualEffortHours"),
                "top_issues": [
                    {
                        "category": str(issue.get("category", "")),
                        "description": str(issue.get("description", "")),
                        "occurrences": issue.get("occurrences", 0),
                    }
                    for issue in schema.get("topIssues", [])
                    if isinstance(issue, dict)
                ],
                "measured": True,
            }
            records.append(
                self._record(
                    engagement_id=engagement_id,
                    subject_id=self.workload_id(name),
                    subject_type="workload",
                    source_ref=f"{path.name}#schemas[{index}] project={project}",
                    collected_on=converted_on,
                    attributes={k: v for k, v in attributes.items() if v is not None},
                    evidence_class=EvidenceClass.OBSERVED,
                    confidence=Confidence.HIGH,
                    notes=(
                        "Conversion statistics describe tool output only. They say nothing "
                        "about whether the converted code behaves identically, which requires "
                        "application testing."
                    ),
                )
            )
        return self._guard_count(records, path)

    @staticmethod
    def _parse_date(value: object, fallback: date) -> date:
        if isinstance(value, str):
            try:
                return date.fromisoformat(value[:10])
            except ValueError:
                return fallback
        return fallback


__all__ = ["SsmaAdapter"]
