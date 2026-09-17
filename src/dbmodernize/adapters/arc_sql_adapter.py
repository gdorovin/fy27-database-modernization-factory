"""Azure Arc-enabled SQL Server adapter.

Arc's value here is continuous inventory over an estate nobody has fully mapped. Its
records are high-confidence for what they cover, but Arc sees only enrolled instances, so
the adapter also emits an estate-level record describing enrollment coverage. Coverage is
what turns "we found 40 instances" into "we found 40 of an unknown total".
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

_DOCUMENT_KEYS = frozenset({"collectedOn", "instances", "enrollmentCoverage"})
_INSTANCE_KEYS = frozenset(
    {
        "name",
        "version",
        "edition",
        "patchLevel",
        "supportStatus",
        "hostAlias",
        "environment",
        "features",
        "securityFindings",
        "databases",
    }
)
_DATABASE_KEYS = frozenset({"name", "sizeInGb", "environment"})


class ArcSqlAdapter(EvidenceAdapter):
    source: ClassVar[EvidenceSource] = EvidenceSource.ARC_ENABLED_SQL
    name: ClassVar[str] = "arc-sql"
    suffixes: ClassVar[tuple[str, ...]] = (".json",)

    def supports(self, path: Path) -> bool:
        if path.suffix.lower() not in self.suffixes:
            return False
        try:
            document = read_json(path)
        except UsageError:
            return False
        return isinstance(document, dict) and "instances" in document

    def extract(self, path: Path, engagement_id: str, collected_on: date) -> list[EvidenceRecord]:
        document = read_json(path)
        if not isinstance(document, dict):
            raise UsageError(f"{path}: expected a JSON object at the document root")

        collected = self._parse_date(document.get("collectedOn"), collected_on)
        instances = [i for i in self._as_list(document.get("instances")) if isinstance(i, dict)]
        records: list[EvidenceRecord] = []
        unmapped = self.unrecognised_keys(document, _DOCUMENT_KEYS)
        for instance in instances:
            unmapped |= self.unrecognised_keys(instance, _INSTANCE_KEYS)
            for database in self._as_list(instance.get("databases")):
                unmapped |= self.unrecognised_keys(database, _DATABASE_KEYS, "databases.")

        for index, instance in enumerate(instances):
            instance_name = str(instance.get("name", "")).strip()
            features = sorted(str(f) for f in self._as_list(instance.get("features")))
            security = [str(f) for f in self._as_list(instance.get("securityFindings"))]

            for db_index, database in enumerate(self._as_list(instance.get("databases"))):
                if not isinstance(database, dict):
                    continue
                name = str(database.get("name", "")).strip()
                if not name:
                    continue
                # Identity is the database name alone, deliberately: the CSV inventory and
                # the other adapters key on the same thing, and that shared key is what lets
                # sources be merged and their disagreements detected. The cost is that two
                # instances each holding a database with the same name collapse into one
                # workload. Until identity carries the instance across every adapter, an
                # estate with duplicate database names should disambiguate them in the
                # inventory; the assessment will report the resulting conflicts.
                attributes: dict[str, Any] = {
                    "name": name,
                    "source_platform": "sql-server",
                    "source_version": instance.get("version"),
                    "edition": instance.get("edition"),
                    "patch_level": instance.get("patchLevel"),
                    "support_status": instance.get("supportStatus"),
                    "host_alias": instance.get("hostAlias") or instance_name,
                    "data_size_gb": database.get("sizeInGb"),
                    "environment": database.get("environment") or instance.get("environment"),
                    "instance_features": features,
                    "security_findings": security,
                    "arc_enrolled": True,
                    "measured": True,
                }
                if unmapped:
                    attributes[UNMAPPED_ATTRIBUTE] = sorted(unmapped)
                records.append(
                    self._record(
                        engagement_id=engagement_id,
                        subject_id=self.workload_id(name),
                        subject_type="workload",
                        source_ref=(f"{path.name}#instances[{index}].databases[{db_index}]"),
                        collected_on=collected,
                        attributes={k: v for k, v in attributes.items() if v is not None},
                        evidence_class=EvidenceClass.OBSERVED,
                        confidence=Confidence.HIGH,
                    )
                )

        coverage = document.get("enrollmentCoverage")
        records.append(
            self._record(
                engagement_id=engagement_id,
                subject_id="estate",
                subject_type="estate",
                source_ref=f"{path.name}#enrollmentCoverage",
                collected_on=collected,
                attributes={
                    "arc_enrolled_instances": len(instances),
                    "estimated_total_instances": (
                        coverage.get("estimatedTotalInstances")
                        if isinstance(coverage, dict)
                        else None
                    ),
                    "coverage_basis": (
                        coverage.get("basis") if isinstance(coverage, dict) else "not stated"
                    ),
                },
                # Coverage is inferred by comparing two counts, so it is derived, not observed.
                evidence_class=EvidenceClass.DERIVED,
                confidence=Confidence.MEDIUM if isinstance(coverage, dict) else Confidence.LOW,
                notes=(
                    "Arc reports only enrolled instances. Anything not enrolled is invisible "
                    "to this evidence and must not be assumed absent."
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


__all__ = ["ArcSqlAdapter"]
