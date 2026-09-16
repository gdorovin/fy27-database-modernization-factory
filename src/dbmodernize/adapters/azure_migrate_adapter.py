"""Azure Migrate export adapter.

Reads the normalized subset of an Azure Migrate database assessment that this repository
depends on. The shape below is documented in ``docs/guidance/discovery-and-assessment.md``;
if a real export differs, change the adapter rather than the downstream contracts.

Readiness verdicts from the tool are recorded as evidence, never copied straight into a
recommendation. A tool saying "Ready" is an input to the decision, not the decision.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any, ClassVar

from dbmodernize.adapters.base import UNMAPPED_ATTRIBUTE, EvidenceAdapter
from dbmodernize.errors import UsageError
from dbmodernize.models.base import Confidence, EvidenceClass
from dbmodernize.models.evidence import EvidenceRecord, EvidenceSource
from dbmodernize.utils.io import read_json

_DOCUMENT_KEYS = frozenset({"assessedOn", "assessmentName", "databases"})
_DATABASE_KEYS = frozenset(
    {
        "databaseName",
        "instanceName",
        "sourcePlatform",
        "version",
        "edition",
        "sizeInGb",
        "environment",
        "readiness",
        "targetReadiness",
        "blockingIssues",
        "featuresInUse",
        "performance",
        "notes",
    }
)
_PERFORMANCE_KEYS = frozenset({"measured", "iops", "cpuCores", "memoryGb", "peakSessions"})


class AzureMigrateAdapter(EvidenceAdapter):
    source: ClassVar[EvidenceSource] = EvidenceSource.AZURE_MIGRATE
    name: ClassVar[str] = "azure-migrate"
    suffixes: ClassVar[tuple[str, ...]] = (".json",)

    def supports(self, path: Path) -> bool:
        if path.suffix.lower() not in self.suffixes:
            return False
        try:
            document = read_json(path)
        except UsageError:
            return False
        return isinstance(document, dict) and "databases" in document

    def extract(self, path: Path, engagement_id: str, collected_on: date) -> list[EvidenceRecord]:
        document = read_json(path)
        if not isinstance(document, dict):
            raise UsageError(f"{path}: expected a JSON object at the document root")

        assessed_on = self._parse_date(document.get("assessedOn"), collected_on)
        assessment = str(document.get("assessmentName", path.stem))
        records: list[EvidenceRecord] = []
        unmapped = self.unrecognised_keys(document, _DOCUMENT_KEYS)

        for index, entry in enumerate(document.get("databases", [])):
            if not isinstance(entry, dict):
                continue
            name = str(entry.get("databaseName") or entry.get("instanceName") or "").strip()
            if not name:
                continue

            performance = entry.get("performance") or {}
            unmapped |= self.unrecognised_keys(entry, _DATABASE_KEYS)
            unmapped |= self.unrecognised_keys(performance, _PERFORMANCE_KEYS, "performance.")
            measured = bool(performance.get("measured", False))
            attributes: dict[str, Any] = {
                "name": name,
                "source_platform": entry.get("sourcePlatform", "sql-server"),
                "source_version": entry.get("version"),
                "edition": entry.get("edition"),
                "data_size_gb": entry.get("sizeInGb"),
                "environment": entry.get("environment"),
                "tool_readiness": entry.get("readiness"),
                "tool_target_readiness": entry.get("targetReadiness", {}),
                "blocking_issues": [
                    {
                        "code": str(issue.get("code", "")),
                        "description": str(issue.get("description", "")),
                    }
                    for issue in entry.get("blockingIssues", [])
                    if isinstance(issue, dict)
                ],
                "instance_features": sorted(
                    str(feature) for feature in entry.get("featuresInUse", [])
                ),
                "measured": measured,
            }
            if performance:
                attributes["peak_iops"] = performance.get("iops")
                attributes["cpu_cores"] = performance.get("cpuCores")
                attributes["memory_gb"] = performance.get("memoryGb")
                attributes["peak_concurrent_sessions"] = performance.get("peakSessions")
            if unmapped:
                attributes[UNMAPPED_ATTRIBUTE] = sorted(unmapped)

            records.append(
                self._record(
                    engagement_id=engagement_id,
                    subject_id=self.workload_id(name),
                    subject_type="workload",
                    source_ref=f"{path.name}#databases[{index}] assessment={assessment}",
                    collected_on=assessed_on,
                    attributes={k: v for k, v in attributes.items() if v is not None},
                    evidence_class=EvidenceClass.OBSERVED,
                    confidence=Confidence.HIGH if measured else Confidence.MEDIUM,
                    notes=str(entry.get("notes")) if entry.get("notes") else None,
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


__all__ = ["AzureMigrateAdapter"]
