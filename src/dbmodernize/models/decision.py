"""Target decision: the justified Azure destination for one workload."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from dbmodernize.models.base import (
    ArtifactBase,
    ArtifactStatus,
    AzureTarget,
    Disposition,
    DowntimeClass,
    Identifier,
    NonEmptyStr,
    StrictModel,
)


class OptionVerdict(StrEnum):
    RECOMMENDED = "recommended"
    VIABLE = "viable"
    REJECTED = "rejected"
    BLOCKED = "blocked"


class ConsideredOption(StrictModel):
    """One evaluated target. Rejected options are kept so the reasoning survives review."""

    target: AzureTarget
    verdict: OptionVerdict
    score: float = Field(ge=0.0, le=100.0)
    rationale: NonEmptyStr
    blockers: list[str] = Field(default_factory=list)
    evidence_refs: list[Identifier] = Field(default_factory=list)

    @model_validator(mode="after")
    def _blocked_needs_a_blocker(self) -> ConsideredOption:
        if self.verdict is OptionVerdict.BLOCKED and not self.blockers:
            raise ValueError(f"Option {self.target} is blocked but names no blocker")
        if self.verdict is OptionVerdict.REJECTED and not self.rationale:
            raise ValueError(f"Option {self.target} is rejected without a rationale")
        return self


class DowntimeApproach(StrictModel):
    """Downtime expectations must name the method that justifies them."""

    method: NonEmptyStr = Field(
        description="e.g. 'log replay with a short application cutover window'."
    )
    expected_class: DowntimeClass = DowntimeClass.UNKNOWN
    basis: NonEmptyStr = Field(
        description="Why this class is credible for this workload, or 'not yet measured'."
    )
    measured: bool = False

    @model_validator(mode="after")
    def _no_zero_downtime_claims(self) -> DowntimeApproach:
        lowered = f"{self.method} {self.basis}".lower()
        if "zero downtime" in lowered or "no downtime" in lowered:
            raise ValueError(
                "Zero-downtime claims are not permitted. Use 'near-zero-planned' with a "
                "method-specific basis, and record the measurement that supports it."
            )
        if self.expected_class is DowntimeClass.NEAR_ZERO_PLANNED and not self.measured:
            raise ValueError(
                "near-zero-planned requires measured evidence. Until a rehearsal has been "
                "run, use short-planned or unknown."
            )
        return self


class CostInput(StrictModel):
    """A cost figure supplied by a human. The repository never invents one."""

    id: Identifier
    label: NonEmptyStr
    amount: float
    currency: str = Field(min_length=3, max_length=3)
    period: str = Field(description="one-off | monthly | annual")
    source: NonEmptyStr
    is_estimate: bool = True


class TargetDecision(ArtifactBase):
    """A per-workload recommendation with its rejected alternatives attached."""

    artifact_type: str = "target-decision"
    workload_id: Identifier
    recommended_target: AzureTarget
    disposition: Disposition
    rationale: NonEmptyStr
    considered_options: list[ConsideredOption] = Field(min_length=2)
    compatibility_notes: list[str] = Field(default_factory=list)
    operational_notes: list[str] = Field(default_factory=list)
    security_notes: list[str] = Field(default_factory=list)
    performance_notes: list[str] = Field(default_factory=list)
    sovereignty_notes: list[str] = Field(default_factory=list)
    application_impact: list[str] = Field(default_factory=list)
    cost_inputs: list[CostInput] = Field(default_factory=list)
    downtime_approach: DowntimeApproach
    requires_application_change: bool = False
    conversion_required: bool = Field(
        default=False, description="True for heterogeneous migrations needing schema/code change."
    )

    @model_validator(mode="after")
    def _recommendation_is_among_options(self) -> TargetDecision:
        recommended = [o for o in self.considered_options if o.verdict is OptionVerdict.RECOMMENDED]
        if len(recommended) != 1:
            raise ValueError(
                "Exactly one considered option must be marked recommended, found "
                f"{len(recommended)}"
            )
        if recommended[0].target != self.recommended_target:
            raise ValueError(
                "recommended_target does not match the option marked recommended: "
                f"{self.recommended_target} vs {recommended[0].target}"
            )
        alternatives = [
            o
            for o in self.considered_options
            if o.verdict in {OptionVerdict.REJECTED, OptionVerdict.BLOCKED}
        ]
        if not alternatives:
            raise ValueError(
                "A target decision must show at least one alternative that was rejected or "
                "blocked, with its reason. A single-option comparison is not a decision."
            )
        return self

    @model_validator(mode="after")
    def _recommendation_needs_evidence(self) -> TargetDecision:
        if self.status is not ArtifactStatus.DRAFT and not self.evidence_refs:
            raise ValueError(
                f"Target decision {self.id} has status {self.status} but cites no evidence"
            )
        return self

    @model_validator(mode="after")
    def _approval_requires_an_approval_artifact(self) -> TargetDecision:
        if self.status is ArtifactStatus.APPROVED and not self.approvals:
            raise ValueError(
                f"Target decision {self.id} is approved but references no approval artifact. "
                "A recommendation cannot approve itself."
            )
        return self

    @model_validator(mode="after")
    def _oracle_conversion_is_never_automatic(self) -> TargetDecision:
        heterogeneous = self.disposition in {
            Disposition.REFACTOR,
            Disposition.REARCHITECT,
            Disposition.REBUILD,
        }
        if heterogeneous and not self.conversion_required:
            raise ValueError(
                f"Disposition {self.disposition} implies schema or code conversion; "
                "conversion_required must be true."
            )
        return self

    @property
    def rejected_alternatives(self) -> list[ConsideredOption]:
        return [
            o
            for o in self.considered_options
            if o.verdict in {OptionVerdict.REJECTED, OptionVerdict.BLOCKED}
        ]


class TargetDecisionSet(StrictModel):
    engagement_id: Identifier
    decisions: list[TargetDecision] = Field(default_factory=list)
    unresolved_workload_ids: list[Identifier] = Field(
        default_factory=list,
        description=(
            "Workloads with open blocking findings. No destination may be recommended for "
            "these; any decision they carry is an interim posture, not a migration target."
        ),
    )

    def get(self, workload_id: str) -> TargetDecision | None:
        return next((d for d in self.decisions if d.workload_id == workload_id), None)
