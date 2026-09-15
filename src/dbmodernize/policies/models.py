"""Playbook models: the enterprise decision and governance contract.

A playbook captures *decisions* — what is approved, what is prohibited, what must hold.
Procedures live in Agent Skills. Copying a procedure into a playbook makes it impossible
to change the procedure without a governance review, which is the wrong trade.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import Field, model_validator

from dbmodernize.models.approval import PolicyException
from dbmodernize.models.base import AzureTarget, NonEmptyStr, StrictModel


class Directive(StrEnum):
    """What a policy does to the subject it names."""

    REQUIRED = "required"
    PROHIBITED = "prohibited"
    RECOMMENDED = "recommended"
    DISCOURAGED = "discouraged"


#: Directive pairs that cannot both hold for the same subject and scope.
HARD_CONFLICTS: frozenset[frozenset[Directive]] = frozenset(
    {frozenset({Directive.REQUIRED, Directive.PROHIBITED})}
)
SOFT_CONFLICTS: frozenset[frozenset[Directive]] = frozenset(
    {
        frozenset({Directive.RECOMMENDED, Directive.DISCOURAGED}),
        frozenset({Directive.REQUIRED, Directive.DISCOURAGED}),
        frozenset({Directive.PROHIBITED, Directive.RECOMMENDED}),
    }
)


class PolicyCategory(StrEnum):
    SECURITY = "security"
    COMPLIANCE = "compliance"
    NAMING = "naming"
    IDENTITY = "identity"
    NETWORKING = "networking"
    DATA = "data"
    OBSERVABILITY = "observability"
    AVAILABILITY = "availability"
    COST = "cost"
    VALIDATION = "validation"
    OPERATIONS = "operations"


class Policy(StrictModel):
    """One governance rule.

    ``subject`` is a stable dotted key such as ``network.public-endpoint``. Two policies
    sharing a subject and scope with opposing directives are a conflict, and conflicts
    fail validation rather than being resolved silently.
    """

    id: NonEmptyStr = Field(pattern=r"^[A-Z]{2,4}-\d{3}$")
    category: PolicyCategory
    subject: NonEmptyStr = Field(pattern=r"^[a-z0-9]+(\.[a-z0-9\-]+)+$")
    directive: Directive
    requirement: NonEmptyStr
    applies_to: NonEmptyStr = Field(
        default="all",
        description="Scope key: 'all', an environment, a platform, or a target code.",
    )

    @property
    def scope_key(self) -> tuple[str, str]:
        return (self.subject, self.applies_to)


class TargetPolicy(StrictModel):
    """Whether a target may be recommended under this playbook, and on what terms."""

    target: AzureTarget
    status: str = Field(pattern=r"^(approved|conditional|prohibited)$")
    conditions: str = ""

    @model_validator(mode="after")
    def _conditional_needs_conditions(self) -> TargetPolicy:
        if self.status == "conditional" and not self.conditions.strip():
            raise ValueError(
                f"Target {self.target.value} is conditional but states no conditions. "
                "A condition nobody can check is not a condition."
            )
        return self


class Playbook(StrictModel):
    """The parsed, validated playbook."""

    name: NonEmptyStr
    version: NonEmptyStr
    path: NonEmptyStr
    charter_sections: dict[str, str] = Field(default_factory=dict)
    policies: list[Policy] = Field(default_factory=list)
    targets: list[TargetPolicy] = Field(default_factory=list)
    exceptions: list[PolicyException] = Field(default_factory=list)
    extended: dict[str, str] = Field(
        default_factory=dict,
        description=(
            "Content that did not map to the schema. Retained verbatim so nothing is lost, "
            "but enforcement over it is best-effort only."
        ),
    )

    def policy(self, policy_id: str) -> Policy | None:
        return next((p for p in self.policies if p.id == policy_id), None)

    def target_status(self, target: AzureTarget) -> str:
        entry = next((t for t in self.targets if t.target is target), None)
        return entry.status if entry else "prohibited"

    def allowed_targets(self) -> list[AzureTarget]:
        return [t.target for t in self.targets if t.status in {"approved", "conditional"}]

    def prohibited_targets(self) -> list[AzureTarget]:
        return [t.target for t in self.targets if t.status == "prohibited"]

    def active_exceptions(self, as_of: date) -> list[PolicyException]:
        return [e for e in self.exceptions if not e.is_expired(as_of)]

    def policy_ids_for(self, categories: set[PolicyCategory]) -> list[str]:
        return sorted(p.id for p in self.policies if p.category in categories)


__all__ = [
    "HARD_CONFLICTS",
    "SOFT_CONFLICTS",
    "Directive",
    "Playbook",
    "Policy",
    "PolicyCategory",
    "PolicyException",
    "TargetPolicy",
]
