"""Approval artifacts. The only mechanism that turns a recommendation into a decision."""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from pydantic import Field, model_validator

from dbmodernize.models.base import (
    ApprovalRole,
    Identifier,
    NonEmptyStr,
    StrictModel,
)


class ApprovalDecision(StrEnum):
    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved-with-conditions"
    REJECTED = "rejected"


class Approval(StrictModel):
    """One role's signature against one artifact version.

    ``artifact_hash`` pins the exact content approved. Editing the artifact afterwards
    invalidates the approval rather than silently carrying it forward.
    """

    id: Identifier
    schema_version: str = "1.0.0"
    artifact_type: str = "approval"
    engagement_id: Identifier
    approved_artifact_id: Identifier
    approved_artifact_type: NonEmptyStr
    artifact_hash: str = Field(pattern=r"^sha256:[a-f0-9]{64}$")
    role: ApprovalRole
    approver_principal: NonEmptyStr = Field(
        description="Pseudonymous principal, e.g. 'security-owner-a'. Never a real email."
    )
    artifact_author: NonEmptyStr = Field(
        description="Copied from the approved artifact so self-approval is detectable."
    )
    decision: ApprovalDecision
    approved_at: datetime
    conditions: list[str] = Field(default_factory=list)
    scope: NonEmptyStr
    expires_on: date | None = None
    comments: str | None = None

    @model_validator(mode="after")
    def _no_self_approval(self) -> Approval:
        if self.approver_principal.strip().lower() == self.artifact_author.strip().lower():
            raise ValueError(
                f"Approval {self.id}: {self.approver_principal} authored the artifact and "
                "cannot approve it. Approval requires a different principal."
            )
        if self.artifact_author.lower().startswith(
            "agent:"
        ) and self.approver_principal.lower().startswith("agent:"):
            raise ValueError(
                f"Approval {self.id}: an agent cannot approve an agent-authored artifact. "
                "Approval is a human decision."
            )
        return self

    @model_validator(mode="after")
    def _conditional_approval_lists_conditions(self) -> Approval:
        if self.decision is ApprovalDecision.APPROVED_WITH_CONDITIONS and not self.conditions:
            raise ValueError(f"Approval {self.id} is conditional but lists no conditions")
        return self


class PolicyException(StrictModel):
    """A time-boxed, compensated deviation from the playbook."""

    id: Identifier
    policy_id: NonEmptyStr
    scope: NonEmptyStr
    justification: NonEmptyStr
    owner_role: NonEmptyStr
    approver_role: NonEmptyStr
    approver_principal: NonEmptyStr
    compensating_controls: list[str] = Field(min_length=1)
    granted_on: date
    expires_on: date
    review_on: date

    @model_validator(mode="after")
    def _dates_are_ordered(self) -> PolicyException:
        if self.expires_on <= self.granted_on:
            raise ValueError(f"Exception {self.id} expires on or before it was granted")
        if self.review_on > self.expires_on:
            raise ValueError(f"Exception {self.id} is reviewed after it expires")
        return self

    @model_validator(mode="after")
    def _requester_is_not_approver(self) -> PolicyException:
        if self.owner_role.strip().lower() == self.approver_role.strip().lower():
            raise ValueError(
                f"Exception {self.id}: the requesting role cannot also be the approving role"
            )
        return self

    def is_expired(self, as_of: date) -> bool:
        return as_of > self.expires_on


class ApprovalLedger(StrictModel):
    engagement_id: Identifier
    approvals: list[Approval] = Field(default_factory=list)
    exceptions: list[PolicyException] = Field(default_factory=list)

    def for_artifact(self, artifact_id: str) -> list[Approval]:
        return [a for a in self.approvals if a.approved_artifact_id == artifact_id]

    def roles_approving(self, artifact_id: str) -> set[ApprovalRole]:
        return {
            a.role
            for a in self.for_artifact(artifact_id)
            if a.decision is not ApprovalDecision.REJECTED
        }
