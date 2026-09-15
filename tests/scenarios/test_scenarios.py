"""Scenarios run offline and match their committed expectations.

Two layers, deliberately. Snapshot comparison catches drift; acceptance criteria catch a
snapshot that was regenerated to make a failure disappear. Either alone is defeatable.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from dbmodernize.validators.scenario import (
    ACCEPTANCE_KINDS,
    load_spec,
    run_scenario,
    validate_scenario,
    validate_scenarios_tree,
)

EXPECTED_SCENARIOS = (
    "01-sql2016-to-managed-instance",
    "02-sql-to-azure-sql-database",
    "03-postgresql-to-flexible-server",
    "04-oracle-heterogeneous-modernization",
    "05-arc-bridge-to-azure-sql",
    "06-app-database-ai-modernization",
    "07-failed-validation-and-rollback",
)


def test_all_seven_scenarios_are_present(scenario_dirs: list[Path]) -> None:
    names = [directory.name for directory in scenario_dirs]
    assert names == list(EXPECTED_SCENARIOS)


def test_all_scenarios_pass(repo_root: Path) -> None:
    findings = validate_scenarios_tree(repo_root, repo_root / "scenarios")
    assert findings.ok, "\n".join(f.render() for f in findings.errors)


@pytest.mark.parametrize("name", EXPECTED_SCENARIOS)
def test_scenario_passes_individually(repo_root: Path, name: str) -> None:
    findings = validate_scenario(repo_root, repo_root / "scenarios" / name)
    assert findings.ok, "\n".join(f.render() for f in findings.errors)


@pytest.mark.parametrize("name", EXPECTED_SCENARIOS)
def test_scenario_declares_acceptance_criteria(repo_root: Path, name: str) -> None:
    """A scenario with only snapshots can be silenced by regenerating them."""
    spec = load_spec(repo_root, repo_root / "scenarios" / name)
    assert len(spec.acceptance) >= 5, f"{name} declares only {len(spec.acceptance)} criteria"
    for criterion in spec.acceptance:
        assert criterion["kind"] in ACCEPTANCE_KINDS


@pytest.mark.parametrize("name", EXPECTED_SCENARIOS)
def test_scenario_has_a_readme(repo_root: Path, name: str) -> None:
    readme = repo_root / "scenarios" / name / "README.md"
    assert readme.is_file(), f"{name} has no README"
    assert len(readme.read_text(encoding="utf-8")) > 500


@pytest.mark.parametrize("name", EXPECTED_SCENARIOS)
def test_scenario_output_is_reproducible(repo_root: Path, name: str) -> None:
    """Identical inputs must produce byte-identical outputs on any machine."""
    first, _ = run_scenario(repo_root, repo_root / "scenarios" / name)
    second, _ = run_scenario(repo_root, repo_root / "scenarios" / name)

    assert first.documents == second.documents
    assert first.structured == second.structured


@pytest.mark.parametrize("name", EXPECTED_SCENARIOS)
def test_scenario_inputs_are_synthetic(repo_root: Path, name: str) -> None:
    """No real customer name, host, or identifier may appear in a committed fixture."""
    from dbmodernize.utils.redaction import contains_secret_like

    for path in sorted((repo_root / "scenarios" / name / "input").rglob("*")):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        assert not contains_secret_like(text), f"{path} matches a secret pattern"


class TestScenarioBehaviour:
    """Cross-scenario properties that no single scenario would catch."""

    def test_no_scenario_recommends_a_target_for_a_blocked_workload(
        self, repo_root: Path, scenario_dirs: list[Path]
    ) -> None:
        moving = {
            "azure-sql-database",
            "azure-sql-database-hyperscale",
            "azure-sql-managed-instance",
            "sql-server-on-azure-vm",
            "azure-database-for-postgresql-flexible-server",
            "azure-database-for-mysql-flexible-server",
        }
        for directory in scenario_dirs:
            result, _ = run_scenario(repo_root, directory)
            for workload in result.inventory.workloads:
                if not workload.blocking_findings:
                    continue
                decision = result.decisions.get(workload.id)
                if decision is None:
                    continue
                assert decision.recommended_target.value not in moving, (
                    f"{directory.name}: {workload.id} is blocked but was given a "
                    f"destination ({decision.recommended_target.value})"
                )

    def test_no_generated_document_claims_zero_downtime(
        self, repo_root: Path, scenario_dirs: list[Path]
    ) -> None:
        for directory in scenario_dirs:
            result, _ = run_scenario(repo_root, directory)
            for name, text in result.documents.items():
                lowered = text.lower()
                assert "zero downtime" not in lowered, f"{directory.name}/{name}"
                assert "zero-downtime" not in lowered, f"{directory.name}/{name}"

    def test_every_recommendation_cites_evidence(
        self, repo_root: Path, scenario_dirs: list[Path]
    ) -> None:
        for directory in scenario_dirs:
            result, _ = run_scenario(repo_root, directory)
            for decision in result.decisions.decisions:
                assert decision.evidence_refs, (
                    f"{directory.name}: {decision.id} recommends a target with no evidence"
                )

    def test_every_decision_shows_a_rejected_or_blocked_alternative(
        self, repo_root: Path, scenario_dirs: list[Path]
    ) -> None:
        for directory in scenario_dirs:
            result, _ = run_scenario(repo_root, directory)
            for decision in result.decisions.decisions:
                assert decision.rejected_alternatives, (
                    f"{directory.name}: {decision.id} shows no alternative"
                )

    def test_every_plan_gates_its_environment_changing_tasks(
        self, repo_root: Path, scenario_dirs: list[Path]
    ) -> None:
        for directory in scenario_dirs:
            result, _ = run_scenario(repo_root, directory)
            for plan in result.plans:
                for phase in plan.phases:
                    for task in phase.tasks:
                        if task.changes_environment:
                            assert task.approval_required, f"{plan.id}/{task.id}"
                            assert task.rollback_note, f"{plan.id}/{task.id}"

    def test_every_cutover_requires_all_five_owner_roles(
        self, repo_root: Path, scenario_dirs: list[Path]
    ) -> None:
        from dbmodernize.models.base import CUTOVER_REQUIRED_ROLES

        for directory in scenario_dirs:
            result, _ = run_scenario(repo_root, directory)
            for plan in result.plans:
                missing = CUTOVER_REQUIRED_ROLES - set(plan.cutover.required_approval_roles)
                assert not missing, f"{plan.id} is missing {sorted(r.value for r in missing)}"

    def test_retained_workloads_are_never_scheduled_into_a_wave(
        self, repo_root: Path, scenario_dirs: list[Path]
    ) -> None:
        """Counting a non-moving workload as scheduled overstates progress."""
        for directory in scenario_dirs:
            result, _ = run_scenario(repo_root, directory)
            scheduled = {
                workload_id for wave in result.waves.waves for workload_id in wave.workload_ids
            }
            for decision in result.decisions.decisions:
                if decision.disposition.value in {"retain", "retire", "replace"}:
                    assert decision.workload_id not in scheduled, (
                        f"{directory.name}: {decision.workload_id} is "
                        f"{decision.disposition.value} but appears in a wave"
                    )

    def test_pilot_waves_are_small(self, repo_root: Path, scenario_dirs: list[Path]) -> None:
        for directory in scenario_dirs:
            result, _ = run_scenario(repo_root, directory)
            for wave in result.waves.waves:
                if wave.is_pilot:
                    assert wave.sequence == 1
                    assert len(wave.workload_ids) <= 2, (
                        f"{directory.name}: pilot holds {len(wave.workload_ids)} workloads"
                    )


class TestRollbackScenario:
    """Scenario 07 exists to prove the repository reports a failure as a failure."""

    def _result(self, repo_root: Path):  # type: ignore[no-untyped-def]
        result, _ = run_scenario(
            repo_root, repo_root / "scenarios" / "07-failed-validation-and-rollback"
        )
        return result

    def test_outcome_is_no_go(self, repo_root: Path) -> None:
        report = self._result(repo_root).validation_report
        assert report is not None
        assert report.outcome.value == "no-go"

    def test_rollback_was_triggered_and_explained(self, repo_root: Path) -> None:
        report = self._result(repo_root).validation_report
        assert report is not None
        assert report.rollback_triggered is True
        assert report.rollback_reason

    def test_corrective_issues_were_created(self, repo_root: Path) -> None:
        report = self._result(repo_root).validation_report
        assert report is not None
        assert len(report.corrective_issue_ids) >= 3

    def test_an_unfinished_check_is_not_a_pass(self, repo_root: Path) -> None:
        report = self._result(repo_root).validation_report
        assert report is not None
        assert report.blocking_not_run, "the un-run reconciliation must be visible"

    def test_generated_tests_did_not_carry_the_verdict(self, repo_root: Path) -> None:
        report = self._result(repo_root).validation_report
        assert report is not None
        generated = [check for check in report.checks if check.generated_test]
        assert generated, "the scenario needs a passing generated suite to be meaningful"
        assert all(check.blocking is False for check in generated)

    def test_the_report_contains_no_success_language(self, repo_root: Path) -> None:
        text = self._result(repo_root).documents["validation-report.md"].lower()
        for phrase in ("successfully", "migration succeeded", "went well"):
            assert phrase not in text, f"report contains {phrase!r}"
