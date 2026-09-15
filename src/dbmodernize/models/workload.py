"""Workload inventory and assessment findings."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from dbmodernize.models.base import (
    ArtifactBase,
    Classification,
    Confidence,
    EvidenceClass,
    Identifier,
    NonEmptyStr,
    Severity,
    SourcePlatform,
    StrictModel,
)


class SupportStatus(StrEnum):
    SUPPORTED = "supported"
    EXTENDED_SUPPORT = "extended-support"
    END_OF_SUPPORT = "end-of-support"
    UNKNOWN = "unknown"


class Criticality(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class EnvironmentKind(StrEnum):
    PRODUCTION = "production"
    PRE_PRODUCTION = "pre-production"
    TEST = "test"
    DEVELOPMENT = "development"
    DISASTER_RECOVERY = "disaster-recovery"
    UNKNOWN = "unknown"


class FindingCategory(StrEnum):
    COMPATIBILITY = "compatibility"
    PERFORMANCE = "performance"
    AVAILABILITY = "availability"
    SECURITY = "security"
    OPERATIONS = "operations"
    LICENSING = "licensing"
    DEPENDENCY = "dependency"
    DATA_QUALITY = "data-quality"
    SUPPORT_LIFECYCLE = "support-lifecycle"
    COST = "cost"


class AssessmentFinding(StrictModel):
    """A single assessed fact about a workload, with its evidence and severity."""

    id: Identifier
    category: FindingCategory
    severity: Severity
    statement: NonEmptyStr
    evidence_class: EvidenceClass
    evidence_refs: list[Identifier] = Field(default_factory=list)
    remediation: str | None = None
    blocking: bool = Field(
        default=False,
        description="A blocking finding prevents target recommendation until it is closed.",
    )

    @model_validator(mode="after")
    def _observed_findings_cite_evidence(self) -> AssessmentFinding:
        if self.evidence_class is EvidenceClass.OBSERVED and not self.evidence_refs:
            raise ValueError(
                f"Finding {self.id} claims to be observed but cites no evidence. "
                "Downgrade it to an assumption or attach the evidence record."
            )
        if self.severity is Severity.BLOCKER and not self.blocking:
            raise ValueError(f"Finding {self.id} has blocker severity but blocking is false")
        return self


class Dependency(StrictModel):
    id: Identifier
    kind: str = Field(
        description="application | linked-server | etl | report | integration | job | unknown"
    )
    name: NonEmptyStr
    direction: str = Field(default="unknown", description="inbound | outbound | bidirectional")
    confirmed: bool = False
    evidence_refs: list[Identifier] = Field(default_factory=list)


class ServiceLevelRequirement(StrictModel):
    availability_target: str | None = Field(
        default=None, description="As stated by the customer, e.g. '99.9% monthly'."
    )
    rpo_minutes: int | None = Field(default=None, ge=0)
    rto_minutes: int | None = Field(default=None, ge=0)
    max_planned_downtime_minutes: int | None = Field(default=None, ge=0)
    stated_by: str | None = None
    is_assumption: bool = True


class WorkloadSizing(StrictModel):
    data_size_gb: float | None = Field(default=None, ge=0)
    largest_table_gb: float | None = Field(default=None, ge=0)
    cpu_cores: int | None = Field(default=None, ge=0)
    memory_gb: float | None = Field(default=None, ge=0)
    peak_iops: int | None = Field(default=None, ge=0)
    peak_concurrent_sessions: int | None = Field(default=None, ge=0)
    annual_growth_percent: float | None = Field(default=None, ge=0)
    measured: bool = False


class Workload(ArtifactBase):
    """One database workload. The unit of assessment, decision, and wave membership."""

    artifact_type: str = "workload"
    name: NonEmptyStr
    source_platform: SourcePlatform
    source_version: str | None = Field(
        default=None, description="Null means unknown. Never guess a version."
    )
    edition: str | None = None
    support_status: SupportStatus = SupportStatus.UNKNOWN
    environment: EnvironmentKind = EnvironmentKind.UNKNOWN
    criticality: Criticality = Criticality.MEDIUM
    classification: Classification = Classification.INTERNAL
    host_alias: str | None = Field(
        default=None, description="Pseudonymous host label, never a real FQDN."
    )
    sizing: WorkloadSizing = Field(default_factory=WorkloadSizing)
    service_level: ServiceLevelRequirement = Field(default_factory=ServiceLevelRequirement)
    instance_features: list[str] = Field(
        default_factory=list,
        description=(
            "Engine features observed in use, e.g. sql-agent, service-broker, clr, "
            "linked-servers, filestream, replication, cross-database-queries."
        ),
    )
    extensions: list[str] = Field(
        default_factory=list, description="PostgreSQL/MySQL extensions or plugins in use."
    )
    dependencies: list[Dependency] = Field(default_factory=list)
    compliance_scopes: list[str] = Field(default_factory=list)
    data_residency: str | None = None
    findings: list[AssessmentFinding] = Field(default_factory=list)
    assessed_targets: list[str] = Field(
        default_factory=list,
        description=(
            "Targets for which a conversion or compatibility assessment exists. A "
            "heterogeneous target absent from this list cannot be recommended, because "
            "cross-engine compatibility is demonstrated per target, never inferred."
        ),
    )
    dependency_discovery_complete: bool = Field(
        default=False,
        description="False means dependency evidence is incomplete, which is itself a finding.",
    )

    @model_validator(mode="after")
    def _unknown_version_is_declared(self) -> Workload:
        if self.source_version is None and self.support_status is not SupportStatus.UNKNOWN:
            raise ValueError(
                f"Workload {self.id}: support_status is {self.support_status} but "
                "source_version is unknown. Support status cannot be derived without a version."
            )
        return self

    @property
    def blocking_findings(self) -> list[AssessmentFinding]:
        return [f for f in self.findings if f.blocking]

    @property
    def is_recommendation_ready(self) -> bool:
        """A target may be proposed only when nothing blocking is outstanding."""
        return not self.blocking_findings and not self.blocking_questions

    @property
    def highest_severity(self) -> Severity:
        order = [Severity.INFO, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.BLOCKER]
        worst = Severity.INFO
        for finding in self.findings:
            if order.index(finding.severity) > order.index(worst):
                worst = finding.severity
        return worst


class WorkloadInventory(StrictModel):
    """The collection produced by discovery and enriched by assessment."""

    engagement_id: Identifier
    workloads: list[Workload] = Field(default_factory=list)
    inventory_completeness: Confidence = Confidence.LOW
    completeness_basis: NonEmptyStr = Field(
        description="How completeness was judged, e.g. 'Arc-reported instance count vs CMDB'."
    )

    @model_validator(mode="after")
    def _unique_ids(self) -> WorkloadInventory:
        seen: set[str] = set()
        for workload in self.workloads:
            if workload.id in seen:
                raise ValueError(f"Duplicate workload id: {workload.id}")
            seen.add(workload.id)
        return self

    def get(self, workload_id: str) -> Workload | None:
        return next((w for w in self.workloads if w.id == workload_id), None)
