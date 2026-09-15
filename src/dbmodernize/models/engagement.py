"""Engagement intake: the customer outcome, trigger, constraints, and cadence."""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import Field, model_validator

from dbmodernize.models.base import (
    ArtifactBase,
    Identifier,
    NonEmptyStr,
    StrictModel,
)


class EngagementTrigger(StrEnum):
    """Why the conversation is happening now.

    All of these lead into the same modernization journey; they differ in urgency,
    sponsor, and the evidence already available.
    """

    LICENSE_OR_EA_RENEWAL = "license-or-ea-renewal"
    END_OF_SUPPORT = "end-of-support"
    AGING_HARDWARE = "aging-hardware"
    SECURITY_OR_COMPLIANCE_FINDING = "security-or-compliance-finding"
    APPLICATION_MODERNIZATION = "application-modernization"
    DATACENTER_EXIT = "datacenter-exit"
    STALLED_MIGRATION = "stalled-migration"
    AI_OR_ANALYTICS_REQUIREMENT = "ai-or-analytics-requirement"
    ORACLE_COST_OR_AUDIT_PRESSURE = "oracle-cost-or-audit-pressure"
    UNSUPPORTED_OPEN_SOURCE_VERSION = "unsupported-open-source-version"
    COMPETITIVE_CLOUD_PRESSURE = "competitive-cloud-pressure"
    AVAILABILITY_OR_DR_GAP = "availability-or-dr-gap"
    OPERATIONAL_SCALE = "operational-scale"
    OTHER = "other"


class Stakeholder(StrictModel):
    role: NonEmptyStr
    alias: NonEmptyStr = Field(
        description="Pseudonym, never a real name or email. Example: 'sponsor-a'."
    )
    responsibility: NonEmptyStr
    decision_rights: list[str] = Field(default_factory=list)


class SuccessMeasure(StrictModel):
    """A measure the customer agrees to be judged on. Baseline may be unknown."""

    id: Identifier
    statement: NonEmptyStr
    baseline: str | None = None
    target: str | None = None
    measured_by: NonEmptyStr
    baseline_known: bool = False

    @model_validator(mode="after")
    def _baseline_consistency(self) -> SuccessMeasure:
        if self.baseline_known and not self.baseline:
            raise ValueError("baseline_known is true but no baseline value was supplied")
        return self


class Constraint(StrictModel):
    id: Identifier
    category: str = Field(
        description="One of: regulatory, contractual, technical, operational, budget, calendar."
    )
    statement: NonEmptyStr
    hard: bool = Field(default=True, description="A hard constraint cannot be traded away.")
    source: NonEmptyStr


class CadenceMilestone(StrictModel):
    """One entry in the renewal-oriented cadence. Configurable, not a fixed schedule."""

    label: NonEmptyStr = Field(description="For example 'T-12', 'T-3', 'T+90'.")
    objective: NonEmptyStr
    target_date: date | None = None
    owner_role: NonEmptyStr
    complete: bool = False


class EngagementScope(StrictModel):
    in_scope: list[str] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)
    estate_summary: str | None = None
    estimated_workload_count: int | None = Field(default=None, ge=0)
    estimated_count_is_assumption: bool = True


class Engagement(ArtifactBase):
    """The intake artifact. Everything downstream references its ``engagement_id``."""

    artifact_type: str = "engagement"
    customer_alias: NonEmptyStr = Field(
        description="Pseudonym such as 'contoso-retail'. Never a real customer name."
    )
    as_of: date = Field(
        description=(
            "The date the engagement state was captured. Renderers use this instead of "
            "the wall clock so that generated documents are reproducible."
        )
    )
    primary_trigger: EngagementTrigger
    secondary_triggers: list[EngagementTrigger] = Field(default_factory=list)
    desired_outcomes: list[str] = Field(
        min_length=1,
        description="Business outcomes in the customer's words, not product names.",
    )
    business_context: NonEmptyStr
    scope: EngagementScope
    constraints: list[Constraint] = Field(default_factory=list)
    stakeholders: list[Stakeholder] = Field(default_factory=list)
    success_measures: list[SuccessMeasure] = Field(default_factory=list)
    renewal_date: date | None = None
    target_first_workload_live: date | None = None
    cadence: list[CadenceMilestone] = Field(default_factory=list)

    @model_validator(mode="after")
    def _outcomes_are_not_product_names(self) -> Engagement:
        product_words = ("azure sql", "managed instance", "hyperscale", "fabric", "cosmos")
        for outcome in self.desired_outcomes:
            lowered = outcome.lower()
            if any(lowered.startswith(word) for word in product_words):
                raise ValueError(
                    f"desired_outcomes entry {outcome!r} names a product. "
                    "Outcomes describe the business result; targets are decided later "
                    "from evidence."
                )
        return self

    @model_validator(mode="after")
    def _renewal_trigger_needs_a_date(self) -> Engagement:
        if (
            self.primary_trigger is EngagementTrigger.LICENSE_OR_EA_RENEWAL
            and not self.renewal_date
        ):
            raise ValueError(
                "primary_trigger is license-or-ea-renewal but renewal_date is unset. "
                "Record it as unknown in open_questions if it truly is not known."
            )
        return self
