"""Risk register entries."""

from __future__ import annotations

from datetime import date
from enum import StrEnum

from pydantic import Field, model_validator

from dbmodernize.models.base import (
    ArtifactBase,
    Identifier,
    Likelihood,
    NonEmptyStr,
    Severity,
    StrictModel,
)

_LEVEL = {Likelihood.LOW: 1, Likelihood.MEDIUM: 2, Likelihood.HIGH: 3}


class RiskCategory(StrEnum):
    TECHNICAL = "technical"
    DATA = "data"
    APPLICATION = "application"
    SECURITY = "security"
    COMPLIANCE = "compliance"
    OPERATIONAL = "operational"
    COMMERCIAL = "commercial"
    SCHEDULE = "schedule"
    PEOPLE = "people"


class RiskStatus(StrEnum):
    OPEN = "open"
    MITIGATING = "mitigating"
    ACCEPTED = "accepted"
    CLOSED = "closed"


class Risk(ArtifactBase):
    artifact_type: str = "risk"
    title: NonEmptyStr
    description: NonEmptyStr
    category: RiskCategory
    likelihood: Likelihood
    impact: Likelihood
    owner_role: NonEmptyStr
    mitigation: NonEmptyStr
    contingency: str | None = None
    trigger: str | None = Field(
        default=None, description="The observable condition that means the risk has materialised."
    )
    risk_status: RiskStatus = RiskStatus.OPEN
    due_date: date | None = None
    accepted_by_role: str | None = None
    accepted_on: date | None = None

    @model_validator(mode="after")
    def _acceptance_is_attributed(self) -> Risk:
        if self.risk_status is RiskStatus.ACCEPTED and not (
            self.accepted_by_role and self.accepted_on
        ):
            raise ValueError(
                f"Risk {self.id} is accepted but does not record who accepted it and when. "
                "Unattributed risk acceptance is not acceptance."
            )
        return self

    @model_validator(mode="after")
    def _high_risk_needs_contingency(self) -> Risk:
        if self.severity in {Severity.HIGH, Severity.BLOCKER} and not self.contingency:
            raise ValueError(
                f"Risk {self.id} scores {self.severity} and needs a contingency, "
                "not only a mitigation."
            )
        return self

    @property
    def score(self) -> int:
        return _LEVEL[self.likelihood] * _LEVEL[self.impact]

    @property
    def severity(self) -> Severity:
        score = self.score
        if score >= 9:
            return Severity.BLOCKER
        if score >= 6:
            return Severity.HIGH
        if score >= 3:
            return Severity.MEDIUM
        return Severity.LOW


class RiskRegister(StrictModel):
    engagement_id: Identifier
    risks: list[Risk] = Field(default_factory=list)

    @model_validator(mode="after")
    def _unique_ids(self) -> RiskRegister:
        seen: set[str] = set()
        for risk in self.risks:
            if risk.id in seen:
                raise ValueError(f"Duplicate risk id: {risk.id}")
            seen.add(risk.id)
        return self

    @property
    def open_high_risks(self) -> list[Risk]:
        return [
            r
            for r in self.risks
            if r.risk_status in {RiskStatus.OPEN, RiskStatus.MITIGATING}
            and r.severity in {Severity.HIGH, Severity.BLOCKER}
        ]
