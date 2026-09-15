"""Validation plans and reports: the evidence behind a go / no-go decision."""

from __future__ import annotations

from enum import StrEnum

from pydantic import Field, model_validator

from dbmodernize.models.base import (
    ArtifactBase,
    Identifier,
    NonEmptyStr,
    StrictModel,
)


class CheckCategory(StrEnum):
    INVENTORY = "inventory"
    CONFIGURATION = "configuration"
    SCHEMA = "schema"
    DATA_RECONCILIATION = "data-reconciliation"
    DATA_TYPES = "data-types"
    REFERENTIAL_INTEGRITY = "referential-integrity"
    PROGRAMMABILITY = "programmability"
    CONNECTIVITY = "connectivity"
    FUNCTIONAL = "functional"
    REGRESSION = "regression"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    CONCURRENCY = "concurrency"
    AVAILABILITY = "availability"
    BACKUP_RESTORE = "backup-restore"
    RPO_RTO = "rpo-rto"
    SECURITY_CONFIGURATION = "security-configuration"
    IDENTITY = "identity"
    NETWORK_ISOLATION = "network-isolation"
    ENCRYPTION = "encryption"
    AUDITING = "auditing"
    POSTURE = "posture"
    COST_SIZING = "cost-sizing"
    MONITORING = "monitoring"
    RUNBOOKS = "runbooks"
    BUSINESS_ACCEPTANCE = "business-acceptance"


class CheckResult(StrEnum):
    PASS = "pass"  # noqa: S105 - a check result, not a credential
    FAIL = "fail"
    NOT_RUN = "not-run"
    NOT_APPLICABLE = "not-applicable"


class Outcome(StrEnum):
    GO = "go"
    CONDITIONAL_GO = "conditional-go"
    NO_GO = "no-go"


class ValidationCheck(StrictModel):
    id: Identifier
    category: CheckCategory
    name: NonEmptyStr
    method: NonEmptyStr
    tolerance: str | None = Field(
        default=None, description="The threshold that separates pass from fail."
    )
    baseline: str | None = None
    observed: str | None = None
    result: CheckResult = CheckResult.NOT_RUN
    evidence_refs: list[Identifier] = Field(default_factory=list)
    blocking: bool = True
    notes: str | None = None
    generated_test: bool = Field(
        default=False,
        description=(
            "True when the check is an auto-generated test. Generated tests are supporting "
            "evidence and never sufficient proof on their own."
        ),
    )

    @model_validator(mode="after")
    def _completed_checks_record_what_was_seen(self) -> ValidationCheck:
        if self.result in {CheckResult.PASS, CheckResult.FAIL} and self.observed is None:
            raise ValueError(
                f"Check {self.id} reports {self.result.value} but records no observed value"
            )
        return self


class BusinessAcceptance(StrictModel):
    business_owner_accepted: bool = False
    application_owner_accepted: bool = False
    accepted_on: str | None = None
    conditions: list[str] = Field(default_factory=list)


class ValidationReport(ArtifactBase):
    artifact_type: str = "validation-report"
    wave_id: Identifier
    migration_plan_id: Identifier
    executed_on: str = Field(description="Date or window the validation ran.")
    checks: list[ValidationCheck] = Field(min_length=1)
    outcome: Outcome
    rollback_triggered: bool = False
    rollback_reason: str | None = None
    business_acceptance: BusinessAcceptance = Field(default_factory=BusinessAcceptance)
    corrective_issue_ids: list[str] = Field(default_factory=list)

    @property
    def counts(self) -> dict[str, int]:
        tally = {result.value: 0 for result in CheckResult}
        for check in self.checks:
            tally[check.result.value] += 1
        return tally

    @property
    def blocking_failures(self) -> list[ValidationCheck]:
        return [c for c in self.checks if c.blocking and c.result is CheckResult.FAIL]

    @property
    def blocking_not_run(self) -> list[ValidationCheck]:
        return [c for c in self.checks if c.blocking and c.result is CheckResult.NOT_RUN]

    @property
    def only_generated_evidence(self) -> bool:
        executed = [c for c in self.checks if c.result is CheckResult.PASS]
        return bool(executed) and all(c.generated_test for c in executed)

    @model_validator(mode="after")
    def _outcome_follows_the_evidence(self) -> ValidationReport:
        if self.blocking_failures and self.outcome is not Outcome.NO_GO:
            names = ", ".join(c.id for c in self.blocking_failures)
            raise ValueError(
                f"Report {self.id} has blocking failures ({names}) but outcome is "
                f"{self.outcome.value}. Blocking failures force a no-go."
            )
        if self.blocking_not_run and self.outcome is Outcome.GO:
            names = ", ".join(c.id for c in self.blocking_not_run)
            raise ValueError(
                f"Report {self.id} declares go while blocking checks have not run ({names}). "
                "Use conditional-go or no-go."
            )
        if self.outcome is Outcome.GO and not (
            self.business_acceptance.business_owner_accepted
            and self.business_acceptance.application_owner_accepted
        ):
            raise ValueError(
                f"Report {self.id} declares go without business and application owner acceptance."
            )
        return self

    @model_validator(mode="after")
    def _rollback_is_explained(self) -> ValidationReport:
        if self.rollback_triggered and not self.rollback_reason:
            raise ValueError(f"Report {self.id} triggered rollback without recording why")
        if self.outcome is Outcome.NO_GO and not self.corrective_issue_ids:
            raise ValueError(
                f"Report {self.id} is a no-go but generates no corrective issues. "
                "A failure with no follow-up work is not a result."
            )
        return self

    @model_validator(mode="after")
    def _generated_tests_are_not_proof(self) -> ValidationReport:
        if self.outcome is Outcome.GO and self.only_generated_evidence:
            raise ValueError(
                f"Report {self.id} rests entirely on generated tests. Generated tests are "
                "supporting evidence, not migration proof; add an independently executed "
                "check before declaring go."
            )
        return self
