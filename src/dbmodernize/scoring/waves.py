"""Group workloads into dependency-aware, low-risk-first migration waves.

Two constraints drive the shape:

* Workloads that reference each other move together. Splitting a dependency pair across
  waves means a cutover that half-works, which is worse than either whole option.
* The first wave is a genuine pilot: small, low criticality, and preferably out of
  production. A "pilot" containing the payment database de-risks nothing.
"""

from __future__ import annotations

from datetime import UTC, datetime

from dbmodernize.models.base import Confidence, Disposition, PlaybookRef
from dbmodernize.models.decision import TargetDecisionSet
from dbmodernize.models.engagement import Engagement
from dbmodernize.models.planning import Criterion, MigrationWave, WavePlan
from dbmodernize.models.workload import (
    Criticality,
    EnvironmentKind,
    Workload,
    WorkloadInventory,
)
from dbmodernize.utils.hashing import slugify

AUTHOR = "agent:migration-planner"

_CRITICALITY_RANK = {
    Criticality.LOW: 0,
    Criticality.MEDIUM: 1,
    Criticality.HIGH: 2,
    Criticality.CRITICAL: 3,
}

_ENVIRONMENT_RANK = {
    EnvironmentKind.DEVELOPMENT: 0,
    EnvironmentKind.TEST: 0,
    EnvironmentKind.PRE_PRODUCTION: 1,
    EnvironmentKind.DISASTER_RECOVERY: 2,
    EnvironmentKind.UNKNOWN: 2,
    EnvironmentKind.PRODUCTION: 3,
}

#: Band label per risk rank. Ranks are the sum of criticality and environment rank.
_BANDS: tuple[tuple[int, str, str], ...] = (
    (
        2,
        "Low risk",
        "Move low-criticality and non-production workloads and confirm the method holds at volume.",
    ),
    (
        4,
        "Medium risk",
        "Move production workloads of moderate criticality once the method is proven.",
    ),
    (
        99,
        "Business critical",
        "Move the highest-criticality workloads last, with the fullest validation and rehearsal.",
    ),
)

PILOT_MAX_WORKLOADS = 2

#: Dispositions that do not move the workload, so cannot be scheduled into a wave.
_NON_MOVING_DISPOSITIONS = frozenset({Disposition.RETAIN, Disposition.RETIRE, Disposition.REPLACE})


def plan_waves(
    inventory: WorkloadInventory,
    decisions: TargetDecisionSet,
    engagement: Engagement,
    playbook_ref: PlaybookRef,
) -> WavePlan:
    timestamp = datetime.combine(engagement.as_of, datetime.min.time(), tzinfo=UTC)

    # A wave moves workloads. A workload that is retained, retired, or only governed in
    # place does not belong in one, and counting it as scheduled would overstate progress.
    eligible = [w for w in inventory.workloads if _is_moving(w, decisions)]
    unscheduled = sorted(w.id for w in inventory.workloads if not _is_moving(w, decisions))

    components = _dependency_components(eligible)
    components.sort(key=lambda group: (_risk_rank(group), sorted(w.id for w in group)[0]))

    waves: list[MigrationWave] = []
    sequence = 1
    remaining = list(components)

    pilot = _select_pilot(remaining)
    if pilot is not None:
        remaining.remove(pilot)
        waves.append(
            _build_wave(
                name="Wave 1 - pilot",
                sequence=sequence,
                objective=(
                    "Prove the migration method, the validation gate, and the rollback path on "
                    "the lowest-risk workloads before anything else moves."
                ),
                group=pilot,
                engagement=engagement,
                playbook_ref=playbook_ref,
                timestamp=timestamp,
                is_pilot=True,
                depends_on=[],
            )
        )
        sequence += 1

    for threshold, label, objective in _BANDS:
        band = [group for group in remaining if _risk_rank(group) <= threshold]
        if not band:
            continue
        for group in band:
            remaining.remove(group)
        members = [workload for group in band for workload in group]
        waves.append(
            _build_wave(
                name=f"Wave {sequence} - {label.lower()}",
                sequence=sequence,
                objective=objective,
                group=members,
                engagement=engagement,
                playbook_ref=playbook_ref,
                timestamp=timestamp,
                is_pilot=False,
                depends_on=[waves[-1].id] if waves else [],
            )
        )
        sequence += 1

    return WavePlan(
        engagement_id=engagement.engagement_id,
        waves=waves,
        deferred_workload_ids=unscheduled,
    )


def _is_moving(workload: Workload, decisions: TargetDecisionSet) -> bool:
    decision = decisions.get(workload.id)
    if decision is None:
        return False
    return decision.disposition not in _NON_MOVING_DISPOSITIONS


def _select_pilot(components: list[list[Workload]]) -> list[Workload] | None:
    """Pick the smallest, lowest-risk group that is small enough to learn from."""
    for group in components:
        if len(group) <= PILOT_MAX_WORKLOADS:
            return group
    return None


def _dependency_components(workloads: list[Workload]) -> list[list[Workload]]:
    """Connected components over declared dependencies, matched by workload name."""
    by_name = {workload.name.strip().lower(): workload.id for workload in workloads}
    adjacency: dict[str, set[str]] = {workload.id: set() for workload in workloads}

    for workload in workloads:
        for dependency in workload.dependencies:
            other = by_name.get(dependency.name.strip().lower())
            if other and other != workload.id:
                adjacency[workload.id].add(other)
                adjacency[other].add(workload.id)

    index = {workload.id: workload for workload in workloads}
    seen: set[str] = set()
    components: list[list[Workload]] = []

    for workload_id in sorted(adjacency):
        if workload_id in seen:
            continue
        stack = [workload_id]
        component: list[str] = []
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            component.append(current)
            stack.extend(sorted(adjacency[current] - seen))
        components.append([index[member] for member in sorted(component)])
    return components


def _risk_rank(group: list[Workload]) -> int:
    return max(
        _CRITICALITY_RANK[workload.criticality] + _ENVIRONMENT_RANK[workload.environment]
        for workload in group
    )


def _build_wave(
    *,
    name: str,
    sequence: int,
    objective: str,
    group: list[Workload],
    engagement: Engagement,
    playbook_ref: PlaybookRef,
    timestamp: datetime,
    is_pilot: bool,
    depends_on: list[str],
) -> MigrationWave:
    wave_id = f"wave-{sequence}-{slugify(name.split('-')[-1])}"
    workload_ids = sorted(workload.id for workload in group)

    return MigrationWave(
        id=wave_id,
        engagement_id=engagement.engagement_id,
        workload_ids=workload_ids,
        created_at=timestamp,
        updated_at=timestamp,
        author=AUTHOR,
        playbook=playbook_ref,
        confidence=Confidence.MEDIUM,
        name=name,
        sequence=sequence,
        objective=objective,
        is_pilot=is_pilot,
        depends_on_wave_ids=depends_on,
        prerequisites=_prerequisites(group),
        entry_criteria=_entry_criteria(wave_id),
        exit_criteria=_exit_criteria(wave_id, is_pilot),
        owner_roles=["delivery-lead", "database-owner", "application-owner"],
        rollback_required=True,
    )


def _prerequisites(group: list[Workload]) -> list[str]:
    prerequisites = [
        "Landing zone readiness check passes for the subscriptions in scope.",
        "A non-production environment exists that mirrors the target configuration.",
    ]
    if any(workload.compliance_scopes for workload in group):
        prerequisites.append(
            "Security owner has confirmed control requirements for the compliance scopes in "
            "this wave."
        )
    if any(not workload.sizing.measured for workload in group):
        prerequisites.append(
            "A performance baseline has been captured for workloads whose sizing is estimated."
        )
    return prerequisites


def _entry_criteria(wave_id: str) -> list[Criterion]:
    return [
        Criterion(
            id=f"{wave_id}-entry-decisions-approved",
            statement="Every workload in the wave has an approved target decision.",
            verification_method="dbmodernize validate-scenario, plus the approval ledger",
            owner_role="architect",
            automated=True,
        ),
        Criterion(
            id=f"{wave_id}-entry-no-open-blockers",
            statement="No workload in the wave has an open blocking finding.",
            verification_method="dbmodernize assess re-run against current evidence",
            owner_role="database-owner",
            automated=True,
        ),
        Criterion(
            id=f"{wave_id}-entry-rollback-rehearsed",
            statement="The rollback path has been rehearsed in a non-production environment.",
            verification_method="Rehearsal record attached to the wave as evidence",
            owner_role="operations-owner",
            automated=False,
        ),
    ]


def _exit_criteria(wave_id: str, is_pilot: bool) -> list[Criterion]:
    criteria = [
        Criterion(
            id=f"{wave_id}-exit-validation-pass",
            statement="All blocking validation checks pass and none is left un-run.",
            verification_method="dbmodernize render-report against the wave validation report",
            owner_role="delivery-lead",
            automated=True,
        ),
        Criterion(
            id=f"{wave_id}-exit-business-acceptance",
            statement="Business and application owners have accepted the outcome.",
            verification_method="Approval artifacts recorded in the ledger",
            owner_role="business-owner",
            automated=True,
        ),
        Criterion(
            id=f"{wave_id}-exit-monitoring-live",
            statement="Monitoring, alerting, and the operational runbook are live and owned.",
            verification_method="Operations owner sign-off with links to the alert rules",
            owner_role="operations-owner",
            automated=False,
        ),
    ]
    if is_pilot:
        criteria.append(
            Criterion(
                id=f"{wave_id}-exit-lessons-captured",
                statement=(
                    "Lessons from the pilot are recorded and the plan for later waves is "
                    "updated to reflect them."
                ),
                verification_method="Updated migration plan artifact referencing the pilot report",
                owner_role="delivery-lead",
                automated=False,
            )
        )
    return criteria


__all__ = ["AUTHOR", "PILOT_MAX_WORKLOADS", "plan_waves"]
