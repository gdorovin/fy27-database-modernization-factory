"""Generate GitHub issue definitions from assessment and planning artifacts.

Issues are written to disk. Creating them live is a separate step behind an explicit
confirmation flag, so a dry run can never surprise a repository with fifty new issues.
"""

from __future__ import annotations

from dbmodernize.models.base import AzureTarget, PlaybookRef
from dbmodernize.models.decision import TargetDecision, TargetDecisionSet
from dbmodernize.models.engagement import Engagement
from dbmodernize.models.issue import GithubIssue, IssueSet
from dbmodernize.models.planning import MigrationWave, WavePlan
from dbmodernize.models.workload import AssessmentFinding, Workload, WorkloadInventory
from dbmodernize.utils.hashing import slugify

#: Labels that mark an issue as touching a real environment. Any of these forces the
#: rollback_considerations field to be populated.
ENVIRONMENT_LABELS = frozenset({"migrate", "cutover", "deploy", "production"})


def generate_issues(
    engagement: Engagement,
    inventory: WorkloadInventory,
    decisions: TargetDecisionSet,
    waves: WavePlan,
    playbook: PlaybookRef,
) -> IssueSet:
    issues: list[GithubIssue] = []

    for workload in sorted(inventory.workloads, key=lambda w: w.id):
        for finding in workload.blocking_findings:
            issues.append(_blocker_issue(engagement, workload, finding, playbook))

    for wave in sorted(waves.waves, key=lambda w: w.sequence):
        blocking_ids = _blocking_issue_ids(inventory, wave)
        for workload_id in wave.workload_ids:
            scheduled = inventory.get(workload_id)
            decision = decisions.get(workload_id)
            if scheduled is None or decision is None:
                continue
            issues.append(
                _implementation_issue(engagement, scheduled, decision, wave, playbook, blocking_ids)
            )
        issues.append(_validation_issue(engagement, wave, playbook, blocking_ids))

    return IssueSet(engagement_id=engagement.engagement_id, issues=issues)


def _blocker_issue(
    engagement: Engagement,
    workload: Workload,
    finding: AssessmentFinding,
    playbook: PlaybookRef,
) -> GithubIssue:
    return GithubIssue(
        id=f"issue-{workload.id}-{slugify(finding.category.value)}-{slugify(finding.id)[-12:]}",
        title=f"Resolve {finding.category.value} blocker for {workload.name}"[:120],
        engagement_id=engagement.engagement_id,
        workload_ids=[workload.id],
        problem_statement=finding.statement,
        source_evidence=finding.evidence_refs,
        approved_target=None,
        target_decision_id=None,
        playbook=playbook,
        dependencies=[],
        scope=[
            finding.remediation or "Gather the missing evidence and update the workload artifact.",
            "Re-run the assessment and confirm the finding is closed or downgraded.",
        ],
        out_of_scope=[
            "Selecting a target. No recommendation is produced while this blocker is open.",
        ],
        acceptance_criteria=[
            f"Finding {finding.id} is closed or downgraded, with evidence attached.",
            "The workload reports no blocking findings.",
        ],
        validation_commands=[
            "dbmodernize assess --help",
            "dbmodernize validate-repo",
        ],
        security_considerations=_security_considerations(workload),
        rollback_considerations=[],
        owner_role=_owner_role(finding),
        labels=sorted({"assessment", "blocker", finding.category.value}),
        milestone=None,
        blocked_by=[],
        definition_of_done=[
            "Workload artifact updated and schema-valid.",
            "Evidence reference recorded for the new information.",
            "Assessment re-run shows the workload is recommendation-ready.",
        ],
    )


def _implementation_issue(
    engagement: Engagement,
    workload: Workload,
    decision: TargetDecision,
    wave: MigrationWave,
    playbook: PlaybookRef,
    blocked_by: list[str],
) -> GithubIssue:
    target: AzureTarget = decision.recommended_target
    decision_id: str = decision.id
    conversion: bool = decision.conversion_required
    app_change: bool = decision.requires_application_change

    scope = [
        f"Prepare the {target.value} target for {workload.name} in a non-production environment.",
        "Seed data and establish continuous replication.",
        "Rehearse the cutover and measure the actual window.",
    ]
    if conversion:
        scope.append(
            "Convert schema and database code, and remediate every object the tooling "
            "could not convert."
        )
    if app_change:
        scope.append("Remediate the application for the target's behaviour.")

    return GithubIssue(
        id=f"issue-{wave.id}-{workload.id}-implement",
        title=f"Implement {target.value} migration for {workload.name}"[:120],
        engagement_id=engagement.engagement_id,
        workload_ids=[workload.id],
        problem_statement=(
            f"{workload.name} runs on {workload.source_platform.value} "
            f"{workload.source_version or '(version unknown)'} and is scheduled in {wave.name}. "
            f"The recommended target is {target.value}."
        ),
        source_evidence=workload.evidence_refs,
        approved_target=target.value,
        target_decision_id=decision_id,
        playbook=playbook,
        dependencies=[f"Wave {wave.sequence} entry criteria are met."],
        scope=scope,
        out_of_scope=[
            "Production cutover, which requires a separate recorded approval from all five "
            "owner roles.",
            "Decommissioning the source system.",
        ],
        acceptance_criteria=[
            "Non-production target is deployed from reviewed infrastructure as code.",
            "Replication reaches and holds zero lag.",
            "Cutover rehearsal produces a measured downtime figure.",
            "Rollback rehearsal completes inside the decision window.",
        ],
        validation_commands=[
            "dbmodernize validate-scenario scenarios",
            "az deployment group what-if --template-file infra/bicep/main.bicep",
        ],
        security_considerations=_security_considerations(workload),
        rollback_considerations=[
            "Non-production work is reversible by deleting the target resource group.",
            "No production traffic moves under this issue.",
        ],
        owner_role="database-owner",
        labels=sorted({"migrate", "wave-" + str(wave.sequence), target.value}),
        milestone=wave.name,
        blocked_by=blocked_by,
        definition_of_done=[
            "Rehearsal evidence attached to the wave.",
            "Validation plan executed with observations recorded for every blocking check.",
            "No new blocking finding introduced.",
        ],
    )


def _validation_issue(
    engagement: Engagement,
    wave: MigrationWave,
    playbook: PlaybookRef,
    blocked_by: list[str],
) -> GithubIssue:
    return GithubIssue(
        id=f"issue-{wave.id}-validate",
        title=f"Execute validation and decide go / no-go for {wave.name}"[:120],
        engagement_id=engagement.engagement_id,
        workload_ids=list(wave.workload_ids),
        problem_statement=(
            f"{wave.name} needs an evidence-backed go / no-go decision before any production "
            "cutover. A blocking failure forces a no-go; an un-run blocking check forbids a go."
        ),
        source_evidence=[],
        approved_target=None,
        target_decision_id=None,
        playbook=playbook,
        dependencies=[f"All implementation issues for {wave.name} are complete."],
        scope=[
            "Execute every check in the wave validation plan.",
            "Record the observed value against the tolerance for each check.",
            "Produce the validation report artifact.",
        ],
        out_of_scope=["Executing the cutover itself."],
        acceptance_criteria=[
            "Every blocking check has a recorded observation.",
            "The validation report is schema-valid and its outcome follows the evidence.",
            "All five owner roles have reviewed the report.",
        ],
        validation_commands=["dbmodernize render-report --help"],
        security_considerations=[
            "Security configuration, identity, network isolation, encryption, and auditing "
            "checks are blocking and cannot be waived without an approved policy exception.",
        ],
        rollback_considerations=[
            "A no-go triggers the documented rollback path.",
            "Evidence is preserved before any rollback, so the failure can be analysed.",
        ],
        owner_role="delivery-lead",
        labels=sorted({"validation", "cutover", "wave-" + str(wave.sequence)}),
        milestone=wave.name,
        blocked_by=blocked_by,
        definition_of_done=[
            "Validation report committed and schema-valid.",
            "Go / no-go decision recorded with the approving roles.",
            "Corrective issues created for every failure.",
        ],
    )


def _blocking_issue_ids(inventory: WorkloadInventory, wave: MigrationWave) -> list[str]:
    ids: list[str] = []
    for workload_id in wave.workload_ids:
        workload = inventory.get(workload_id)
        if workload is None:
            continue
        for finding in workload.blocking_findings:
            ids.append(
                f"issue-{workload.id}-{slugify(finding.category.value)}-{slugify(finding.id)[-12:]}"
            )
    return sorted(set(ids))


def _security_considerations(workload: Workload) -> list[str]:
    considerations = [
        "No credential, connection string, or customer identifier may appear in this issue "
        "or in any artifact it produces.",
    ]
    if workload.compliance_scopes:
        considerations.append(
            "In scope for "
            + ", ".join(sorted(workload.compliance_scopes))
            + "; control evidence is required before acceptance."
        )
    return considerations


def _owner_role(finding: AssessmentFinding) -> str:
    mapping = {
        "dependency": "application-owner",
        "security": "security-owner",
        "availability": "operations-owner",
        "operations": "operations-owner",
        "licensing": "business-owner",
        "cost": "business-owner",
    }
    return mapping.get(finding.category.value, "database-owner")


__all__ = ["ENVIRONMENT_LABELS", "generate_issues"]
