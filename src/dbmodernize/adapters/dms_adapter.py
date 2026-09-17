"""Azure Database Migration Service assessment adapter.

DMS assessments are per target platform. That matters: a database can be "ready" for one
target and blocked for another, so the adapter keeps the target dimension instead of
flattening it into a single readiness verdict.
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

_DOCUMENT_KEYS = frozenset({"assessedOn", "results"})
_RESULT_KEYS = frozenset(
    {
        "databaseName",
        "targetPlatform",
        "featureParity",
        "compatibilityIssues",
        "sourcePlatform",
        "sourceVersion",
    }
)


class DmsAdapter(EvidenceAdapter):
    source: ClassVar[EvidenceSource] = EvidenceSource.DATA_MIGRATION_SERVICE
    name: ClassVar[str] = "dms"
    suffixes: ClassVar[tuple[str, ...]] = (".json",)

    def supports(self, path: Path) -> bool:
        if path.suffix.lower() not in self.suffixes:
            return False
        try:
            document = read_json(path)
        except UsageError:
            return False
        return isinstance(document, dict) and "results" in document

    def extract(self, path: Path, engagement_id: str, collected_on: date) -> list[EvidenceRecord]:
        document = read_json(path)
        if not isinstance(document, dict):
            raise UsageError(f"{path}: expected a JSON object at the document root")

        assessed_on = self._parse_date(document.get("assessedOn"), collected_on)
        records: list[EvidenceRecord] = []
        results = [r for r in self._as_list(document.get("results")) if isinstance(r, dict)]
        unmapped = self.unrecognised_keys(document, _DOCUMENT_KEYS)
        for result in results:
            unmapped |= self.unrecognised_keys(result, _RESULT_KEYS)

        for index, result in enumerate(results):
            name = str(result.get("databaseName", "")).strip()
            if not name:
                continue

            parity = [
                {
                    "feature": str(item.get("feature", "")),
                    "severity": str(item.get("severity", "medium")),
                    "description": str(item.get("description", "")),
                }
                for item in self._as_list(result.get("featureParity"))
                if isinstance(item, dict)
            ]
            compatibility = [
                {
                    "rule_id": str(item.get("ruleId", "")),
                    "severity": str(item.get("severity", "medium")),
                    "impacted_objects": self._as_int(item.get("impactedObjects")),
                    "description": str(item.get("description", "")),
                }
                for item in self._as_list(result.get("compatibilityIssues"))
                if isinstance(item, dict)
            ]

            attributes: dict[str, Any] = {
                "name": name,
                "assessed_target": result.get("targetPlatform"),
                "feature_parity_issues": parity,
                "compatibility_issues": compatibility,
                "blocking_feature_count": sum(
                    1 for item in parity if item["severity"] == "blocker"
                ),
                "source_platform": result.get("sourcePlatform", "sql-server"),
                "source_version": result.get("sourceVersion"),
                "measured": True,
            }
            if unmapped:
                attributes[UNMAPPED_ATTRIBUTE] = sorted(unmapped)
            records.append(
                self._record(
                    engagement_id=engagement_id,
                    subject_id=self.workload_id(name),
                    subject_type="workload",
                    source_ref=f"{path.name}#results[{index}]",
                    collected_on=assessed_on,
                    attributes={k: v for k, v in attributes.items() if v is not None},
                    evidence_class=EvidenceClass.OBSERVED,
                    confidence=Confidence.HIGH,
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


__all__ = ["DmsAdapter"]
