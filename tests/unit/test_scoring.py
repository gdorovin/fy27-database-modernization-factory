"""Scoring: assessment rules, target comparison, disposition, and wave planning.

These tests pin the behaviour that makes the factory trustworthy rather than merely
productive: that it refuses to recommend on thin evidence, and that it shows its working.
"""

from __future__ import annotations

from datetime import date

import pytest

from dbmodernize.models.base import AzureTarget, Disposition, PlaybookRef, SourcePlatform
from dbmodernize.models.decision import OptionVerdict
from dbmodernize.models.engagement import Engagement
from dbmodernize.models.workload import (
    AssessmentFinding,
    Criticality,
    EnvironmentKind,
    EvidenceClass,
    FindingCategory,
    Severity,
    SupportStatus,
    Workload,
    WorkloadSizing,
)
from dbmodernize.policies.models import Playbook
from dbmodernize.scoring.classification import classify, requires_application_change
from dbmodernize.scoring.reference import (
    HYPERSCALE_SIZE_THRESHOLD_GB,
    VERIFIED_ON,
    open_source_support,
    sql_server_support,
)
from dbmodernize.scoring.targets import evaluate, recommend
from tests.conftest import TIMESTAMP


def _workload(playbook_ref: PlaybookRef, **overrides: object) -> Workload:
    payload: dict[str, object] = {
        "id": "wl-test",
        "engagement_id": "eng-test",
        "created_at": TIMESTAMP,
        "updated_at": TIMESTAMP,
        "author": "agent:estate-assessor",
        "playbook": playbook_ref,
        "evidence_refs": ["ev-test"],
        "name": "Test workload",
        "source_platform": SourcePlatform.SQL_SERVER,
        "source_version": "15.0",
        "environment": EnvironmentKind.PRODUCTION,
        "criticality": Criticality.MEDIUM,
        "dependency_discovery_complete": True,
        "sizing": WorkloadSizing(data_size_gb=200.0, measured=True),
    }
    payload.update(overrides)
    return Workload(**payload)  # type: ignore[arg-type]


class TestReferenceData:
    def test_reference_tables_carry_a_verification_date(self) -> None:
        """Everything in the reference module perishes; readers need to know how stale."""
        assert isinstance(VERIFIED_ON, date)

    def test_unknown_version_never_guesses_support_status(self) -> None:
        assert sql_server_support(None) is SupportStatus.UNKNOWN
        assert sql_server_support("not-a-version") is SupportStatus.UNKNOWN
        assert open_source_support(SourcePlatform.POSTGRESQL, None) is SupportStatus.UNKNOWN

    def test_known_versions_map_to_a_posture(self) -> None:
        assert sql_server_support("13.0") is SupportStatus.END_OF_SUPPORT
        assert sql_server_support("15.0") is SupportStatus.SUPPORTED
        assert (
            open_source_support(SourcePlatform.POSTGRESQL, "11.9") is SupportStatus.END_OF_SUPPORT
        )


class TestTargetEvaluation:
    def test_instance_scoped_features_block_database_scope(self, playbook_ref: PlaybookRef) -> None:
        """Blocked, not scored down. The feature is unavailable, not merely inconvenient."""
        workload = _workload(
            playbook_ref, instance_features=["sql-agent", "cross-database-queries"]
        )
        result = evaluate(workload, AzureTarget.SQL_DATABASE)
        assert result.blockers
        assert "cross-database-queries" in result.blockers[0]

    def test_os_level_dependency_blocks_every_managed_target(
        self, playbook_ref: PlaybookRef
    ) -> None:
        workload = _workload(playbook_ref, instance_features=["os-level-access"])
        for target in (
            AzureTarget.SQL_DATABASE,
            AzureTarget.SQL_DATABASE_HYPERSCALE,
            AzureTarget.SQL_MANAGED_INSTANCE,
        ):
            assert evaluate(workload, target).blockers, f"{target} should be blocked"
        assert not evaluate(workload, AzureTarget.SQL_ON_AZURE_VM).blockers

    def test_hyperscale_is_penalised_when_scale_does_not_justify_it(
        self, playbook_ref: PlaybookRef
    ) -> None:
        """Recommending more capability than the evidence supports is its own failure."""
        small = _workload(playbook_ref, sizing=WorkloadSizing(data_size_gb=50.0, measured=True))
        assert (
            evaluate(small, AzureTarget.SQL_DATABASE).score
            > evaluate(small, AzureTarget.SQL_DATABASE_HYPERSCALE).score
        )

    def test_hyperscale_wins_when_scale_justifies_it(self, playbook_ref: PlaybookRef) -> None:
        large = _workload(
            playbook_ref,
            sizing=WorkloadSizing(
                data_size_gb=HYPERSCALE_SIZE_THRESHOLD_GB * 2,
                annual_growth_percent=60.0,
                measured=True,
            ),
        )
        assert (
            evaluate(large, AzureTarget.SQL_DATABASE_HYPERSCALE).score
            > evaluate(large, AzureTarget.SQL_DATABASE).score
        )

    def test_infrastructure_is_penalised_without_a_reason_to_choose_it(
        self, playbook_ref: PlaybookRef
    ) -> None:
        workload = _workload(playbook_ref)
        result = evaluate(workload, AzureTarget.SQL_ON_AZURE_VM)
        assert any("patching" in reason for reason in result.reasons)

    def test_heterogeneous_target_is_blocked_without_conversion_evidence(
        self, playbook_ref: PlaybookRef
    ) -> None:
        oracle = _workload(
            playbook_ref, source_platform=SourcePlatform.ORACLE, source_version="19.3"
        )
        result = evaluate(oracle, AzureTarget.POSTGRESQL_FLEXIBLE)
        assert result.blockers
        assert "never assumed" in result.blockers[0]

    def test_conversion_evidence_does_not_transfer_between_targets(
        self, playbook_ref: PlaybookRef
    ) -> None:
        """Assessing against one destination says nothing about a different one."""
        oracle = _workload(
            playbook_ref,
            source_platform=SourcePlatform.ORACLE,
            source_version="19.3",
            assessed_targets=["azure-database-for-postgresql-flexible-server"],
            findings=[
                AssessmentFinding(
                    id="wl-test-r-conversion-effort",
                    category=FindingCategory.COMPATIBILITY,
                    severity=Severity.HIGH,
                    statement="Conversion required.",
                    evidence_class=EvidenceClass.OBSERVED,
                    evidence_refs=["ev-test"],
                )
            ],
        )
        assert not evaluate(oracle, AzureTarget.POSTGRESQL_FLEXIBLE).blockers
        assert evaluate(oracle, AzureTarget.SQL_MANAGED_INSTANCE).blockers


class TestRecommendation:
    def test_blocked_workload_gets_no_destination(
        self, playbook_ref: PlaybookRef, engagement: Engagement, default_playbook: Playbook
    ) -> None:
        """A workload with unknown consumers may be governed, but it may not be moved."""
        workload = _workload(
            playbook_ref,
            dependency_discovery_complete=False,
            findings=[
                AssessmentFinding(
                    id="wl-test-r-dependencies-unknown",
                    category=FindingCategory.DEPENDENCY,
                    severity=Severity.BLOCKER,
                    statement="Consumers unknown.",
                    evidence_class=EvidenceClass.OBSERVED,
                    evidence_refs=["ev-test"],
                    blocking=True,
                )
            ],
        )
        decision = recommend(workload, engagement, default_playbook, playbook_ref)
        assert decision is not None
        assert decision.recommended_target is AzureTarget.ARC_ENABLED_SQL
        assert decision.disposition is Disposition.RETAIN
        assert "interim posture" in decision.rationale

        moving = [
            option
            for option in decision.considered_options
            if option.target in {AzureTarget.SQL_DATABASE, AzureTarget.SQL_MANAGED_INSTANCE}
        ]
        assert moving and all(o.verdict is OptionVerdict.BLOCKED for o in moving)

    def test_recommendation_shows_its_working(
        self, playbook_ref: PlaybookRef, engagement: Engagement, default_playbook: Playbook
    ) -> None:
        workload = _workload(playbook_ref, instance_features=["sql-agent"])
        decision = recommend(workload, engagement, default_playbook, playbook_ref)

        assert decision is not None
        assert decision.recommended_target is AzureTarget.SQL_MANAGED_INSTANCE
        assert len(decision.considered_options) >= 2
        assert decision.rejected_alternatives
        assert decision.evidence_refs == ["ev-test"]

    def test_downtime_stays_provisional_without_a_budget(
        self, playbook_ref: PlaybookRef, engagement: Engagement, default_playbook: Playbook
    ) -> None:
        workload = _workload(playbook_ref)
        decision = recommend(workload, engagement, default_playbook, playbook_ref)
        assert decision is not None
        assert decision.downtime_approach.measured is False
        assert decision.downtime_approach.expected_class.value in {
            "unknown",
            "short-planned",
        }

    def test_scoring_is_deterministic(
        self, playbook_ref: PlaybookRef, engagement: Engagement, default_playbook: Playbook
    ) -> None:
        workload = _workload(playbook_ref, instance_features=["sql-agent"])
        first = recommend(workload, engagement, default_playbook, playbook_ref)
        second = recommend(workload, engagement, default_playbook, playbook_ref)
        assert first is not None and second is not None
        assert first.model_dump(mode="json") == second.model_dump(mode="json")


class TestClassification:
    @pytest.mark.parametrize(
        ("target", "expected"),
        [
            (AzureTarget.ARC_ENABLED_SQL, Disposition.RETAIN),
            (AzureTarget.RETAIN, Disposition.RETAIN),
            (AzureTarget.RETIRE, Disposition.RETIRE),
            (AzureTarget.REPLACE_SAAS, Disposition.REPLACE),
            (AzureTarget.SQL_ON_AZURE_VM, Disposition.REHOST),
            (AzureTarget.SQL_MANAGED_INSTANCE, Disposition.REPLATFORM),
        ],
    )
    def test_disposition_follows_the_target(
        self, playbook_ref: PlaybookRef, target: AzureTarget, expected: Disposition
    ) -> None:
        assert classify(_workload(playbook_ref), target) is expected

    def test_arc_is_retain_not_modernization(self, playbook_ref: PlaybookRef) -> None:
        """Counting a governed-in-place workload as modernized overstates progress."""
        assert classify(_workload(playbook_ref), AzureTarget.ARC_ENABLED_SQL) is Disposition.RETAIN

    def test_database_scope_implies_application_change_when_features_are_used(
        self, playbook_ref: PlaybookRef
    ) -> None:
        workload = _workload(playbook_ref, instance_features=["sql-agent"])
        assert requires_application_change(workload, AzureTarget.SQL_DATABASE) is True
        assert requires_application_change(workload, AzureTarget.SQL_MANAGED_INSTANCE) is False
