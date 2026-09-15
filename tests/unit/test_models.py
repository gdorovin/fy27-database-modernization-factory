"""Model invariants.

These are the rules that cannot be expressed in JSON Schema, so this file is where the
safety properties actually live. Each test names the failure it prevents.
"""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from dbmodernize.models.approval import Approval, ApprovalDecision, PolicyException
from dbmodernize.models.base import (
    ApprovalRole,
    ArtifactStatus,
    AzureTarget,
    Disposition,
    DowntimeClass,
    EvidenceClass,
    Likelihood,
    PlaybookRef,
    Severity,
)
from dbmodernize.models.decision import (
    ConsideredOption,
    DowntimeApproach,
    OptionVerdict,
    TargetDecision,
)
from dbmodernize.models.engagement import Engagement, EngagementScope, EngagementTrigger
from dbmodernize.models.evidence import EvidenceRecord, EvidenceSource
from dbmodernize.models.planning import (
    Criterion,
    MigrationWave,
    PlanTask,
    TaskKind,
    WavePlan,
)
from dbmodernize.models.risk import Risk, RiskCategory, RiskStatus
from dbmodernize.models.validation import (
    BusinessAcceptance,
    CheckCategory,
    CheckResult,
    Outcome,
    ValidationCheck,
    ValidationReport,
)
from dbmodernize.models.workload import AssessmentFinding, FindingCategory, SupportStatus, Workload
from tests.conftest import AS_OF, TIMESTAMP


def _base(playbook_ref: PlaybookRef, **overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "engagement_id": "eng-test",
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
        "author": "agent:test",
        "playbook": playbook_ref,
    }
    payload.update(overrides)
    return payload


class TestEngagement:
    def test_outcome_naming_a_product_is_rejected(self, playbook_ref: PlaybookRef) -> None:
        """An outcome that names a product pre-decides the target before any evidence."""
        with pytest.raises(ValidationError, match="names a product"):
            Engagement(
                id="eng-x",
                **_base(playbook_ref),
                customer_alias="contoso",
                as_of=AS_OF,
                primary_trigger=EngagementTrigger.END_OF_SUPPORT,
                desired_outcomes=["Azure SQL Managed Instance for everything"],
                business_context="context",
                scope=EngagementScope(),
            )

    def test_renewal_trigger_requires_a_date(self, playbook_ref: PlaybookRef) -> None:
        with pytest.raises(ValidationError, match="renewal_date is unset"):
            Engagement(
                id="eng-x",
                **_base(playbook_ref),
                customer_alias="contoso",
                as_of=AS_OF,
                primary_trigger=EngagementTrigger.LICENSE_OR_EA_RENEWAL,
                desired_outcomes=["Reduce audit exposure before the renewal."],
                business_context="context",
                scope=EngagementScope(),
            )

    def test_unknown_field_is_an_error_not_a_silent_noop(self, playbook_ref: PlaybookRef) -> None:
        with pytest.raises(ValidationError):
            Engagement(
                id="eng-x",
                **_base(playbook_ref),
                customer_alias="contoso",
                as_of=AS_OF,
                primary_trigger=EngagementTrigger.END_OF_SUPPORT,
                desired_outcomes=["An outcome."],
                business_context="context",
                scope=EngagementScope(),
                renewl_date=AS_OF,  # type: ignore[call-arg]
            )


class TestEvidence:
    def test_evidence_cannot_be_a_recommendation(self) -> None:
        """Evidence is an input to reasoning. A recommendation is an output of it."""
        with pytest.raises(ValidationError, match="cannot be a recommendation"):
            EvidenceRecord(
                id="ev-1",
                engagement_id="eng-test",
                subject_type="workload",
                subject_id="wl-1",
                source=EvidenceSource.CSV_INVENTORY,
                source_ref="inventory.csv#row=2",
                collected_on=AS_OF,
                evidence_class=EvidenceClass.RECOMMENDATION,
            )


class TestWorkload:
    def test_support_status_cannot_be_derived_from_an_unknown_version(
        self, playbook_ref: PlaybookRef
    ) -> None:
        with pytest.raises(ValidationError, match="support_status"):
            Workload(
                id="wl-1",
                **_base(playbook_ref),
                name="Example",
                source_platform="sql-server",
                source_version=None,
                support_status=SupportStatus.END_OF_SUPPORT,
            )

    def test_observed_finding_must_cite_evidence(self) -> None:
        with pytest.raises(ValidationError, match="cites no evidence"):
            AssessmentFinding(
                id="f-1",
                category=FindingCategory.COMPATIBILITY,
                severity=Severity.HIGH,
                statement="Something was observed.",
                evidence_class=EvidenceClass.OBSERVED,
                evidence_refs=[],
            )

    def test_blocking_findings_prevent_recommendation_readiness(
        self, playbook_ref: PlaybookRef
    ) -> None:
        workload = Workload(
            id="wl-1",
            **_base(playbook_ref),
            name="Example",
            source_platform="sql-server",
            source_version="15.0",
            findings=[
                AssessmentFinding(
                    id="f-1",
                    category=FindingCategory.DEPENDENCY,
                    severity=Severity.BLOCKER,
                    statement="Consumers unknown.",
                    evidence_class=EvidenceClass.ASSUMPTION,
                    blocking=True,
                )
            ],
        )
        assert workload.is_recommendation_ready is False
        assert workload.highest_severity is Severity.BLOCKER


def _decision(playbook_ref: PlaybookRef, **overrides: object) -> TargetDecision:
    payload: dict[str, object] = {
        "id": "td-1",
        **_base(playbook_ref),
        "evidence_refs": ["ev-1"],
        "workload_id": "wl-1",
        "recommended_target": AzureTarget.SQL_MANAGED_INSTANCE,
        "disposition": Disposition.REPLATFORM,
        "rationale": "Instance-scoped features are in use.",
        "considered_options": [
            ConsideredOption(
                target=AzureTarget.SQL_MANAGED_INSTANCE,
                verdict=OptionVerdict.RECOMMENDED,
                score=82.0,
                rationale="Supports the observed features.",
            ),
            ConsideredOption(
                target=AzureTarget.SQL_DATABASE,
                verdict=OptionVerdict.REJECTED,
                score=41.0,
                rationale="Database scope does not offer the observed features.",
            ),
        ],
        "downtime_approach": DowntimeApproach(
            method="Log replay with a short application cutover window.",
            expected_class=DowntimeClass.SHORT_PLANNED,
            basis="No rehearsal has been run.",
            measured=False,
        ),
    }
    payload.update(overrides)
    return TargetDecision(**payload)  # type: ignore[arg-type]


class TestTargetDecision:
    def test_a_single_option_is_not_a_decision(self, playbook_ref: PlaybookRef) -> None:
        with pytest.raises(ValidationError, match="at least one alternative"):
            _decision(
                playbook_ref,
                considered_options=[
                    ConsideredOption(
                        target=AzureTarget.SQL_MANAGED_INSTANCE,
                        verdict=OptionVerdict.RECOMMENDED,
                        score=82.0,
                        rationale="Only option.",
                    ),
                    ConsideredOption(
                        target=AzureTarget.SQL_DATABASE,
                        verdict=OptionVerdict.VIABLE,
                        score=41.0,
                        rationale="Also fine, apparently.",
                    ),
                ],
            )

    def test_near_zero_downtime_requires_a_measurement(self, playbook_ref: PlaybookRef) -> None:
        """The strongest downtime claim available, and only with a rehearsal behind it."""
        with pytest.raises(ValidationError, match="requires measured evidence"):
            DowntimeApproach(
                method="Continuous replication.",
                expected_class=DowntimeClass.NEAR_ZERO_PLANNED,
                basis="It should be quick.",
                measured=False,
            )

    def test_zero_downtime_wording_is_refused(self) -> None:
        with pytest.raises(ValidationError, match="not permitted"):
            DowntimeApproach(
                method="Cutover with zero downtime.",
                expected_class=DowntimeClass.SHORT_PLANNED,
                basis="Vendor said so.",
            )

    def test_approved_status_requires_an_approval_artifact(self, playbook_ref: PlaybookRef) -> None:
        with pytest.raises(ValidationError, match="cannot approve itself"):
            _decision(playbook_ref, status=ArtifactStatus.APPROVED)

    def test_heterogeneous_disposition_forces_conversion_flag(
        self, playbook_ref: PlaybookRef
    ) -> None:
        with pytest.raises(ValidationError, match="conversion_required must be true"):
            _decision(
                playbook_ref,
                disposition=Disposition.REFACTOR,
                conversion_required=False,
            )


class TestApproval:
    def _approval(self, **overrides: object) -> Approval:
        payload: dict[str, object] = {
            "id": "ap-1",
            "engagement_id": "eng-test",
            "approved_artifact_id": "td-1",
            "approved_artifact_type": "target-decision",
            "artifact_hash": "sha256:" + "0" * 64,
            "role": ApprovalRole.ARCHITECT,
            "approver_principal": "architect-a",
            "artifact_author": "agent:target-architect",
            "decision": ApprovalDecision.APPROVED,
            "approved_at": TIMESTAMP,
            "scope": "One workload.",
        }
        payload.update(overrides)
        return Approval(**payload)  # type: ignore[arg-type]

    def test_author_cannot_approve_own_artifact(self) -> None:
        with pytest.raises(ValidationError, match="cannot approve it"):
            self._approval(approver_principal="agent:target-architect")

    def test_agent_cannot_approve_agent_authored_work(self) -> None:
        with pytest.raises(ValidationError, match="agent cannot approve"):
            self._approval(approver_principal="agent:governance-reviewer")

    def test_conditional_approval_needs_conditions(self) -> None:
        with pytest.raises(ValidationError, match="lists no conditions"):
            self._approval(decision=ApprovalDecision.APPROVED_WITH_CONDITIONS)


class TestPolicyException:
    def _exception(self, **overrides: object) -> PolicyException:
        payload: dict[str, object] = {
            "id": "EX-1",
            "policy_id": "IAM-001",
            "scope": "One legacy tool.",
            "justification": "The vendor has no supported alternative in this window.",
            "owner_role": "database-owner",
            "approver_role": "security-owner",
            "approver_principal": "security-owner-a",
            "compensating_controls": ["Rotated every 30 days"],
            "granted_on": date(2026, 1, 15),
            "expires_on": date(2026, 4, 15),
            "review_on": date(2026, 3, 15),
        }
        payload.update(overrides)
        return PolicyException(**payload)  # type: ignore[arg-type]

    def test_requester_cannot_be_approver(self) -> None:
        with pytest.raises(ValidationError, match="cannot also be the approving role"):
            self._exception(approver_role="database-owner")

    def test_expiry_must_follow_grant(self) -> None:
        with pytest.raises(ValidationError, match="expires on or before"):
            self._exception(expires_on=date(2026, 1, 1))

    def test_expiry_is_detected(self) -> None:
        exception = self._exception()
        assert exception.is_expired(date(2026, 4, 16)) is True
        assert exception.is_expired(date(2026, 4, 14)) is False


class TestRisk:
    def _risk(self, **overrides: object) -> dict[str, object]:
        payload: dict[str, object] = {
            "id": "risk-1",
            "engagement_id": "eng-test",
            "created_at": TIMESTAMP,
            "updated_at": TIMESTAMP,
            "author": "agent:test",
            "title": "Unknown consumers",
            "description": "Nobody can enumerate the consumers.",
            "category": RiskCategory.APPLICATION,
            "likelihood": Likelihood.HIGH,
            "impact": Likelihood.HIGH,
            "owner_role": "application-owner",
            "mitigation": "Complete dependency mapping.",
            "contingency": "Defer the workload.",
        }
        payload.update(overrides)
        return payload

    def test_severity_is_derived(self, playbook_ref: PlaybookRef) -> None:
        risk = Risk(**self._risk(), playbook=playbook_ref)  # type: ignore[arg-type]
        assert risk.score == 9
        assert risk.severity is Severity.BLOCKER

    def test_high_risk_needs_a_contingency(self, playbook_ref: PlaybookRef) -> None:
        with pytest.raises(ValidationError, match="needs a contingency"):
            Risk(**self._risk(contingency=None), playbook=playbook_ref)  # type: ignore[arg-type]

    def test_acceptance_must_be_attributed(self, playbook_ref: PlaybookRef) -> None:
        with pytest.raises(ValidationError, match="who accepted it"):
            Risk(
                **self._risk(risk_status=RiskStatus.ACCEPTED),  # type: ignore[arg-type]
                playbook=playbook_ref,
            )


class TestPlanning:
    def test_mutating_task_needs_approval_and_rollback(self) -> None:
        with pytest.raises(ValidationError, match="does not require approval"):
            PlanTask(
                id="t-1",
                title="Deploy",
                kind=TaskKind.CUTOVER,
                description="Deploy the target.",
                owner_role="architect",
                changes_environment=True,
                approval_required=False,
            )

        with pytest.raises(ValidationError, match="no rollback path"):
            PlanTask(
                id="t-2",
                title="Deploy",
                kind=TaskKind.CUTOVER,
                description="Deploy the target.",
                owner_role="architect",
                changes_environment=True,
                approval_required=True,
            )

    def test_waves_cannot_share_a_workload(self, playbook_ref: PlaybookRef) -> None:
        def wave(identifier: str, sequence: int, workloads: list[str]) -> MigrationWave:
            return MigrationWave(
                id=identifier,
                **_base(playbook_ref, workload_ids=workloads),
                name=identifier,
                sequence=sequence,
                objective="Move things.",
                owner_roles=["delivery-lead"],
                exit_criteria=[
                    Criterion(
                        id=f"{identifier}-exit",
                        statement="Validation passes.",
                        verification_method="Validation report",
                        owner_role="delivery-lead",
                    )
                ],
            )

        with pytest.raises(ValidationError, match="more than one wave"):
            WavePlan(
                engagement_id="eng-test",
                waves=[wave("w1", 1, ["wl-a"]), wave("w2", 2, ["wl-a"])],
            )

    def test_wave_cannot_depend_on_a_later_wave(self, playbook_ref: PlaybookRef) -> None:
        def wave(identifier: str, sequence: int, depends: list[str]) -> MigrationWave:
            return MigrationWave(
                id=identifier,
                **_base(playbook_ref, workload_ids=[f"wl-{sequence}"]),
                name=identifier,
                sequence=sequence,
                objective="Move things.",
                owner_roles=["delivery-lead"],
                depends_on_wave_ids=depends,
                exit_criteria=[
                    Criterion(
                        id=f"{identifier}-exit",
                        statement="Validation passes.",
                        verification_method="Validation report",
                        owner_role="delivery-lead",
                    )
                ],
            )

        with pytest.raises(ValidationError, match="which runs later"):
            WavePlan(
                engagement_id="eng-test",
                waves=[wave("w1", 1, ["w2"]), wave("w2", 2, [])],
            )

    def test_pilot_must_be_small_and_first(self, playbook_ref: PlaybookRef) -> None:
        with pytest.raises(ValidationError, match="must be sequence 1"):
            MigrationWave(
                id="w2",
                **_base(playbook_ref, workload_ids=["wl-a"]),
                name="pilot",
                sequence=2,
                objective="Pilot.",
                is_pilot=True,
                owner_roles=["delivery-lead"],
                exit_criteria=[
                    Criterion(
                        id="ec",
                        statement="Validation passes.",
                        verification_method="Report",
                        owner_role="delivery-lead",
                    )
                ],
            )


def _check(identifier: str, **overrides: object) -> ValidationCheck:
    payload: dict[str, object] = {
        "id": identifier,
        "category": CheckCategory.PERFORMANCE,
        "name": "Performance within tolerance",
        "method": "Replay the baseline workload.",
        "tolerance": "Within 10%",
    }
    payload.update(overrides)
    return ValidationCheck(**payload)  # type: ignore[arg-type]


def _report(playbook_ref: PlaybookRef, **overrides: object) -> ValidationReport:
    payload: dict[str, object] = {
        "id": "vr-1",
        **_base(playbook_ref),
        "wave_id": "wave-1",
        "migration_plan_id": "plan-wave-1",
        "executed_on": "2026-03-02",
        "checks": [_check("vc-1", result=CheckResult.PASS, observed="within 3%")],
        "outcome": Outcome.GO,
        "business_acceptance": BusinessAcceptance(
            business_owner_accepted=True, application_owner_accepted=True
        ),
    }
    payload.update(overrides)
    return ValidationReport(**payload)  # type: ignore[arg-type]


class TestValidationReport:
    def test_blocking_failure_forces_no_go(self, playbook_ref: PlaybookRef) -> None:
        with pytest.raises(ValidationError, match="force a no-go"):
            _report(
                playbook_ref,
                checks=[_check("vc-1", result=CheckResult.FAIL, observed="47% regression")],
            )

    def test_un_run_blocking_check_forbids_go(self, playbook_ref: PlaybookRef) -> None:
        with pytest.raises(ValidationError, match="blocking checks have not run"):
            _report(playbook_ref, checks=[_check("vc-1", result=CheckResult.NOT_RUN)])

    def test_go_requires_business_acceptance(self, playbook_ref: PlaybookRef) -> None:
        with pytest.raises(ValidationError, match="business and application owner"):
            _report(playbook_ref, business_acceptance=BusinessAcceptance())

    def test_generated_tests_alone_cannot_justify_go(self, playbook_ref: PlaybookRef) -> None:
        with pytest.raises(ValidationError, match="rests entirely on generated tests"):
            _report(
                playbook_ref,
                checks=[
                    _check(
                        "vc-1",
                        result=CheckResult.PASS,
                        observed="412 of 412 matched",
                        generated_test=True,
                    )
                ],
            )

    def test_no_go_must_produce_corrective_issues(self, playbook_ref: PlaybookRef) -> None:
        with pytest.raises(ValidationError, match="generates no corrective issues"):
            _report(
                playbook_ref,
                checks=[_check("vc-1", result=CheckResult.FAIL, observed="failed")],
                outcome=Outcome.NO_GO,
                business_acceptance=BusinessAcceptance(),
            )

    def test_completed_check_must_record_what_was_seen(self) -> None:
        with pytest.raises(ValidationError, match="records no observed value"):
            _check("vc-1", result=CheckResult.PASS)

    def test_rollback_must_be_explained(self, playbook_ref: PlaybookRef) -> None:
        with pytest.raises(ValidationError, match="without recording why"):
            _report(
                playbook_ref,
                checks=[_check("vc-1", result=CheckResult.FAIL, observed="failed")],
                outcome=Outcome.NO_GO,
                business_acceptance=BusinessAcceptance(),
                rollback_triggered=True,
                corrective_issue_ids=["issue-1"],
            )
