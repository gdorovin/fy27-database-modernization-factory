"""Normalized evidence records and the evidence bundle."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Any

from pydantic import Field, field_validator, model_validator

from dbmodernize.models.base import (
    Classification,
    Confidence,
    EvidenceClass,
    Identifier,
    NonEmptyStr,
    StrictModel,
)


class EvidenceSource(StrEnum):
    AZURE_MIGRATE = "azure-migrate"
    ARC_ENABLED_SQL = "arc-enabled-sql"
    DATA_MIGRATION_SERVICE = "data-migration-service"
    SSMA = "ssma"
    CSV_INVENTORY = "csv-inventory"
    STAKEHOLDER_INTERVIEW = "stakeholder-interview"
    MONITORING = "monitoring"
    MANUAL_INSPECTION = "manual-inspection"
    OTHER = "other"


class InjectionFinding(StrictModel):
    """Directive-like content detected inside imported text.

    Recorded, never obeyed. Presence of any finding forces the record's evidence class to
    stay ``observed`` data and flags it for human review.
    """

    pattern: NonEmptyStr
    excerpt: NonEmptyStr = Field(max_length=280)
    field_name: NonEmptyStr


class EvidenceRecord(StrictModel):
    """One normalized fact with its provenance intact."""

    id: Identifier
    engagement_id: Identifier
    subject_type: str = Field(description="workload | application | host | estate | policy")
    subject_id: str = Field(description="Identifier of the subject, or 'estate' for estate-wide.")
    source: EvidenceSource
    source_ref: NonEmptyStr = Field(
        description=(
            "Where the fact came from: a file name, an export ID, or an interview "
            "reference. Never a credentialed URL."
        )
    )
    collected_on: date
    evidence_class: EvidenceClass
    classification: Classification = Classification.INTERNAL
    confidence: Confidence = Confidence.MEDIUM
    attributes: dict[str, Any] = Field(default_factory=dict)
    notes: str | None = None
    injection_findings: list[InjectionFinding] = Field(default_factory=list)
    superseded_by: Identifier | None = None

    @field_validator("attributes")
    @classmethod
    def _reject_nested_callables(cls, value: dict[str, Any]) -> dict[str, Any]:
        for key, item in value.items():
            if callable(item):
                raise ValueError(f"attributes[{key!r}] is not serialisable")
        return value

    @model_validator(mode="after")
    def _recommendations_are_not_evidence(self) -> EvidenceRecord:
        if self.evidence_class in {EvidenceClass.RECOMMENDATION, EvidenceClass.APPROVED_DECISION}:
            raise ValueError(
                "An evidence record cannot be a recommendation or an approved decision. "
                "Those belong in a target-decision or approval artifact."
            )
        return self

    @property
    def is_committable(self) -> bool:
        return self.classification in {Classification.PUBLIC, Classification.INTERNAL}


class EvidenceConflict(StrictModel):
    """Two sources disagree. The bundle records it and refuses to pick a winner."""

    id: Identifier
    subject_id: NonEmptyStr
    attribute: NonEmptyStr
    values: list[str] = Field(min_length=2)
    evidence_refs: list[Identifier] = Field(min_length=2)
    resolution_owner_role: NonEmptyStr
    resolved: bool = False
    resolution: str | None = None

    @model_validator(mode="after")
    def _resolution_requires_text(self) -> EvidenceConflict:
        if self.resolved and not self.resolution:
            raise ValueError("A resolved conflict must record how it was resolved and by whom")
        return self


class EvidenceManifestEntry(StrictModel):
    """Reference to an external artifact that is deliberately not committed."""

    id: Identifier
    description: NonEmptyStr
    sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    location_description: NonEmptyStr = Field(
        description="Human description of approved storage. Never a URL containing a token."
    )
    classification: Classification
    retention_note: str | None = None


class EvidenceBundle(StrictModel):
    """The output of ``dbmodernize normalize-evidence``."""

    engagement_id: Identifier
    generated_at: datetime
    generator: NonEmptyStr
    records: list[EvidenceRecord] = Field(default_factory=list)
    conflicts: list[EvidenceConflict] = Field(default_factory=list)
    manifest: list[EvidenceManifestEntry] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_ids(self) -> EvidenceBundle:
        seen: set[str] = set()
        for record in self.records:
            if record.id in seen:
                raise ValueError(f"Duplicate evidence id: {record.id}")
            seen.add(record.id)
        return self

    def by_subject(self, subject_id: str) -> list[EvidenceRecord]:
        return [r for r in self.records if r.subject_id == subject_id and not r.superseded_by]

    @property
    def unresolved_conflicts(self) -> list[EvidenceConflict]:
        return [c for c in self.conflicts if not c.resolved]

    @property
    def injection_flagged(self) -> list[EvidenceRecord]:
        return [r for r in self.records if r.injection_findings]
