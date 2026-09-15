"""Build a migration plan for one wave.

Every task that can change an environment is generated with ``approval_required`` and a
rollback note attached, because the model refuses to construct one without them. That is
deliberate: the safety property is enforced by the type, not by the author remembering.
"""

from __future__ import annotations

from datetime import UTC, datetime

from dbmodernize.models.base import ApprovalRole, Confidence, PlaybookRef
from dbmodernize.models.decision import TargetDecisionSet
from dbmodernize.models.engagement import Engagement
from dbmodernize.models.planning import (
    Criterion,
    CutoverPlan,
    MigrationPlan,
    MigrationWave,
    PlanPhase,
    PlanTask,
    RollbackPlan,
    TaskKind,
)
from dbmodernize.models.workload import WorkloadInventory  # noqa: F401 - re-exported for callers
from dbmodernize.policies.models import Playbook, PolicyCategory

AUTHOR = "agent:migration-planner"

#: Preview only. Nothing in this repository applies a deployment.
WHAT_IF_COMMAND = "az deployment group what-if --template-file infra/bicep/main.bicep"

_ALL_CUTOVER_ROLES = [
    ApprovalRole.BUSINESS_OWNER,
    ApprovalRole.APPLICATION_OWNER,
    ApprovalRole.DATABASE_OWNER,
    ApprovalRole.SECURITY_OWNER,
    ApprovalRole.OPERATIONS_OWNER,
]


def build_plan(
    wave: MigrationWave,
    decisions: TargetDecisionSet,
    engagement: Engagement,
    playbook: Playbook,
    playbook_ref: PlaybookRef,
) -> MigrationPlan:
    timestamp = datetime.combine(engagement.as_of, datetime.min.time(), tzinfo=UTC)
    wave_decisions = [
        decision for decision in decisions.decisions if decision.workload_id in wave.workload_ids
    ]
    conversion_needed = any(decision.conversion_required for decision in wave_decisions)
    app_change_needed = any(decision.requires_application_change for decision in wave_decisions)
    security_policies = playbook.policy_ids_for({PolicyCategory.SECURITY, PolicyCategory.IDENTITY})
    network_policies = playbook.policy_ids_for({PolicyCategory.NETWORKING})
    validation_policies = playbook.policy_ids_for({PolicyCategory.VALIDATION})

    phases = [
        _prepare_phase(wave, security_policies, network_policies),
        _build_phase(wave, security_policies, conversion_needed, app_change_needed),
        _migrate_phase(wave),
        _validate_phase(wave, validation_policies),
        _cutover_phase(wave),
        _stabilize_phase(wave),
    ]

    return MigrationPlan(
        id=f"plan-{wave.id}",
        engagement_id=engagement.engagement_id,
        workload_ids=wave.workload_ids,
        created_at=timestamp,
        updated_at=timestamp,
        author=AUTHOR,
        evidence_refs=sorted(
            {ref for decision in wave_decisions for ref in decision.evidence_refs}
        ),
        playbook=playbook_ref,
        confidence=Confidence.MEDIUM,
        risk_ids=sorted({risk for decision in wave_decisions for risk in decision.risk_ids}),
        wave_id=wave.id,
        target_decision_ids=sorted(decision.id for decision in wave_decisions),
        phases=phases,
        cutover=_cutover(wave),
        rollback=_rollback(wave),
        acceptance_criteria=_acceptance(wave),
        validation_plan_ref=f"validation-plan-{wave.sequence}.md",
    )


def _prepare_phase(
    wave: MigrationWave, security_policies: list[str], network_policies: list[str]
) -> PlanPhase:
    return PlanPhase(
        name="Prepare",
        objective="Establish readiness and close every entry criterion before anything moves.",
        tasks=[
            PlanTask(
                id=f"{wave.id}-t-landing-zone",
                title="Confirm landing zone readiness",
                kind=TaskKind.PREPARE,
                description=(
                    "Verify subscription, identity, network, private connectivity, DNS, policy, "
                    "logging, backup, and disaster-recovery ownership for the target scope."
                ),
                owner_role="architect",
                dry_run_command="dbmodernize validate-playbook playbooks/default",
                policy_ids=sorted(set(security_policies + network_policies)),
            ),
            PlanTask(
                id=f"{wave.id}-t-baseline",
                title="Capture the source performance and behaviour baseline",
                kind=TaskKind.PREPARE,
                description=(
                    "Record query latency, throughput, concurrency, and error rates over a "
                    "representative period. Without this baseline, no post-migration "
                    "comparison can be made and no regression can be proven."
                ),
                owner_role="database-owner",
            ),
            PlanTask(
                id=f"{wave.id}-t-dependency-confirm",
                title="Confirm application dependencies with their owners",
                kind=TaskKind.PREPARE,
                description=(
                    "Walk the dependency list with each application owner and record "
                    "confirmation. Unconfirmed consumers are the usual cause of a failed cutover."
                ),
                owner_role="application-owner",
                depends_on=[f"{wave.id}-t-landing-zone"],
            ),
        ],
    )


def _build_phase(
    wave: MigrationWave,
    security_policies: list[str],
    conversion_needed: bool,
    app_change_needed: bool,
) -> PlanPhase:
    tasks = [
        PlanTask(
            id=f"{wave.id}-t-provision-nonprod",
            title="Provision the non-production target environment",
            kind=TaskKind.BUILD,
            description=(
                "Deploy the target configuration to a non-production subscription using "
                "infrastructure as code, reviewing the what-if output before applying."
            ),
            owner_role="architect",
            depends_on=[f"{wave.id}-t-landing-zone"],
            dry_run_command=WHAT_IF_COMMAND,
            changes_environment=True,
            approval_required=True,
            rollback_note=(
                "Delete the non-production resource group. No production system is affected "
                "at this step."
            ),
            policy_ids=security_policies,
        )
    ]
    if conversion_needed:
        tasks.append(
            PlanTask(
                id=f"{wave.id}-t-convert-schema",
                title="Convert schema and database code",
                kind=TaskKind.BUILD,
                description=(
                    "Run conversion tooling, then hand-remediate every object the tooling could "
                    "not convert. A conversion percentage is tool output, not evidence of "
                    "equivalent behaviour."
                ),
                owner_role="database-owner",
                depends_on=[f"{wave.id}-t-provision-nonprod"],
            )
        )
    if app_change_needed:
        tasks.append(
            PlanTask(
                id=f"{wave.id}-t-application-remediation",
                title="Remediate the application for the target",
                kind=TaskKind.BUILD,
                description=(
                    "Update connection handling, retry logic, driver versions, and any code that "
                    "relied on instance-scoped behaviour that the target does not offer."
                ),
                owner_role="application-owner",
                depends_on=[f"{wave.id}-t-provision-nonprod"],
            )
        )
    return PlanPhase(
        name="Build",
        objective="Stand up the target and make the application able to use it.",
        tasks=tasks,
    )


def _migrate_phase(wave: MigrationWave) -> PlanPhase:
    return PlanPhase(
        name="Migrate",
        objective="Move data into the non-production target and rehearse the cutover.",
        tasks=[
            PlanTask(
                id=f"{wave.id}-t-seed-nonprod",
                title="Seed the non-production target",
                kind=TaskKind.MIGRATE,
                description="Perform an initial data load and start continuous replication.",
                owner_role="database-owner",
                depends_on=[f"{wave.id}-t-provision-nonprod"],
                changes_environment=True,
                approval_required=True,
                rollback_note="Stop replication and drop the non-production target databases.",
            ),
            PlanTask(
                id=f"{wave.id}-t-rehearse-cutover",
                title="Rehearse the cutover and measure the window",
                kind=TaskKind.MIGRATE,
                description=(
                    "Run the full cutover sequence against non-production and measure the actual "
                    "downtime. Until this produces a number, downtime expectations stay at "
                    "short-planned rather than near-zero."
                ),
                owner_role="delivery-lead",
                depends_on=[f"{wave.id}-t-seed-nonprod"],
                changes_environment=True,
                approval_required=True,
                rollback_note="Restore the non-production target from the pre-rehearsal snapshot.",
            ),
            PlanTask(
                id=f"{wave.id}-t-rehearse-rollback",
                title="Rehearse the rollback",
                kind=TaskKind.MIGRATE,
                description=(
                    "Execute the documented rollback against non-production and confirm the "
                    "source returns to service within the decision window."
                ),
                owner_role="operations-owner",
                depends_on=[f"{wave.id}-t-rehearse-cutover"],
                changes_environment=True,
                approval_required=True,
                rollback_note=(
                    "This task is the rollback rehearsal; failure means the plan is not ready."
                ),
            ),
        ],
    )


def _validate_phase(wave: MigrationWave, validation_policies: list[str]) -> PlanPhase:
    return PlanPhase(
        name="Validate",
        objective="Produce the evidence a go / no-go decision will rest on.",
        tasks=[
            PlanTask(
                id=f"{wave.id}-t-run-validation",
                title="Execute the validation plan",
                kind=TaskKind.VALIDATE,
                description=(
                    "Run every check in the validation plan and record the observed value "
                    "against its tolerance. A check with no recorded observation counts as "
                    "not run, not as a pass."
                ),
                owner_role="delivery-lead",
                depends_on=[f"{wave.id}-t-rehearse-rollback"],
                dry_run_command=f"dbmodernize render-report --wave {wave.id}",
                policy_ids=validation_policies,
            ),
            PlanTask(
                id=f"{wave.id}-t-review-validation",
                title="Review validation evidence and decide go / no-go",
                kind=TaskKind.VALIDATE,
                description=(
                    "Review the validation report with all five approval roles. A blocking "
                    "failure forces a no-go; an un-run blocking check forbids a go."
                ),
                owner_role="architect",
                depends_on=[f"{wave.id}-t-run-validation"],
            ),
        ],
    )


def _cutover_phase(wave: MigrationWave) -> PlanPhase:
    return PlanPhase(
        name="Cutover",
        objective="Move production traffic, with an explicit decision point before doing so.",
        tasks=[
            PlanTask(
                id=f"{wave.id}-t-production-provision",
                title="Provision the production target",
                kind=TaskKind.CUTOVER,
                description=(
                    "Deploy the reviewed infrastructure to production after a what-if review. "
                    "Requires the recorded approval of all five owner roles."
                ),
                owner_role="architect",
                depends_on=[f"{wave.id}-t-review-validation"],
                dry_run_command=WHAT_IF_COMMAND,
                changes_environment=True,
                approval_required=True,
                rollback_note=(
                    "Leave the source serving traffic and remove the unused production target. "
                    "No traffic has moved at this point."
                ),
            ),
            PlanTask(
                id=f"{wave.id}-t-execute-cutover",
                title="Execute the cutover",
                kind=TaskKind.CUTOVER,
                description=(
                    "Apply the write freeze, drain replication, switch the application, and "
                    "verify the smoke tests inside the agreed window."
                ),
                owner_role="delivery-lead",
                depends_on=[f"{wave.id}-t-production-provision"],
                changes_environment=True,
                approval_required=True,
                rollback_note=(
                    "Invoke the documented rollback: restore application configuration to the "
                    "source, confirm write availability, and reconcile any data written to the "
                    "target during the window."
                ),
            ),
        ],
    )


def _stabilize_phase(wave: MigrationWave) -> PlanPhase:
    return PlanPhase(
        name="Stabilize",
        objective="Hold the workload under observation before anything is decommissioned.",
        tasks=[
            PlanTask(
                id=f"{wave.id}-t-hypercare",
                title="Run the hypercare period",
                kind=TaskKind.STABILIZE,
                description=(
                    "Monitor performance, errors, and cost against baseline for the agreed "
                    "period, with the rollback path still available throughout."
                ),
                owner_role="operations-owner",
                depends_on=[f"{wave.id}-t-execute-cutover"],
            ),
            PlanTask(
                id=f"{wave.id}-t-decommission-decision",
                title="Decide whether to decommission the source",
                kind=TaskKind.DECOMMISSION,
                description=(
                    "Only after hypercare completes and business acceptance is recorded. This "
                    "repository never decommissions anything; the decision and the execution "
                    "are both human."
                ),
                owner_role="business-owner",
                depends_on=[f"{wave.id}-t-hypercare"],
            ),
        ],
    )


def _cutover(wave: MigrationWave) -> CutoverPlan:
    return CutoverPlan(
        freeze_start="T-2h relative to the agreed window start",
        replication_method="Continuous replication drained to zero lag before the switch.",
        go_no_go_criteria=[
            Criterion(
                id=f"{wave.id}-gng-validation",
                statement="No blocking validation check has failed and none is un-run.",
                verification_method="Validation report for the wave",
                owner_role="delivery-lead",
                automated=True,
            ),
            Criterion(
                id=f"{wave.id}-gng-replication-lag",
                statement=(
                    "Replication lag has reached zero and stayed there for the agreed period."
                ),
                verification_method="Replication monitoring output captured as evidence",
                owner_role="database-owner",
                automated=True,
            ),
            Criterion(
                id=f"{wave.id}-gng-rollback-ready",
                statement="The rollback path is rehearsed, staffed, and available for the window.",
                verification_method="Rehearsal record plus named on-call roster",
                owner_role="operations-owner",
                automated=False,
            ),
            Criterion(
                id=f"{wave.id}-gng-approvals",
                statement="All five owner roles have recorded an approval for this cutover.",
                verification_method="Approval ledger for the migration plan",
                owner_role="delivery-lead",
                automated=True,
            ),
        ],
        communication_plan=[
            "Notify affected application owners and the service desk at freeze start.",
            "Post status at each checkpoint inside the window.",
            "Announce the go / no-go decision explicitly, including a no-go.",
            "Confirm completion or rollback, with the reason, to all stakeholders.",
        ],
        required_approval_roles=_ALL_CUTOVER_ROLES,
        execution_window="An agreed low-traffic window, sized from the measured rehearsal.",
        owner_role="delivery-lead",
    )


def _rollback(wave: MigrationWave) -> RollbackPlan:
    return RollbackPlan(
        triggers=[
            Criterion(
                id=f"{wave.id}-rb-performance",
                statement=(
                    "Post-cutover performance regresses beyond the agreed tolerance against "
                    "baseline."
                ),
                verification_method="Baseline comparison from the validation report",
                owner_role="database-owner",
                automated=True,
            ),
            Criterion(
                id=f"{wave.id}-rb-integration-failure",
                statement="Any blocking application integration test fails after cutover.",
                verification_method="Integration test results captured as evidence",
                owner_role="application-owner",
                automated=True,
            ),
            Criterion(
                id=f"{wave.id}-rb-data-reconciliation",
                statement="Data reconciliation is incomplete or shows an unexplained difference.",
                verification_method="Row count and checksum comparison",
                owner_role="database-owner",
                automated=True,
            ),
            Criterion(
                id=f"{wave.id}-rb-window-exceeded",
                statement="The cutover exceeds the agreed window with no clear path to completion.",
                verification_method="Elapsed time against the window",
                owner_role="delivery-lead",
                automated=False,
            ),
        ],
        method=(
            "Return application configuration to the source, confirm write availability, then "
            "reconcile anything written to the target during the window."
        ),
        maximum_decision_window=(
            "The rollback decision is taken no later than the agreed window minus the measured "
            "rollback duration."
        ),
        data_reconciliation_note=(
            "Writes accepted by the target during the window must be identified, extracted, and "
            "replayed or formally written off with business-owner agreement. Rollback is not "
            "complete until this is settled."
        ),
        owner_role="operations-owner",
        rehearsed=False,
        evidence_preservation=(
            "Before rolling back, capture logs, metrics, failed test output, and replication "
            "state. Rolling back without evidence guarantees the same failure next attempt."
        ),
    )


def _acceptance(wave: MigrationWave) -> list[Criterion]:
    return [
        Criterion(
            id=f"{wave.id}-acc-functional",
            statement="Agreed functional and integration tests pass against the target.",
            verification_method="Test results attached to the validation report",
            owner_role="application-owner",
            automated=True,
        ),
        Criterion(
            id=f"{wave.id}-acc-performance",
            statement="Performance is within the agreed tolerance of the recorded baseline.",
            verification_method="Baseline comparison in the validation report",
            owner_role="database-owner",
            automated=True,
        ),
        Criterion(
            id=f"{wave.id}-acc-security",
            statement=(
                "Security configuration, identity, network isolation, and auditing match policy."
            ),
            verification_method="Security checks in the validation report",
            owner_role="security-owner",
            automated=True,
        ),
        Criterion(
            id=f"{wave.id}-acc-business",
            statement=(
                "The business owner accepts the outcome against the engagement success measures."
            ),
            verification_method="Approval artifact recorded in the ledger",
            owner_role="business-owner",
            automated=False,
        ),
    ]


__all__ = ["AUTHOR", "build_plan"]
