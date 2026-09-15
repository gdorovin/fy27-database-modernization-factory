"""GitHub issue definitions.

These are generated to disk. Creating live issues is a separate, explicitly confirmed
step; see ``dbmodernize generate-issues --help``.
"""

from __future__ import annotations

from pydantic import Field, model_validator

from dbmodernize.models.base import (
    Identifier,
    NonEmptyStr,
    PlaybookRef,
    StrictModel,
)


class GithubIssue(StrictModel):
    """One actionable unit of work, traceable back to evidence and a target decision."""

    id: Identifier
    title: NonEmptyStr = Field(max_length=120)
    engagement_id: Identifier
    workload_ids: list[Identifier] = Field(default_factory=list)
    problem_statement: NonEmptyStr
    source_evidence: list[Identifier] = Field(default_factory=list)
    approved_target: str | None = Field(
        default=None,
        description="Null when the issue precedes an approved target decision.",
    )
    target_decision_id: Identifier | None = None
    playbook: PlaybookRef
    dependencies: list[str] = Field(default_factory=list)
    scope: list[str] = Field(min_length=1)
    out_of_scope: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(min_length=1)
    validation_commands: list[str] = Field(default_factory=list)
    security_considerations: list[str] = Field(default_factory=list)
    rollback_considerations: list[str] = Field(default_factory=list)
    owner_role: NonEmptyStr
    labels: list[str] = Field(default_factory=list)
    milestone: str | None = Field(default=None, description="Usually the wave name.")
    blocked_by: list[str] = Field(default_factory=list)
    definition_of_done: list[str] = Field(min_length=1)

    @model_validator(mode="after")
    def _normalise_collections(self) -> GithubIssue:
        self.labels = sorted(set(self.labels))
        self.blocked_by = sorted(set(self.blocked_by))
        return self

    @model_validator(mode="after")
    def _environment_changing_work_has_rollback(self) -> GithubIssue:
        mutating_labels = {"cutover", "migrate", "deploy", "production"}
        if mutating_labels & set(self.labels) and not self.rollback_considerations:
            raise ValueError(
                f"Issue {self.id} is labelled for an environment-changing activity but "
                "documents no rollback considerations."
            )
        return self

    @model_validator(mode="after")
    def _claims_are_grounded(self) -> GithubIssue:
        if self.approved_target and not self.target_decision_id:
            raise ValueError(
                f"Issue {self.id} names an approved target without referencing the "
                "target decision that approved it."
            )
        return self


class IssueSet(StrictModel):
    engagement_id: Identifier
    issues: list[GithubIssue] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_and_resolvable(self) -> IssueSet:
        ids = [issue.id for issue in self.issues]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate issue ids")
        known = set(ids)
        for issue in self.issues:
            unknown = [b for b in issue.blocked_by if b not in known]
            if unknown:
                raise ValueError(f"Issue {issue.id} is blocked by unknown issues: {unknown}")
        return self
