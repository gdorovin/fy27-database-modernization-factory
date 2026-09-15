"""Migration waves and the migration plan they produce."""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import Field, model_validator

from dbmodernize.models.base import (
    ApprovalRole,
    ArtifactBase,
    Identifier,
    NonEmptyStr,
    StrictModel,
)


class Criterion(StrictModel):
    """A testable gate. Prose that cannot be checked is not a criterion."""

    id: Identifier
    statement: NonEmptyStr
    verification_method: NonEmptyStr
    owner_role: NonEmptyStr
    automated: bool = False


class MigrationWave(ArtifactBase):
    artifact_type: str = "migration-wave"
    name: NonEmptyStr
    sequence: int = Field(ge=1)
    objective: NonEmptyStr
    is_pilot: bool = False
    depends_on_wave_ids: list[Identifier] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    entry_criteria: list[Criterion] = Field(default_factory=list)
    exit_criteria: list[Criterion] = Field(min_length=1)
    owner_roles: list[str] = Field(min_length=1)
    planned_start: date | None = None
    planned_end: date | None = None
    rollback_required: bool = True

    @model_validator(mode="after")
    def _wave_has_workloads(self) -> MigrationWave:
        if not self.workload_ids:
            raise ValueError(f"Wave {self.id} contains no workloads")
        return self

    @model_validator(mode="after")
    def _pilot_is_first_and_small(self) -> MigrationWave:
        if self.is_pilot and self.sequence != 1:
            raise ValueError("A pilot wave must be sequence 1; later waves learn from it")
        if self.is_pilot and len(self.workload_ids) > 3:
            raise ValueError(
                f"Pilot wave {self.id} contains {len(self.workload_ids)} workloads. "
                "A pilot that large does not de-risk anything."
            )
        return self

    @model_validator(mode="after")
    def _dates_are_ordered(self) -> MigrationWave:
        if self.planned_start and self.planned_end and self.planned_end < self.planned_start:
            raise ValueError(f"Wave {self.id} ends before it starts")
        return self


class WavePlan(StrictModel):
    engagement_id: Identifier
    waves: list[MigrationWave] = Field(default_factory=list)
    deferred_workload_ids: list[Identifier] = Field(
        default_factory=list,
        description=(
            "Workloads not scheduled into any wave: those with open blocking findings, and "
            "those whose disposition is retain, retire, or replace. A wave moves workloads, "
            "so counting a non-moving workload as scheduled would overstate progress."
        ),
    )

    @model_validator(mode="after")
    def _sequences_and_dependencies_are_sane(self) -> WavePlan:
        sequences = [w.sequence for w in self.waves]
        if len(set(sequences)) != len(sequences):
            raise ValueError("Wave sequences must be unique")
        known = {w.id for w in self.waves}
        by_id = {w.id: w for w in self.waves}
        for wave in self.waves:
            for dependency in wave.depends_on_wave_ids:
                if dependency not in known:
                    raise ValueError(f"Wave {wave.id} depends on unknown wave {dependency}")
                if by_id[dependency].sequence >= wave.sequence:
                    raise ValueError(
                        f"Wave {wave.id} (sequence {wave.sequence}) depends on "
                        f"{dependency} (sequence {by_id[dependency].sequence}), which runs later"
                    )
        assigned: set[str] = set()
        for wave in self.waves:
            overlap = assigned & set(wave.workload_ids)
            if overlap:
                raise ValueError(f"Workloads appear in more than one wave: {sorted(overlap)}")
            assigned |= set(wave.workload_ids)
        return self


class TaskKind(StrEnum):
    PREPARE = "prepare"
    BUILD = "build"
    MIGRATE = "migrate"
    VALIDATE = "validate"
    CUTOVER = "cutover"
    STABILIZE = "stabilize"
    OPTIMIZE = "optimize"
    DECOMMISSION = "decommission"


class PlanTask(StrictModel):
    id: Identifier
    title: NonEmptyStr
    kind: TaskKind
    description: NonEmptyStr
    owner_role: NonEmptyStr
    depends_on: list[Identifier] = Field(default_factory=list)
    dry_run_command: str | None = Field(
        default=None, description="A command that shows the effect without making a change."
    )
    changes_environment: bool = False
    approval_required: bool = False
    rollback_note: str | None = None
    policy_ids: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _mutating_tasks_are_gated(self) -> PlanTask:
        if self.changes_environment:
            if not self.approval_required:
                raise ValueError(
                    f"Task {self.id} changes an environment but does not require approval"
                )
            if not self.rollback_note:
                raise ValueError(
                    f"Task {self.id} changes an environment but documents no rollback path"
                )
        return self


class PlanPhase(StrictModel):
    name: NonEmptyStr
    objective: NonEmptyStr
    tasks: list[PlanTask] = Field(min_length=1)


class CutoverPlan(StrictModel):
    freeze_start: str = Field(description="Relative or absolute, e.g. 'T-4h' or a date-time.")
    replication_method: NonEmptyStr
    go_no_go_criteria: list[Criterion] = Field(min_length=1)
    communication_plan: list[str] = Field(min_length=1)
    required_approval_roles: list[ApprovalRole] = Field(min_length=5)
    execution_window: NonEmptyStr
    owner_role: NonEmptyStr

    @model_validator(mode="after")
    def _all_five_roles_required(self) -> CutoverPlan:
        from dbmodernize.models.base import CUTOVER_REQUIRED_ROLES

        missing = CUTOVER_REQUIRED_ROLES - set(self.required_approval_roles)
        if missing:
            raise ValueError(
                "Cutover approval is missing required roles: "
                + ", ".join(sorted(role.value for role in missing))
            )
        return self


class RollbackPlan(StrictModel):
    triggers: list[Criterion] = Field(min_length=1)
    method: NonEmptyStr
    maximum_decision_window: NonEmptyStr
    data_reconciliation_note: NonEmptyStr
    owner_role: NonEmptyStr
    rehearsed: bool = False
    evidence_preservation: NonEmptyStr = Field(
        description="What is captured before rollback so the failure can be analysed."
    )


class MigrationPlan(ArtifactBase):
    artifact_type: str = "migration-plan"
    wave_id: Identifier
    target_decision_ids: list[Identifier] = Field(min_length=1)
    phases: list[PlanPhase] = Field(min_length=1)
    cutover: CutoverPlan
    rollback: RollbackPlan
    acceptance_criteria: list[Criterion] = Field(min_length=1)
    validation_plan_ref: str | None = None

    @model_validator(mode="after")
    def _task_dependencies_resolve(self) -> MigrationPlan:
        known = {task.id for phase in self.phases for task in phase.tasks}
        for phase in self.phases:
            for task in phase.tasks:
                unknown = [d for d in task.depends_on if d not in known]
                if unknown:
                    raise ValueError(f"Task {task.id} depends on unknown tasks: {unknown}")
                if task.id in task.depends_on:
                    raise ValueError(f"Task {task.id} depends on itself")
        return self

    @model_validator(mode="after")
    def _plan_has_validation_before_cutover(self) -> MigrationPlan:
        kinds = [task.kind for phase in self.phases for task in phase.tasks]
        if TaskKind.VALIDATE not in kinds:
            raise ValueError(
                f"Plan {self.id} has no validation task. A plan without validation "
                "cannot support a go/no-go decision."
            )
        return self
