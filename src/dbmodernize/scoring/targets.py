"""Deterministic, rule-based target comparison.

There is no model here. Scores come from a published table of adjustments so that a
reviewer can reconstruct any number by hand, and so that the same evidence always yields
the same recommendation.

Two properties are load-bearing:

* A workload with an open blocking finding gets **no** recommendation at all. Producing a
  target from incomplete evidence is how an assessment becomes a sales artifact.
* A heterogeneous move is *blocked* until conversion evidence exists. The repository never
  claims Oracle-to-anything compatibility on the strength of a platform comparison.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from dbmodernize.models.base import (
    ArtifactStatus,
    AzureTarget,
    Confidence,
    DowntimeClass,
    OpenQuestion,
    PlaybookRef,
    SourcePlatform,
)
from dbmodernize.models.decision import (
    ConsideredOption,
    DowntimeApproach,
    OptionVerdict,
    TargetDecision,
    TargetDecisionSet,
)
from dbmodernize.models.engagement import Engagement
from dbmodernize.models.workload import Criticality, Workload, WorkloadInventory
from dbmodernize.policies.models import Playbook
from dbmodernize.scoring.classification import (
    blocks_platform_as_a_service,
    classify,
    requires_application_change,
    requires_conversion,
)
from dbmodernize.scoring.reference import (
    HYPERSCALE_GROWTH_THRESHOLD_PERCENT,
    HYPERSCALE_SIZE_THRESHOLD_GB,
    INSTANCE_SCOPED_FEATURES,
    PLATFORM_CANDIDATES,
)

AUTHOR = "agent:target-architect"
BASE_SCORE = 50.0

#: Targets that do not move the workload. A blocking finding stops a migration; it does not
#: stop the organisation from governing the system in the meantime, so these stay available
#: while destination targets are blocked.
NON_MOVING_TARGETS: frozenset[AzureTarget] = frozenset(
    {AzureTarget.ARC_ENABLED_SQL, AzureTarget.RETAIN, AzureTarget.RETIRE}
)


@dataclass(slots=True)
class Evaluation:
    """One target's assessment, before playbook filtering."""

    target: AzureTarget
    score: float = BASE_SCORE
    blockers: list[str] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)

    def adjust(self, delta: float, reason: str) -> None:
        self.score = max(0.0, min(100.0, self.score + delta))
        sign = "+" if delta >= 0 else ""
        self.reasons.append(f"{reason} ({sign}{delta:g})")

    def block(self, reason: str) -> None:
        self.blockers.append(reason)

    @property
    def rationale(self) -> str:
        if self.blockers:
            return "Blocked: " + "; ".join(self.blockers)
        return "; ".join(self.reasons) if self.reasons else "No differentiating factors found."


def evaluate(workload: Workload, target: AzureTarget) -> Evaluation:
    """Score one target against one workload."""
    evaluation = Evaluation(target=target)
    os_blockers = blocks_platform_as_a_service(workload)
    instance_features = sorted(set(workload.instance_features) & INSTANCE_SCOPED_FEATURES)
    size = workload.sizing.data_size_gb or 0.0
    growth = workload.sizing.annual_growth_percent or 0.0

    if requires_conversion(workload, target):
        _evaluate_heterogeneous(workload, evaluation, target)
        return evaluation

    match target:
        case AzureTarget.SQL_DATABASE:
            _evaluate_sql_database(evaluation, os_blockers, instance_features, size, growth)
        case AzureTarget.SQL_DATABASE_HYPERSCALE:
            _evaluate_hyperscale(evaluation, os_blockers, instance_features, size, growth)
        case AzureTarget.SQL_MANAGED_INSTANCE:
            _evaluate_managed_instance(evaluation, os_blockers, instance_features)
        case AzureTarget.SQL_ON_AZURE_VM:
            _evaluate_azure_vm(evaluation, os_blockers, workload)
        case AzureTarget.ARC_ENABLED_SQL:
            _evaluate_arc(evaluation, workload)
        case AzureTarget.POSTGRESQL_FLEXIBLE | AzureTarget.MYSQL_FLEXIBLE:
            _evaluate_managed_open_source(evaluation, os_blockers, workload, target)
        case AzureTarget.RETAIN:
            _evaluate_retain(evaluation, workload, os_blockers)
        case _:
            evaluation.block(f"No evaluation rule exists for {target.value}")
    return evaluation


def _evaluate_sql_database(
    evaluation: Evaluation,
    os_blockers: list[str],
    instance_features: list[str],
    size: float,
    growth: float,
) -> None:
    if os_blockers:
        evaluation.block(
            f"Operating-system dependencies rule out a managed target: {', '.join(os_blockers)}"
        )
        return
    if instance_features:
        evaluation.block(
            "Instance-scoped features are in use and are not available at database scope: "
            + ", ".join(instance_features)
        )
        return
    evaluation.adjust(15, "No instance-scoped dependencies, so database-level isolation fits")
    evaluation.adjust(10, "Managed operations remove patching and backup toil")
    if size > HYPERSCALE_SIZE_THRESHOLD_GB:
        evaluation.adjust(
            -20,
            f"Data size {size:g} GB is above the point where Hyperscale is the fairer comparison",
        )
    if growth > HYPERSCALE_GROWTH_THRESHOLD_PERCENT:
        evaluation.adjust(-10, f"Stated growth of {growth:g}% per year strains a fixed-size tier")


def _evaluate_hyperscale(
    evaluation: Evaluation,
    os_blockers: list[str],
    instance_features: list[str],
    size: float,
    growth: float,
) -> None:
    if os_blockers:
        evaluation.block(
            f"Operating-system dependencies rule out a managed target: {', '.join(os_blockers)}"
        )
        return
    if instance_features:
        evaluation.block(
            "Instance-scoped features are in use and are not available at database scope: "
            + ", ".join(instance_features)
        )
        return
    high_scale = size > HYPERSCALE_SIZE_THRESHOLD_GB
    high_growth = growth > HYPERSCALE_GROWTH_THRESHOLD_PERCENT
    if high_scale:
        evaluation.adjust(20, f"Data size {size:g} GB is in the range Hyperscale exists to serve")
    if high_growth:
        evaluation.adjust(15, f"Stated growth of {growth:g}% per year favours elastic storage")
    if not (high_scale or high_growth):
        evaluation.adjust(
            -25,
            "Neither size nor growth justifies Hyperscale; choosing it here would add "
            "capability nobody asked for",
        )
    evaluation.adjust(5, "Managed operations remove patching and backup toil")


def _evaluate_managed_instance(
    evaluation: Evaluation, os_blockers: list[str], instance_features: list[str]
) -> None:
    if os_blockers:
        evaluation.block(
            f"Operating-system dependencies rule out a managed target: {', '.join(os_blockers)}"
        )
        return
    if instance_features:
        evaluation.adjust(
            25,
            "Instance-scoped features in use are available at instance scope: "
            + ", ".join(instance_features),
        )
    else:
        evaluation.adjust(
            -5,
            "No instance-scoped dependency was found, so instance scope is more surface "
            "area than this workload needs",
        )
    evaluation.adjust(12, "Broad engine compatibility limits application change")
    evaluation.adjust(8, "Managed operations remove patching and backup toil")


def _evaluate_azure_vm(evaluation: Evaluation, os_blockers: list[str], workload: Workload) -> None:
    if os_blockers:
        evaluation.adjust(
            30, "Operating-system level control is required: " + ", ".join(os_blockers)
        )
    else:
        evaluation.adjust(
            -18,
            "No operating-system dependency was found, so this target keeps patching and "
            "backup responsibility without a reason",
        )
    evaluation.adjust(10, "Full engine control preserves third-party application support")
    if workload.criticality is Criticality.CRITICAL:
        evaluation.adjust(
            -5, "Availability design remains the customer's responsibility on infrastructure"
        )


def _evaluate_arc(evaluation: Evaluation, workload: Workload) -> None:
    incomplete = not workload.dependency_discovery_complete or bool(workload.blocking_findings)
    if incomplete:
        evaluation.adjust(
            25,
            "Evidence is incomplete, and Arc gives continuous inventory, assessment, and "
            "governance while that is fixed",
        )
    else:
        evaluation.adjust(
            -15,
            "Evidence is already sufficient to choose a destination, so a bridge adds a step "
            "without adding information",
        )
    evaluation.adjust(5, "Governance and security posture improve without moving the workload")
    evaluation.reasons.append(
        "Arc enablement is a bridge, not a completed modernization; the workload has not moved"
    )


def _evaluate_managed_open_source(
    evaluation: Evaluation,
    os_blockers: list[str],
    workload: Workload,
    target: AzureTarget,
) -> None:
    expected = {
        AzureTarget.POSTGRESQL_FLEXIBLE: {SourcePlatform.POSTGRESQL},
        AzureTarget.MYSQL_FLEXIBLE: {SourcePlatform.MYSQL, SourcePlatform.MARIADB},
    }[target]
    if workload.source_platform not in expected:
        evaluation.block(
            f"{target.value} does not serve {workload.source_platform.value} without conversion"
        )
        return
    if os_blockers:
        evaluation.block(
            f"Operating-system dependencies rule out a managed target: {', '.join(os_blockers)}"
        )
        return

    evaluation.adjust(20, "Managed flexible server is the default for this engine family")
    evaluation.adjust(
        10, "Built-in high availability, backup, and patching reduce operational load"
    )
    if workload.extensions:
        evaluation.adjust(
            -12,
            "Extensions in use must be verified per extension and per version before this "
            "target can be confirmed: " + ", ".join(sorted(workload.extensions)),
        )


def _evaluate_retain(evaluation: Evaluation, workload: Workload, os_blockers: list[str]) -> None:
    evaluation.adjust(-20, "Retaining the workload leaves every current risk in place")
    if os_blockers:
        evaluation.adjust(
            15, "Operating-system dependencies would need removing before any managed target"
        )
    if workload.blocking_findings:
        evaluation.adjust(
            10, "Open blocking findings mean any move would be made on incomplete evidence"
        )


def _evaluate_heterogeneous(
    workload: Workload, evaluation: Evaluation, target: AzureTarget
) -> None:
    """Cross-engine moves require conversion evidence against the specific target.

    Assessing a schema against one destination says nothing about a different one. Without
    that distinction, a tie-break could recommend a target nobody ever assessed.
    """
    has_conversion_evidence = any(
        finding.id.endswith("r-conversion-effort") for finding in workload.findings
    )
    if not has_conversion_evidence:
        evaluation.block(
            "No schema or code conversion assessment is present. Compatibility across engine "
            "families is never assumed; it is demonstrated per schema."
        )
        return
    if target.value not in workload.assessed_targets:
        evaluation.block(
            f"Conversion was assessed against "
            f"{', '.join(workload.assessed_targets) or 'no target'}, not against "
            f"{target.value}. A conversion result does not transfer between destinations."
        )
        return
    evaluation.adjust(
        10, "Conversion assessment exists for this target, so the scale of the change is known"
    )
    evaluation.adjust(
        -15,
        "Converted code requires application remediation and business validation before it "
        "can be trusted",
    )
    evaluation.reasons.append(
        "Automatic compatibility is not claimed; conversion percentages describe tool output only"
    )


def recommend(
    workload: Workload,
    engagement: Engagement,
    playbook: Playbook,
    playbook_ref: PlaybookRef,
) -> TargetDecision | None:
    """Produce a target decision.

    When blocking evidence is open, every destination target is blocked and only a
    non-moving posture remains available. That is the honest answer: the workload cannot
    move yet, but leaving it ungoverned in the meantime is a separate, avoidable failure.
    """
    ready = workload.is_recommendation_ready
    open_blockers = [finding.id for finding in workload.blocking_findings] + [
        question.id for question in workload.blocking_questions
    ]

    candidates = PLATFORM_CANDIDATES.get(workload.source_platform, (AzureTarget.RETAIN,))
    options: list[ConsideredOption] = []

    for target in candidates:
        if playbook.target_status(target) == "prohibited":
            options.append(
                ConsideredOption(
                    target=target,
                    verdict=OptionVerdict.REJECTED,
                    score=0.0,
                    rationale=(
                        f"Prohibited by playbook {playbook.name} v{playbook.version}. "
                        "An exception with compensating controls would be required."
                    ),
                    evidence_refs=workload.evidence_refs,
                )
            )
            continue

        if not ready and target not in NON_MOVING_TARGETS:
            options.append(
                ConsideredOption(
                    target=target,
                    verdict=OptionVerdict.BLOCKED,
                    score=0.0,
                    rationale=(
                        "Cannot be recommended while blocking evidence is open. Choosing a "
                        "destination now would commit the engagement to a decision the "
                        "evidence does not support."
                    ),
                    blockers=open_blockers or ["open blocking finding"],
                    evidence_refs=workload.evidence_refs,
                )
            )
            continue

        evaluation = evaluate(workload, target)
        options.append(
            ConsideredOption(
                target=evaluation.target,
                verdict=OptionVerdict.BLOCKED if evaluation.blockers else OptionVerdict.VIABLE,
                score=0.0 if evaluation.blockers else round(evaluation.score, 1),
                rationale=evaluation.rationale,
                blockers=evaluation.blockers,
                evidence_refs=workload.evidence_refs,
            )
        )

    viable = [o for o in options if o.verdict is OptionVerdict.VIABLE]
    if not viable or len(options) < 2:
        # A single option with nothing weighed against it is a preference, not a decision.
        return None

    winner = max(viable, key=lambda option: (option.score, option.target.value))

    final: list[ConsideredOption] = []
    for option in options:
        if option is winner:
            final.append(option.model_copy(update={"verdict": OptionVerdict.RECOMMENDED}))
        elif option.verdict is OptionVerdict.BLOCKED or option.verdict is OptionVerdict.REJECTED:
            final.append(option)
        else:
            final.append(
                option.model_copy(
                    update={
                        "verdict": OptionVerdict.REJECTED,
                        "rationale": (
                            f"Scored {option.score:g} against {winner.score:g} for "
                            f"{winner.target.value}. {option.rationale}"
                        ),
                    }
                )
            )

    timestamp = datetime.combine(engagement.as_of, datetime.min.time(), tzinfo=UTC)
    target = winner.target
    return TargetDecision(
        id=f"td-{workload.id}",
        engagement_id=engagement.engagement_id,
        workload_ids=[workload.id],
        created_at=timestamp,
        updated_at=timestamp,
        author=AUTHOR,
        evidence_refs=workload.evidence_refs,
        playbook=playbook_ref,
        confidence=_confidence(workload, ready),
        status=ArtifactStatus.RECOMMENDED,
        open_questions=_open_questions(workload),
        workload_id=workload.id,
        recommended_target=target,
        disposition=classify(workload, target),
        rationale=_rationale(workload, winner, ready),
        considered_options=sorted(final, key=lambda option: option.target.value),
        compatibility_notes=_compatibility_notes(workload, target),
        operational_notes=_operational_notes(target),
        security_notes=_security_notes(workload),
        performance_notes=_performance_notes(workload),
        sovereignty_notes=(
            [f"Data residency requirement recorded as {workload.data_residency}."]
            if workload.data_residency
            else ["No data residency requirement was recorded."]
        ),
        application_impact=_application_impact(workload, target),
        downtime_approach=_downtime(workload),
        requires_application_change=requires_application_change(workload, target),
        conversion_required=requires_conversion(workload, target),
    )


def _confidence(workload: Workload, ready: bool) -> Confidence:
    if not ready:
        return Confidence.LOW
    return Confidence.MEDIUM if workload.sizing.measured else Confidence.LOW


def _open_questions(workload: Workload) -> list[OpenQuestion]:
    """Carry each blocking finding forward as a question the decision depends on."""
    return [
        OpenQuestion(
            id=f"q-{finding.id}",
            question=(
                f"{finding.statement} This must be resolved before a destination can be "
                "recommended."
            ),
            owner_role="database-owner",
            blocking=True,
        )
        for finding in workload.blocking_findings
    ]


def _rationale(workload: Workload, winner: ConsideredOption, ready: bool) -> str:
    if not ready:
        return (
            f"No destination can be recommended for {workload.name} while blocking evidence "
            f"is open, so every migration target is blocked. {winner.target.value} is "
            f"proposed as an interim posture only: it governs the workload where it stands "
            f"and does not move it. It must not be recorded as completed modernization. "
            f"{winner.rationale}"
        )
    return (
        f"{winner.target.value} scored highest ({winner.score:g}) for {workload.name} on the "
        f"published comparison. {winner.rationale}. This is a recommendation and requires "
        f"architecture review before it becomes a decision."
    )


def _compatibility_notes(workload: Workload, target: AzureTarget) -> list[str]:
    notes: list[str] = []
    features = sorted(set(workload.instance_features) & INSTANCE_SCOPED_FEATURES)
    if features:
        notes.append(f"Instance-scoped features observed in use: {', '.join(features)}.")
    if workload.extensions:
        notes.append(
            "Extension availability must be verified per extension and per version: "
            + ", ".join(sorted(workload.extensions))
        )
    if requires_conversion(workload, target):
        notes.append(
            "Schema and code conversion is required. Conversion tooling output is not a "
            "compatibility verdict; the application must be re-tested."
        )
    if not notes:
        notes.append("No compatibility obstacle was found in the available evidence.")
    return notes


def _operational_notes(target: AzureTarget) -> list[str]:
    if target is AzureTarget.SQL_ON_AZURE_VM:
        return [
            "Patching, backup, and availability design remain the customer's responsibility.",
            "Operational runbooks must be written before the workload is considered live.",
        ]
    if target is AzureTarget.ARC_ENABLED_SQL:
        return [
            "The workload stays where it is. This delivers inventory, assessment, and "
            "governance, not modernization.",
            "A follow-on decision is still required for the destination.",
        ]
    if target is AzureTarget.RETAIN:
        return ["Existing operational burden and risk continue unchanged."]
    return [
        "Platform-managed patching, backup, and high availability reduce operational load.",
        "Monitoring and alerting still need to be configured and owned.",
    ]


def _security_notes(workload: Workload) -> list[str]:
    notes = [
        "Private network access, managed identity, and encryption in transit and at rest are "
        "landing-zone requirements and are checked separately.",
    ]
    if workload.compliance_scopes:
        notes.append(
            "In scope for "
            + ", ".join(sorted(workload.compliance_scopes))
            + "; control evidence must be collected during validation."
        )
    return notes


def _performance_notes(workload: Workload) -> list[str]:
    if workload.sizing.measured:
        return [
            "Sizing is based on measured figures; target sizing must still be validated "
            "against a baseline comparison after migration.",
        ]
    return [
        "Sizing figures are estimates. No capacity or cost commitment can rest on them until "
        "a performance baseline has been collected.",
    ]


def _application_impact(workload: Workload, target: AzureTarget) -> list[str]:
    impact: list[str] = []
    if requires_application_change(workload, target):
        impact.append("The application must change before it can use this target.")
    else:
        impact.append("No application change is implied by the target itself.")
    impact.append("Connection strings, retry logic, and driver versions must be reviewed.")
    if not workload.dependency_discovery_complete:
        impact.append(
            "Dependency discovery is incomplete, so this impact assessment is provisional."
        )
    return impact


def _downtime(workload: Workload) -> DowntimeApproach:
    """Downtime claims stay conservative until a rehearsal has actually been measured."""
    budget = workload.service_level.max_planned_downtime_minutes
    if budget is None:
        return DowntimeApproach(
            method="To be selected once a planned-downtime budget is agreed.",
            expected_class=DowntimeClass.UNKNOWN,
            basis="No planned-downtime budget has been agreed, so no method can be justified.",
            measured=False,
        )
    return DowntimeApproach(
        method="Continuous replication with a planned application cutover window.",
        expected_class=DowntimeClass.SHORT_PLANNED,
        basis=(
            f"A budget of {budget} minutes has been stated. The class stays short-planned "
            "until a rehearsal measures the actual window."
        ),
        measured=False,
    )


def recommend_all(
    inventory: WorkloadInventory,
    engagement: Engagement,
    playbook: Playbook,
    playbook_ref: PlaybookRef,
) -> TargetDecisionSet:
    decisions: list[TargetDecision] = []
    unresolved: list[str] = []
    for workload in inventory.workloads:
        decision = recommend(workload, engagement, playbook, playbook_ref)
        if decision is None or not workload.is_recommendation_ready:
            unresolved.append(workload.id)
        if decision is not None:
            decisions.append(decision)
    return TargetDecisionSet(
        engagement_id=engagement.engagement_id,
        decisions=sorted(decisions, key=lambda d: d.workload_id),
        unresolved_workload_ids=sorted(unresolved),
    )


__all__ = [
    "AUTHOR",
    "BASE_SCORE",
    "NON_MOVING_TARGETS",
    "Evaluation",
    "evaluate",
    "recommend",
    "recommend_all",
]
