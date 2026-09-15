"""End-to-end pipeline and CLI behaviour. Offline throughout."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from typer.testing import CliRunner

from dbmodernize.cli import app, command_names
from dbmodernize.errors import ExitCode
from dbmodernize.pipeline import run_pipeline

SCENARIO = "01-sql2016-to-managed-instance"


@pytest.fixture(scope="module")
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture(scope="module")
def scenario_input(request: pytest.FixtureRequest) -> Path:
    root = Path(__file__).resolve().parents[2]
    return root / "scenarios" / SCENARIO / "input"


class TestPipeline:
    def test_full_chain_produces_every_artifact(self, repo_root: Path) -> None:
        result = run_pipeline(
            repo_root,
            repo_root / "scenarios" / SCENARIO / "input" / "engagement.yaml",
            repo_root / "scenarios" / SCENARIO / "input",
            repo_root / "playbooks" / "default",
        )

        for name in (
            "evidence.json",
            "workloads.json",
            "risks.json",
            "target-decisions.json",
            "waves.json",
            "issues.yaml",
        ):
            assert name in result.structured

        for name in (
            "assessment-summary.md",
            "target-decision.md",
            "migration-waves.md",
            "executive-brief.md",
        ):
            assert name in result.documents

        assert any(name.startswith("migration-plan-") for name in result.documents)
        assert any(name.startswith("rollback-plan-") for name in result.documents)

    def test_a_plan_is_rendered_for_every_wave(self, repo_root: Path) -> None:
        """Rendering only the first wave would hide the rest of the programme."""
        result = run_pipeline(
            repo_root,
            repo_root / "scenarios" / SCENARIO / "input" / "engagement.yaml",
            repo_root / "scenarios" / SCENARIO / "input",
            repo_root / "playbooks" / "default",
        )
        for wave in result.waves.waves:
            assert f"migration-plan-{wave.sequence}.md" in result.documents
            assert f"cutover-plan-{wave.sequence}.md" in result.documents
            assert f"rollback-plan-{wave.sequence}.md" in result.documents
            assert f"validation-plan-{wave.sequence}.md" in result.documents

    def test_artifacts_record_the_playbook_version(self, repo_root: Path) -> None:
        """Without the pin, nobody can reconstruct which rules produced a decision."""
        result = run_pipeline(
            repo_root,
            repo_root / "scenarios" / SCENARIO / "input" / "engagement.yaml",
            repo_root / "scenarios" / SCENARIO / "input",
            repo_root / "playbooks" / "default",
        )
        for decision in result.decisions.decisions:
            assert decision.playbook.version == result.playbook.version
            assert decision.playbook.policy_ids

    def test_traceability_chain_holds(self, repo_root: Path) -> None:
        """Evidence ids referenced downstream must exist upstream."""
        result = run_pipeline(
            repo_root,
            repo_root / "scenarios" / SCENARIO / "input" / "engagement.yaml",
            repo_root / "scenarios" / SCENARIO / "input",
            repo_root / "playbooks" / "default",
        )
        known = {record.id for record in result.bundle.records}

        for workload in result.inventory.workloads:
            assert set(workload.evidence_refs) <= known
        for decision in result.decisions.decisions:
            assert set(decision.evidence_refs) <= known
        for risk in result.risks.risks:
            assert set(risk.evidence_refs) <= known

    def test_every_issue_traces_back_to_a_workload_or_wave(self, repo_root: Path) -> None:
        result = run_pipeline(
            repo_root,
            repo_root / "scenarios" / SCENARIO / "input" / "engagement.yaml",
            repo_root / "scenarios" / SCENARIO / "input",
            repo_root / "playbooks" / "default",
        )
        known_workloads = {workload.id for workload in result.inventory.workloads}
        for issue in result.issues.issues:
            assert set(issue.workload_ids) <= known_workloads
            assert issue.playbook.version == result.playbook.version


class TestCliContract:
    def test_help_lists_every_command(self, runner: CliRunner) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        for name in command_names():
            assert name in result.output

    def test_version_prints_the_package_version(self, runner: CliRunner) -> None:
        from dbmodernize import __version__

        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_validate_repo_succeeds(self, runner: CliRunner, repo_root: Path) -> None:
        result = runner.invoke(app, ["validate-repo", "--repo", str(repo_root)])
        assert result.exit_code == int(ExitCode.OK), result.output

    def test_validate_repo_json_is_machine_readable(
        self, runner: CliRunner, repo_root: Path
    ) -> None:
        result = runner.invoke(app, ["validate-repo", "--repo", str(repo_root), "--json"])
        payload = json.loads(result.output)
        assert payload["ok"] is True
        assert payload["errors"] == 0

    def test_validation_failure_uses_the_contractual_exit_code(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        result = runner.invoke(app, ["validate-repo", "--repo", str(tmp_path)])
        assert result.exit_code == int(ExitCode.VALIDATION_FAILED)

    def test_live_issue_creation_is_refused(
        self, runner: CliRunner, repo_root: Path, tmp_path: Path
    ) -> None:
        """The refusal is the feature. A dry run must not be able to surprise a repository."""
        from dbmodernize.errors import SafetyRefusalError

        result = runner.invoke(
            app,
            [
                "generate-issues",
                "--engagement",
                str(repo_root / "scenarios" / SCENARIO / "input" / "engagement.yaml"),
                "--input",
                str(repo_root / "scenarios" / SCENARIO / "input"),
                "--out",
                str(tmp_path / "out"),
                "--create",
            ],
        )
        assert isinstance(result.exception, SafetyRefusalError)
        assert result.exception.exit_code == ExitCode.SAFETY_REFUSAL

    def test_dry_run_writes_nothing(
        self, runner: CliRunner, repo_root: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "out"
        result = runner.invoke(
            app,
            [
                "render-plan",
                "--engagement",
                str(repo_root / "scenarios" / SCENARIO / "input" / "engagement.yaml"),
                "--input",
                str(repo_root / "scenarios" / SCENARIO / "input"),
                "--out",
                str(out),
                "--dry-run",
            ],
        )
        assert result.exit_code == 0, result.output
        assert "Would write" in result.output
        assert not out.exists()

    def test_existing_output_is_not_overwritten_without_force(
        self, runner: CliRunner, repo_root: Path, tmp_path: Path
    ) -> None:
        out = tmp_path / "out"
        arguments = [
            "render-plan",
            "--engagement",
            str(repo_root / "scenarios" / SCENARIO / "input" / "engagement.yaml"),
            "--input",
            str(repo_root / "scenarios" / SCENARIO / "input"),
            "--out",
            str(out),
        ]
        first = runner.invoke(app, arguments)
        assert first.exit_code == 0, first.output

        second = runner.invoke(app, arguments)
        assert second.exception is not None
        assert getattr(second.exception, "exit_code", None) == ExitCode.OUTPUT_EXISTS

        third = runner.invoke(app, [*arguments, "--force"])
        assert third.exit_code == 0, third.output

    def test_render_report_exits_non_zero_on_a_no_go(
        self, runner: CliRunner, repo_root: Path, tmp_path: Path
    ) -> None:
        """A pipeline must not be able to walk past a no-go by accident."""
        scenario = repo_root / "scenarios" / "07-failed-validation-and-rollback"
        result = runner.invoke(
            app,
            [
                "render-report",
                "--engagement",
                str(scenario / "input" / "engagement.yaml"),
                "--input",
                str(scenario / "input"),
                "--report",
                str(scenario / "input" / "validation-report.json"),
                "--out",
                str(tmp_path / "out"),
            ],
        )
        assert result.exit_code == int(ExitCode.VALIDATION_FAILED)
        assert "no-go" in result.output

    def test_init_scaffolds_an_engagement(self, runner: CliRunner, tmp_path: Path) -> None:
        result = runner.invoke(
            app, ["init", "--engagement-id", "eng-example", "--out", str(tmp_path)]
        )
        assert result.exit_code == 0, result.output
        assert (tmp_path / "eng-example" / "input" / "engagement.yaml").is_file()
        assert (tmp_path / "eng-example" / "README.md").is_file()

    def test_missing_input_uses_the_contractual_exit_code(
        self, runner: CliRunner, tmp_path: Path
    ) -> None:
        result = runner.invoke(
            app,
            [
                "assess",
                "--engagement",
                str(tmp_path / "nope.yaml"),
                "--input",
                str(tmp_path),
                "--out",
                str(tmp_path / "out"),
            ],
        )
        assert getattr(result.exception, "exit_code", None) == ExitCode.INPUT_NOT_FOUND


def test_no_cli_command_can_reach_a_customer_environment() -> None:
    """A structural check: nothing in the package imports a cloud or database client."""
    import dbmodernize

    package_root = Path(dbmodernize.__file__).parent
    forbidden = ("azure.identity", "azure.mgmt", "pyodbc", "psycopg", "pymssql", "boto3")

    offenders: list[str] = []
    for path in package_root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for module in forbidden:
            if f"import {module}" in text or f"from {module}" in text:
                offenders.append(f"{path.name}: {module}")

    assert not offenders, f"Core package imports a client library: {offenders}"
