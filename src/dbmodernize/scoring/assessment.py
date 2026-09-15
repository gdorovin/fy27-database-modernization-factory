"""Build the workload inventory and assessment findings from normalized evidence.

Every finding is produced by a named rule so a reviewer can ask "which rule said that?"
and get an answer. Rules are pure functions of the merged evidence for one workload; none
of them reaches outside their inputs.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from dbmodernize.evidence.normalize import evidence_ids_for, merged_attributes
from dbmodernize.models.base import (
    ArtifactStatus,
    Confidence,
    EvidenceClass,
    Likelihood,
    PlaybookRef,
    Severity,
    SourcePlatform,
)
from dbmodernize.models.engagement import Engagement
from dbmodernize.models.evidence import EvidenceBundle
from dbmodernize.models.risk import Risk, RiskCategory, RiskRegister
from dbmodernize.models.workload import (
    AssessmentFinding,
    Criticality,
    Dependency,
    EnvironmentKind,
    FindingCategory,
    ServiceLevelRequirement,
    SupportStatus,
    Workload,
    WorkloadInventory,
    WorkloadSizing,
)
from dbmodernize.scoring.reference import (
    INSTANCE_SCOPED_FEATURES,
    OS_LEVEL_FEATURES,
    open_source_support,
    sql_server_support,
)

AUTHOR = "agent:estate-assessor"

Rule = Callable[["AssessmentContext"], list[AssessmentFinding]]


class AssessmentContext:
    """Everything a rule is allowed to see."""

    def __init__(
        self,
        workload: Workload,
        attributes: dict[str, Any],
        bundle: EvidenceBundle,
    ) -> None:
        self.workload = workload
        self.attributes = attributes
        self.bundle = bundle
        self.evidence_refs = workload.evidence_refs

    def finding(
        self,
        rule_id: str,
        category: FindingCategory,
        severity: Severity,
        statement: str,
        *,
        evidence_class: EvidenceClass = EvidenceClass.DERIVED,
        remediation: str | None = None,
        blocking: bool = False,
    ) -> AssessmentFinding:
        return AssessmentFinding(
            id=f"{self.workload.id}-{rule_id}",
            category=category,
            severity=severity,
            statement=statement,
            evidence_class=evidence_class,
            evidence_refs=self.evidence_refs,
            remediation=remediation,
            blocking=blocking or severity is Severity.BLOCKER,
        )


def rule_unknown_version(ctx: AssessmentContext) -> list[AssessmentFinding]:
    if ctx.workload.source_version:
        return []
    return [
        ctx.finding(
            "r-version-unknown",
            FindingCategory.SUPPORT_LIFECYCLE,
            Severity.BLOCKER,
            "The engine version is unknown, so support posture, upgrade path, and target "
            "compatibility cannot be determined.",
            remediation="Collect the version from the instance or an Arc/Azure Migrate export.",
            blocking=True,
        )
    ]


def rule_support_status(ctx: AssessmentContext) -> list[AssessmentFinding]:
    status = ctx.workload.support_status
    if status is SupportStatus.END_OF_SUPPORT:
        return [
            ctx.finding(
                "r-end-of-support",
                FindingCategory.SUPPORT_LIFECYCLE,
                Severity.HIGH,
                f"Engine version {ctx.workload.source_version} is past end of support, so it "
                "receives no security fixes and carries audit and cyber exposure.",
                remediation="Modernize, upgrade in place, or obtain extended support cover.",
            )
        ]
    if status is SupportStatus.EXTENDED_SUPPORT:
        return [
            ctx.finding(
                "r-extended-support",
                FindingCategory.SUPPORT_LIFECYCLE,
                Severity.MEDIUM,
                f"Engine version {ctx.workload.source_version} is in extended support; the "
                "window is finite and should anchor the modernization date.",
            )
        ]
    return []


def rule_dependency_discovery(ctx: AssessmentContext) -> list[AssessmentFinding]:
    if ctx.workload.dependency_discovery_complete:
        return []
    return [
        ctx.finding(
            "r-dependencies-unknown",
            FindingCategory.DEPENDENCY,
            Severity.BLOCKER,
            "Dependency discovery is incomplete, so the consumers of this database and the "
            "blast radius of a cutover are unknown.",
            evidence_class=EvidenceClass.OBSERVED
            if ctx.evidence_refs
            else EvidenceClass.ASSUMPTION,
            remediation=(
                "Run dependency mapping and confirm every consumer with its application owner."
            ),
            blocking=True,
        )
    ]


def rule_unresolved_conflicts(ctx: AssessmentContext) -> list[AssessmentFinding]:
    conflicts = [c for c in ctx.bundle.unresolved_conflicts if c.subject_id == ctx.workload.id]
    if not conflicts:
        return []
    attributes = ", ".join(sorted(c.attribute for c in conflicts))
    return [
        ctx.finding(
            "r-evidence-conflict",
            FindingCategory.DATA_QUALITY,
            Severity.BLOCKER,
            f"Evidence sources disagree about: {attributes}. The repository will not choose "
            "between them.",
            evidence_class=EvidenceClass.OBSERVED,
            remediation="Have the database owner reconcile the sources and record the decision.",
            blocking=True,
        )
    ]


def rule_prompt_injection(ctx: AssessmentContext) -> list[AssessmentFinding]:
    flagged = [
        record for record in ctx.bundle.by_subject(ctx.workload.id) if record.injection_findings
    ]
    if not flagged:
        return []
    patterns = sorted({f.pattern for record in flagged for f in record.injection_findings})
    return [
        ctx.finding(
            "r-prompt-injection",
            FindingCategory.SECURITY,
            Severity.BLOCKER,
            f"Imported evidence for this workload contains directive-like content "
            f"({', '.join(patterns)}). It was treated as data and not acted on, but the "
            "source must be reviewed before the evidence is trusted.",
            evidence_class=EvidenceClass.OBSERVED,
            remediation="Review the source export and confirm who produced the text.",
            blocking=True,
        )
    ]


def rule_estimated_sizing(ctx: AssessmentContext) -> list[AssessmentFinding]:
    if ctx.workload.sizing.measured:
        return []
    return [
        ctx.finding(
            "r-sizing-estimated",
            FindingCategory.PERFORMANCE,
            Severity.MEDIUM,
            "Sizing figures are estimates rather than measurements, so they cannot support a "
            "capacity or cost commitment.",
            evidence_class=EvidenceClass.ASSUMPTION,
            remediation="Collect a performance baseline over a representative period.",
        )
    ]


def rule_service_level_assumed(ctx: AssessmentContext) -> list[AssessmentFinding]:
    level = ctx.workload.service_level
    if not level.is_assumption:
        return []
    if level.rpo_minutes is None and level.rto_minutes is None:
        severity = (
            Severity.HIGH
            if ctx.workload.criticality in {Criticality.HIGH, Criticality.CRITICAL}
            else Severity.MEDIUM
        )
        return [
            ctx.finding(
                "r-no-stated-rpo-rto",
                FindingCategory.AVAILABILITY,
                severity,
                "No RPO or RTO has been stated, so no availability design can be justified and "
                "no rollback window can be sized.",
                evidence_class=EvidenceClass.ASSUMPTION,
                remediation="Agree RPO and RTO with the business owner and record who stated them.",
            )
        ]
    return [
        ctx.finding(
            "r-service-level-assumed",
            FindingCategory.AVAILABILITY,
            Severity.MEDIUM,
            "Service-level figures are assumed rather than stated by the business owner.",
            evidence_class=EvidenceClass.ASSUMPTION,
            remediation="Confirm the figures with the business owner.",
        )
    ]


def rule_instance_features(ctx: AssessmentContext) -> list[AssessmentFinding]:
    used = sorted(set(ctx.workload.instance_features) & INSTANCE_SCOPED_FEATURES)
    if not used:
        return []
    return [
        ctx.finding(
            "r-instance-scoped-features",
            FindingCategory.COMPATIBILITY,
            Severity.HIGH,
            f"Instance-scoped features are in use ({', '.join(used)}). A database-scoped "
            "target would require application change.",
            evidence_class=EvidenceClass.OBSERVED,
            remediation=(
                "Confirm each feature is genuinely required, then weigh it in target selection."
            ),
        )
    ]


def rule_os_level_features(ctx: AssessmentContext) -> list[AssessmentFinding]:
    used = sorted(set(ctx.workload.instance_features) & OS_LEVEL_FEATURES)
    if not used:
        return []
    return [
        ctx.finding(
            "r-os-level-dependency",
            FindingCategory.COMPATIBILITY,
            Severity.HIGH,
            f"Operating-system level dependencies are in use ({', '.join(used)}), which rules "
            "out platform-as-a-service targets unless they are removed.",
            evidence_class=EvidenceClass.OBSERVED,
            remediation=(
                "Decide whether to remove the dependency or accept an infrastructure target."
            ),
        )
    ]


def rule_extensions(ctx: AssessmentContext) -> list[AssessmentFinding]:
    if not ctx.workload.extensions:
        return []
    return [
        ctx.finding(
            "r-extensions-unverified",
            FindingCategory.COMPATIBILITY,
            Severity.HIGH,
            f"Extensions or plugins are in use ({', '.join(sorted(ctx.workload.extensions))}). "
            "Availability on the managed service must be verified per extension and per "
            "version; it cannot be assumed.",
            evidence_class=EvidenceClass.OBSERVED,
            remediation="Check each extension against the managed service's supported list.",
        )
    ]


def rule_tool_blocking_issues(ctx: AssessmentContext) -> list[AssessmentFinding]:
    findings: list[AssessmentFinding] = []
    for issue in ctx.attributes.get("blocking_issues", []) or []:
        if not isinstance(issue, dict):
            continue
        code = str(issue.get("code", "unknown"))
        findings.append(
            ctx.finding(
                f"r-tool-blocking-{code.lower()}",
                FindingCategory.COMPATIBILITY,
                Severity.BLOCKER,
                f"Assessment tooling reported a blocking issue ({code}): "
                f"{issue.get('description', 'no description supplied')}",
                evidence_class=EvidenceClass.OBSERVED,
                blocking=True,
            )
        )
    for item in ctx.attributes.get("feature_parity_issues", []) or []:
        if not isinstance(item, dict) or item.get("severity") != "blocker":
            continue
        feature = str(item.get("feature", "unknown"))
        assessed = ctx.attributes.get("assessed_target", "the assessed target")
        findings.append(
            ctx.finding(
                f"r-parity-{feature.lower()}",
                FindingCategory.COMPATIBILITY,
                Severity.BLOCKER,
                f"Feature parity gap against {assessed}: "
                f"{feature}. {item.get('description', '')}".strip(),
                evidence_class=EvidenceClass.OBSERVED,
                blocking=True,
            )
        )
    return findings


def rule_conversion_effort(ctx: AssessmentContext) -> list[AssessmentFinding]:
    errors = int(ctx.attributes.get("conversion_errors", 0) or 0)
    manual = int(ctx.attributes.get("conversion_manual", 0) or 0)
    if errors == 0 and manual == 0:
        return []
    percent = ctx.attributes.get("conversion_automatic_percent")
    suffix = f" Automatic conversion covered {percent}% of objects." if percent else ""
    return [
        ctx.finding(
            "r-conversion-effort",
            FindingCategory.COMPATIBILITY,
            Severity.HIGH,
            f"Schema and code conversion is required: {manual} object(s) need manual work and "
            f"{errors} failed to convert.{suffix} A conversion percentage is not a "
            "compatibility verdict; converted code still has to be tested against the "
            "application.",
            evidence_class=EvidenceClass.OBSERVED,
            remediation="Scope the manual conversion work and plan application regression testing.",
        )
    ]


def rule_compliance_scope(ctx: AssessmentContext) -> list[AssessmentFinding]:
    if not ctx.workload.compliance_scopes:
        return []
    return [
        ctx.finding(
            "r-compliance-scope",
            FindingCategory.SECURITY,
            Severity.MEDIUM,
            f"The workload is in scope for {', '.join(sorted(ctx.workload.compliance_scopes))}, "
            "so landing-zone controls and evidence collection must be agreed before migration.",
            evidence_class=EvidenceClass.USER_PROVIDED,
            remediation="Confirm control requirements with the security owner.",
        )
    ]


def rule_production_criticality(ctx: AssessmentContext) -> list[AssessmentFinding]:
    if (
        ctx.workload.environment is EnvironmentKind.PRODUCTION
        and ctx.workload.criticality is Criticality.CRITICAL
        and ctx.workload.service_level.max_planned_downtime_minutes is None
    ):
        return [
            ctx.finding(
                "r-no-downtime-budget",
                FindingCategory.OPERATIONS,
                Severity.HIGH,
                "A business-critical production workload has no agreed planned-downtime budget, "
                "so no cutover method can be selected on evidence.",
                evidence_class=EvidenceClass.ASSUMPTION,
                remediation="Agree a maximum planned downtime with the business owner.",
            )
        ]
    return []


RULES: tuple[Rule, ...] = (
    rule_unknown_version,
    rule_support_status,
    rule_dependency_discovery,
    rule_unresolved_conflicts,
    rule_prompt_injection,
    rule_estimated_sizing,
    rule_service_level_assumed,
    rule_instance_features,
    rule_os_level_features,
    rule_extensions,
    rule_tool_blocking_issues,
    rule_conversion_effort,
    rule_compliance_scope,
    rule_production_criticality,
)


def assess(
    engagement: Engagement,
    bundle: EvidenceBundle,
    playbook: PlaybookRef,
) -> tuple[WorkloadInventory, RiskRegister]:
    """Build workloads from evidence, run every rule, and derive a risk register."""
    timestamp = datetime.combine(engagement.as_of, datetime.min.time(), tzinfo=UTC)
    subject_ids = sorted({r.subject_id for r in bundle.records if r.subject_type == "workload"})

    workloads: list[Workload] = []
    for subject_id in subject_ids:
        attributes = merged_attributes(bundle, subject_id)
        workload = _build_workload(subject_id, attributes, engagement, playbook, timestamp, bundle)
        context = AssessmentContext(workload, attributes, bundle)
        findings: list[AssessmentFinding] = []
        for rule in RULES:
            findings.extend(rule(context))
        workload.findings = sorted(findings, key=lambda f: f.id)
        workload.confidence = _confidence_for(workload)
        workload.status = _status_for(workload)
        workloads.append(workload)

    inventory = WorkloadInventory(
        engagement_id=engagement.engagement_id,
        workloads=workloads,
        inventory_completeness=_inventory_confidence(bundle),
        completeness_basis=_completeness_basis(bundle),
    )
    return inventory, _derive_risks(inventory, engagement, playbook, timestamp)


def _build_workload(
    subject_id: str,
    attributes: dict[str, Any],
    engagement: Engagement,
    playbook: PlaybookRef,
    timestamp: datetime,
    bundle: EvidenceBundle,
) -> Workload:
    platform = _enum(SourcePlatform, attributes.get("source_platform"), SourcePlatform.OTHER)
    version = _optional_str(attributes.get("source_version"))

    declared = attributes.get("support_status")
    support = (
        _enum(SupportStatus, declared, SupportStatus.UNKNOWN)
        if declared
        else (
            sql_server_support(version)
            if platform is SourcePlatform.SQL_SERVER
            else open_source_support(platform, version)
        )
    )
    if version is None:
        support = SupportStatus.UNKNOWN

    dependency_names = attributes.get("dependency_names") or []
    dependencies = [
        Dependency(
            id=f"{subject_id}-dep-{index}",
            kind="application",
            name=str(name),
            direction="unknown",
            confirmed=False,
            evidence_refs=evidence_ids_for(bundle, subject_id),
        )
        for index, name in enumerate(dependency_names)
    ]

    return Workload(
        id=subject_id,
        engagement_id=engagement.engagement_id,
        workload_ids=[subject_id],
        created_at=timestamp,
        updated_at=timestamp,
        author=AUTHOR,
        evidence_refs=evidence_ids_for(bundle, subject_id),
        playbook=playbook,
        name=str(attributes.get("name", subject_id)),
        source_platform=platform,
        source_version=version,
        edition=_optional_str(attributes.get("edition")),
        support_status=support,
        environment=_enum(EnvironmentKind, attributes.get("environment"), EnvironmentKind.UNKNOWN),
        criticality=_enum(Criticality, attributes.get("criticality"), Criticality.MEDIUM),
        host_alias=_optional_str(attributes.get("host_alias")),
        sizing=WorkloadSizing(
            data_size_gb=_number(attributes.get("data_size_gb")),
            largest_table_gb=_number(attributes.get("largest_table_gb")),
            cpu_cores=_integer(attributes.get("cpu_cores")),
            memory_gb=_number(attributes.get("memory_gb")),
            peak_iops=_integer(attributes.get("peak_iops")),
            peak_concurrent_sessions=_integer(attributes.get("peak_concurrent_sessions")),
            annual_growth_percent=_number(attributes.get("annual_growth_percent")),
            measured=bool(attributes.get("measured", False)),
        ),
        service_level=ServiceLevelRequirement(
            availability_target=_optional_str(attributes.get("availability_target")),
            rpo_minutes=_integer(attributes.get("rpo_minutes")),
            rto_minutes=_integer(attributes.get("rto_minutes")),
            max_planned_downtime_minutes=_integer(attributes.get("max_planned_downtime_minutes")),
            stated_by=_optional_str(attributes.get("service_level_stated_by")),
            is_assumption=not attributes.get("service_level_stated_by"),
        ),
        instance_features=sorted(str(f) for f in attributes.get("instance_features", [])),
        extensions=sorted(str(e) for e in attributes.get("extensions", [])),
        dependencies=dependencies,
        compliance_scopes=sorted(str(c) for c in attributes.get("compliance_scopes", [])),
        data_residency=_optional_str(attributes.get("data_residency")),
        assessed_targets=_assessed_targets(attributes),
        dependency_discovery_complete=bool(attributes.get("dependency_discovery_complete", False)),
    )


def _assessed_targets(attributes: dict[str, Any]) -> list[str]:
    """Targets a tool actually assessed. Absence is meaningful, so nothing is inferred."""
    targets: set[str] = set()
    single = attributes.get("assessed_target")
    if isinstance(single, str) and single.strip():
        targets.add(single.strip())
    for value in attributes.get("assessed_targets", []) or []:
        if isinstance(value, str) and value.strip():
            targets.add(value.strip())
    return sorted(targets)


def _derive_risks(
    inventory: WorkloadInventory,
    engagement: Engagement,
    playbook: PlaybookRef,
    timestamp: datetime,
) -> RiskRegister:
    """Every blocking finding becomes a tracked risk with an owner."""
    risks: list[Risk] = []
    for workload in inventory.workloads:
        for finding in workload.blocking_findings:
            risks.append(
                Risk(
                    id=f"risk-{finding.id}",
                    engagement_id=engagement.engagement_id,
                    workload_ids=[workload.id],
                    created_at=timestamp,
                    updated_at=timestamp,
                    author=AUTHOR,
                    evidence_refs=finding.evidence_refs,
                    playbook=playbook,
                    title=f"{workload.name}: {finding.category.value} blocker",
                    description=finding.statement,
                    category=_risk_category(finding.category),
                    likelihood=Likelihood.HIGH,
                    impact=Likelihood.HIGH,
                    owner_role=_owner_for(finding.category),
                    mitigation=finding.remediation
                    or "Close the finding with evidence before the workload enters a wave.",
                    contingency=(
                        "Defer the workload to a later wave and keep it out of the current "
                        "cutover scope."
                    ),
                    trigger=f"Finding {finding.id} is still open at the wave entry gate.",
                    confidence=Confidence.MEDIUM,
                )
            )
    return RiskRegister(engagement_id=engagement.engagement_id, risks=risks)


_RISK_CATEGORY = {
    FindingCategory.COMPATIBILITY: RiskCategory.TECHNICAL,
    FindingCategory.PERFORMANCE: RiskCategory.TECHNICAL,
    FindingCategory.AVAILABILITY: RiskCategory.OPERATIONAL,
    FindingCategory.SECURITY: RiskCategory.SECURITY,
    FindingCategory.OPERATIONS: RiskCategory.OPERATIONAL,
    FindingCategory.LICENSING: RiskCategory.COMMERCIAL,
    FindingCategory.DEPENDENCY: RiskCategory.APPLICATION,
    FindingCategory.DATA_QUALITY: RiskCategory.DATA,
    FindingCategory.SUPPORT_LIFECYCLE: RiskCategory.COMPLIANCE,
    FindingCategory.COST: RiskCategory.COMMERCIAL,
}

_OWNER = {
    FindingCategory.DEPENDENCY: "application-owner",
    FindingCategory.SECURITY: "security-owner",
    FindingCategory.AVAILABILITY: "operations-owner",
    FindingCategory.OPERATIONS: "operations-owner",
    FindingCategory.LICENSING: "business-owner",
    FindingCategory.COST: "business-owner",
}


def _risk_category(category: FindingCategory) -> RiskCategory:
    return _RISK_CATEGORY.get(category, RiskCategory.TECHNICAL)


def _owner_for(category: FindingCategory) -> str:
    return _OWNER.get(category, "database-owner")


def _confidence_for(workload: Workload) -> Confidence:
    if workload.blocking_findings:
        return Confidence.LOW
    if workload.sizing.measured and workload.source_version:
        return Confidence.HIGH
    return Confidence.MEDIUM


def _status_for(workload: Workload) -> ArtifactStatus:
    return ArtifactStatus.DRAFT if workload.blocking_findings else ArtifactStatus.EVIDENCE_COMPLETE


def _inventory_confidence(bundle: EvidenceBundle) -> Confidence:
    estate = [r for r in bundle.records if r.subject_type == "estate"]
    for record in estate:
        total = record.attributes.get("estimated_total_instances")
        found = record.attributes.get("arc_enrolled_instances")
        if isinstance(total, int) and isinstance(found, int) and total > 0:
            ratio = found / total
            if ratio >= 0.95:
                return Confidence.HIGH
            if ratio >= 0.7:
                return Confidence.MEDIUM
            return Confidence.LOW
    return Confidence.LOW


def _completeness_basis(bundle: EvidenceBundle) -> str:
    sources = sorted({record.source.value for record in bundle.records})
    estate = [r for r in bundle.records if r.subject_type == "estate"]
    if estate:
        record = estate[0]
        return (
            f"Compared enrolled instances ({record.attributes.get('arc_enrolled_instances')}) "
            f"with the stated estate total "
            f"({record.attributes.get('estimated_total_instances', 'unknown')}). "
            f"Sources: {', '.join(sources)}."
        )
    return (
        f"No estate-level coverage evidence was supplied, so completeness is unproven. "
        f"Sources: {', '.join(sources)}."
    )


def _enum(enum_type: Any, value: Any, default: Any) -> Any:
    if value is None:
        return default
    try:
        return enum_type(str(value).strip().lower())
    except ValueError:
        return default


def _optional_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _integer(value: Any) -> int | None:
    number = _number(value)
    return int(number) if number is not None else None


__all__ = ["AUTHOR", "RULES", "AssessmentContext", "assess"]
