"""The ``dbmodernize`` command line.

Rules this CLI keeps:

* Nothing here mutates a cloud environment. There is no code path that could.
* Exit codes are contractual and asserted in tests (see ``errors.ExitCode``).
* Errors name the artifact and the failing rule, so a message is actionable on its own.
* Output is deterministic for identical input.
* Existing files are never overwritten without ``--force``.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Annotated

import typer

from dbmodernize import __version__
from dbmodernize.errors import (
    DbModernizeError,
    ExitCode,
    FindingSet,
    SafetyRefusalError,
)
from dbmodernize.evidence.normalize import normalize_directory
from dbmodernize.issue_generation.generator import generate_issues
from dbmodernize.models.base import PlaybookRef
from dbmodernize.pipeline import load_engagement, run_pipeline
from dbmodernize.scoring.assessment import assess
from dbmodernize.scoring.targets import recommend_all
from dbmodernize.scoring.waves import plan_waves
from dbmodernize.utils.io import write_json, write_text, write_yaml
from dbmodernize.utils.logging import configure
from dbmodernize.validators.agent import validate_agents_tree
from dbmodernize.validators.playbook import validate_playbook
from dbmodernize.validators.repository import validate_repository
from dbmodernize.validators.scenario import validate_scenario, validate_scenarios_tree
from dbmodernize.validators.schema import check_schema_self_validity
from dbmodernize.validators.skill import validate_skills_tree

app = typer.Typer(
    name="dbmodernize",
    help=(
        "Guided database modernization factory. Read-only and dry-run by default: this tool "
        "produces plans and evidence, it does not migrate, deploy, or cut over anything."
    ),
    no_args_is_help=True,
    add_completion=False,
)

RepoOption = Annotated[
    Path | None,
    typer.Option("--repo", help="Repository root. Defaults to the current directory."),
]
JsonOption = Annotated[bool, typer.Option("--json", help="Emit machine-readable JSON.")]
ForceOption = Annotated[bool, typer.Option("--force", help="Overwrite existing output files.")]
DryRunOption = Annotated[
    bool, typer.Option("--dry-run", help="Report what would be written without writing it.")
]


def command_names() -> set[str]:
    """Registered command names. The repository validator checks the README against these."""
    names: set[str] = set()
    for info in app.registered_commands:
        if info.name:
            names.add(info.name)
        elif info.callback is not None:
            names.add(info.callback.__name__.replace("_", "-"))
    return names


def _repo(value: Path | None) -> Path:
    return (value or Path.cwd()).resolve()


def _report(findings: FindingSet, subject: str, as_json: bool) -> None:
    """Print findings and exit with the contractual code."""
    if as_json:
        payload = {
            "subject": subject,
            "ok": findings.ok,
            "errors": len(findings.errors),
            "warnings": len(findings.warnings),
            "findings": findings.as_dicts(),
        }
        typer.echo(json.dumps(payload, indent=2, sort_keys=True))
    else:
        for finding in findings:
            typer.echo(finding.render(), err=not findings.ok)
        if findings.ok:
            warned = f" ({len(findings.warnings)} warning(s))" if findings.warnings else ""
            typer.echo(f"OK: {subject} passed{warned}.")
        else:
            typer.echo(f"FAILED: {subject} has {len(findings.errors)} error(s).", err=True)
    raise typer.Exit(ExitCode.OK if findings.ok else ExitCode.VALIDATION_FAILED)


@app.callback()
def main(
    verbose: Annotated[bool, typer.Option("--verbose", "-v", help="Verbose logging.")] = False,
) -> None:
    configure(verbose=verbose)


@app.command()
def version() -> None:
    """Print the package version."""
    typer.echo(__version__)


@app.command()
def init(
    engagement_id: Annotated[str, typer.Option(help="Identifier for the new engagement.")],
    out: Annotated[Path, typer.Option(help="Directory to scaffold.")] = Path("engagements"),
    repo: RepoOption = None,
    force: ForceOption = False,
    dry_run: DryRunOption = False,
) -> None:
    """Scaffold an engagement folder from the repository templates."""
    root = _repo(repo)
    target = out / engagement_id
    template = (root / "templates" / "engagement-intake.yaml").read_text(encoding="utf-8")
    written = [
        write_text(
            target / "input" / "engagement.yaml",
            template.replace("REPLACE-ENGAGEMENT-ID", engagement_id),
            force=force,
            dry_run=dry_run,
        ),
        write_text(
            target / "input" / "inventory.csv",
            (root / "templates" / "workload-inventory.csv").read_text(encoding="utf-8"),
            force=force,
            dry_run=dry_run,
        ),
        write_text(
            target / "README.md",
            _engagement_readme(engagement_id),
            force=force,
            dry_run=dry_run,
        ),
    ]
    prefix = "Would create" if dry_run else "Created"
    for path in written:
        typer.echo(f"{prefix}: {path}")
    typer.echo(
        "\nNext: fill in the engagement file, drop assessment exports into input/, then run\n"
        f"  dbmodernize normalize-evidence --engagement {target / 'input' / 'engagement.yaml'} "
        f"--input {target / 'input'} --out {target / 'out'}"
    )


@app.command("validate-repo")
def validate_repo(repo: RepoOption = None, as_json: JsonOption = False) -> None:
    """Check repository structure, safety rules, and documentation consistency."""
    root = _repo(repo)
    findings = validate_repository(root)
    findings.extend(check_schema_self_validity(root))
    _report(findings, f"repository at {root}", as_json)


@app.command("validate-playbook")
def validate_playbook_command(
    playbook: Annotated[Path, typer.Argument(help="Playbook directory.")],
    as_of: Annotated[
        str | None, typer.Option(help="Evaluate exception expiry as at this date (YYYY-MM-DD).")
    ] = None,
    as_json: JsonOption = False,
) -> None:
    """Validate a playbook: duplicates, conflicts, coverage, and exception expiry."""
    reference = date.fromisoformat(as_of) if as_of else None
    _, findings = validate_playbook(playbook, as_of=reference)
    _report(findings, f"playbook {playbook}", as_json)


@app.command("validate-skill")
def validate_skill_command(
    skills: Annotated[Path, typer.Argument(help="Skills root directory.")],
    as_json: JsonOption = False,
) -> None:
    """Validate every Agent Skill under a directory."""
    _report(validate_skills_tree(skills), f"skills under {skills}", as_json)


@app.command("validate-agent")
def validate_agent_command(
    agents: Annotated[Path, typer.Argument(help="Agents root directory.")],
    as_json: JsonOption = False,
) -> None:
    """Validate agent definitions, including least-privilege tool allowlists."""
    _report(validate_agents_tree(agents), f"agents under {agents}", as_json)


@app.command("normalize-evidence")
def normalize_evidence(
    engagement: Annotated[Path, typer.Option(help="Engagement file.")],
    input_dir: Annotated[Path, typer.Option("--input", help="Directory of exports.")],
    out: Annotated[Path, typer.Option(help="Output directory.")],
    adapter: Annotated[
        str | None, typer.Option(help="Force a specific adapter instead of detecting one.")
    ] = None,
    force: ForceOption = False,
    dry_run: DryRunOption = False,
) -> None:
    """Convert third-party exports into normalized evidence, preserving provenance."""
    record = load_engagement(engagement)
    bundle = normalize_directory(
        input_dir,
        engagement_id=record.engagement_id,
        collected_on=record.as_of,
        adapter_name=adapter,
    )
    path = write_json(
        out / "evidence.json",
        bundle.model_dump(mode="json"),
        force=force,
        dry_run=dry_run,
    )
    typer.echo(
        f"{'Would write' if dry_run else 'Wrote'} {path}: {len(bundle.records)} record(s), "
        f"{len(bundle.unresolved_conflicts)} unresolved conflict(s), "
        f"{len(bundle.injection_flagged)} record(s) flagged for directive-like content."
    )
    if bundle.unresolved_conflicts:
        typer.echo(
            "Unresolved conflicts block target recommendation. Resolve them with the "
            "database owner and record the decision.",
            err=True,
        )


@app.command("assess")
def assess_command(
    engagement: Annotated[Path, typer.Option("--engagement", help="Engagement file.")],
    input_dir: Annotated[Path, typer.Option("--input", help="Directory of exports.")],
    playbook: Annotated[Path, typer.Option(help="Playbook directory.")] = Path("playbooks/default"),
    out: Annotated[Path, typer.Option(help="Output directory.")] = Path("out"),
    force: ForceOption = False,
    dry_run: DryRunOption = False,
) -> None:
    """Assess the estate: build the workload inventory, findings, and risk register."""
    record = load_engagement(engagement)
    book, findings = validate_playbook(playbook, as_of=record.as_of)
    if book is None or not findings.ok:
        _report(findings, f"playbook {playbook}", False)

    assert book is not None
    reference = PlaybookRef(
        path=book.path, version=book.version, policy_ids=[p.id for p in book.policies]
    )
    bundle = normalize_directory(
        input_dir, engagement_id=record.engagement_id, collected_on=record.as_of
    )
    inventory, risks = assess(record, bundle, reference)

    for name, payload in (
        ("evidence.json", bundle),
        ("workloads.json", inventory),
        ("risks.json", risks),
    ):
        path = write_json(out / name, payload.model_dump(mode="json"), force=force, dry_run=dry_run)
        typer.echo(f"{'Would write' if dry_run else 'Wrote'} {path}")

    blocked = [w for w in inventory.workloads if w.blocking_findings]
    typer.echo(
        f"\n{len(inventory.workloads)} workload(s) assessed. "
        f"{len(blocked)} blocked pending evidence. "
        f"{len(risks.risks)} risk(s) raised."
    )


@app.command("recommend-targets")
def recommend_targets(
    engagement: Annotated[Path, typer.Option(help="Engagement file.")],
    input_dir: Annotated[Path, typer.Option("--input", help="Directory of exports.")],
    playbook: Annotated[Path, typer.Option(help="Playbook directory.")] = Path("playbooks/default"),
    out: Annotated[Path, typer.Option(help="Output directory.")] = Path("out"),
    force: ForceOption = False,
    dry_run: DryRunOption = False,
) -> None:
    """Compare Azure targets per workload and record the rejected alternatives."""
    record = load_engagement(engagement)
    book, findings = validate_playbook(playbook, as_of=record.as_of)
    if book is None or not findings.ok:
        _report(findings, f"playbook {playbook}", False)
    assert book is not None

    reference = PlaybookRef(
        path=book.path, version=book.version, policy_ids=[p.id for p in book.policies]
    )
    bundle = normalize_directory(
        input_dir, engagement_id=record.engagement_id, collected_on=record.as_of
    )
    inventory, _ = assess(record, bundle, reference)
    decisions = recommend_all(inventory, record, book, reference)

    path = write_json(
        out / "target-decisions.json",
        decisions.model_dump(mode="json"),
        force=force,
        dry_run=dry_run,
    )
    typer.echo(f"{'Would write' if dry_run else 'Wrote'} {path}")
    typer.echo(
        f"{len(decisions.decisions)} recommendation(s). "
        f"{len(decisions.unresolved_workload_ids)} workload(s) have no recommendation "
        "because blocking evidence is outstanding."
    )


@app.command("plan-waves")
def plan_waves_command(
    engagement: Annotated[Path, typer.Option(help="Engagement file.")],
    input_dir: Annotated[Path, typer.Option("--input", help="Directory of exports.")],
    playbook: Annotated[Path, typer.Option(help="Playbook directory.")] = Path("playbooks/default"),
    out: Annotated[Path, typer.Option(help="Output directory.")] = Path("out"),
    force: ForceOption = False,
    dry_run: DryRunOption = False,
) -> None:
    """Group workloads into dependency-aware, low-risk-first waves."""
    record = load_engagement(engagement)
    book, findings = validate_playbook(playbook, as_of=record.as_of)
    if book is None or not findings.ok:
        _report(findings, f"playbook {playbook}", False)
    assert book is not None

    reference = PlaybookRef(
        path=book.path, version=book.version, policy_ids=[p.id for p in book.policies]
    )
    bundle = normalize_directory(
        input_dir, engagement_id=record.engagement_id, collected_on=record.as_of
    )
    inventory, _ = assess(record, bundle, reference)
    decisions = recommend_all(inventory, record, book, reference)
    waves = plan_waves(inventory, decisions, record, reference)

    path = write_json(
        out / "waves.json", waves.model_dump(mode="json"), force=force, dry_run=dry_run
    )
    typer.echo(f"{'Would write' if dry_run else 'Wrote'} {path}")
    typer.echo(
        f"{len(waves.waves)} wave(s). {len(waves.deferred_workload_ids)} workload(s) deferred."
    )


@app.command("render-plan")
def render_plan(
    engagement: Annotated[Path, typer.Option(help="Engagement file.")],
    input_dir: Annotated[Path, typer.Option("--input", help="Directory of exports.")],
    playbook: Annotated[Path, typer.Option(help="Playbook directory.")] = Path("playbooks/default"),
    out: Annotated[Path, typer.Option(help="Output directory.")] = Path("out"),
    repo: RepoOption = None,
    force: ForceOption = False,
    dry_run: DryRunOption = False,
) -> None:
    """Render the full document set: assessment, decisions, waves, plan, cutover, rollback."""
    root = _repo(repo)
    result = run_pipeline(root, engagement, input_dir, playbook)
    for name, text in sorted(result.documents.items()):
        path = write_text(out / name, text, force=force, dry_run=dry_run)
        typer.echo(f"{'Would write' if dry_run else 'Wrote'} {path}")


@app.command("generate-issues")
def generate_issues_command(
    engagement: Annotated[Path, typer.Option(help="Engagement file.")],
    input_dir: Annotated[Path, typer.Option("--input", help="Directory of exports.")],
    playbook: Annotated[Path, typer.Option(help="Playbook directory.")] = Path("playbooks/default"),
    out: Annotated[Path, typer.Option(help="Output directory.")] = Path("out"),
    repo: RepoOption = None,
    create: Annotated[
        bool,
        typer.Option(
            "--create",
            help="Reserved for live GitHub creation, which is not implemented and is refused.",
        ),
    ] = False,
    force: ForceOption = False,
    dry_run: DryRunOption = False,
) -> None:
    """Generate GitHub issue definitions to disk. Live creation is refused by design."""
    if create:
        raise SafetyRefusalError(
            "Live GitHub issue creation is not implemented in the core CLI. Issues are "
            "generated to disk so they can be reviewed before anything is created. See "
            "docs/copilot/issue-driven-development.md for the reviewed-then-created flow."
        )
    root = _repo(repo)
    result = run_pipeline(root, engagement, input_dir, playbook)
    issues = generate_issues(
        result.engagement, result.inventory, result.decisions, result.waves, result.playbook_ref
    )
    path = write_yaml(
        out / "issues.yaml", issues.model_dump(mode="json"), force=force, dry_run=dry_run
    )
    typer.echo(f"{'Would write' if dry_run else 'Wrote'} {path}: {len(issues.issues)} issue(s)")


@app.command("validate-scenario")
def validate_scenario_command(
    scenario: Annotated[Path, typer.Argument(help="A scenario directory, or the root.")],
    repo: RepoOption = None,
    update: Annotated[
        bool,
        typer.Option(
            "--update",
            help="Rewrite expectations. Review every line of the resulting diff.",
        ),
    ] = False,
    as_json: JsonOption = False,
) -> None:
    """Run scenarios and compare them with their committed expectations."""
    root = _repo(repo)
    if (scenario / "scenario.yaml").is_file():
        findings = validate_scenario(root, scenario, update=update)
    else:
        findings = validate_scenarios_tree(root, scenario, update=update)
    _report(findings, f"scenarios at {scenario}", as_json)


@app.command("render-report")
def render_report(
    engagement: Annotated[Path, typer.Option(help="Engagement file.")],
    input_dir: Annotated[Path, typer.Option("--input", help="Directory of exports.")],
    report: Annotated[Path, typer.Option(help="Validation report artifact.")],
    playbook: Annotated[Path, typer.Option(help="Playbook directory.")] = Path("playbooks/default"),
    out: Annotated[Path, typer.Option(help="Output directory.")] = Path("out"),
    repo: RepoOption = None,
    force: ForceOption = False,
    dry_run: DryRunOption = False,
) -> None:
    """Render a validation report and state the go / no-go outcome it supports."""
    root = _repo(repo)
    result = run_pipeline(root, engagement, input_dir, playbook, validation_report_path=report)
    if result.validation_report is None:
        typer.echo(f"No validation report could be read from {report}", err=True)
        raise typer.Exit(ExitCode.INPUT_NOT_FOUND)

    text = result.documents["validation-report.md"]
    path = write_text(out / "validation-report.md", text, force=force, dry_run=dry_run)
    typer.echo(f"{'Would write' if dry_run else 'Wrote'} {path}")
    typer.echo(f"Outcome: {result.validation_report.outcome.value}")
    if result.validation_report.outcome.value == "no-go":
        typer.echo(
            "No-go. The documented rollback path applies and corrective issues are required.",
            err=True,
        )
        raise typer.Exit(ExitCode.VALIDATION_FAILED)


def run() -> int:
    """Entry point that converts domain errors into contractual exit codes."""
    import click

    try:
        app(standalone_mode=False)
    except typer.Exit as exit_signal:
        return int(exit_signal.exit_code)
    except DbModernizeError as error:
        typer.echo(f"error: {error}", err=True)
        return int(error.exit_code)
    except click.UsageError as error:
        typer.echo(f"error: {error}", err=True)
        return int(ExitCode.USAGE_ERROR)
    except click.ClickException as error:
        typer.echo(f"error: {error}", err=True)
        return int(ExitCode.USAGE_ERROR)
    except click.Abort:
        typer.echo("aborted", err=True)
        return int(ExitCode.USAGE_ERROR)
    return int(ExitCode.OK)


def _engagement_readme(engagement_id: str) -> str:
    return f"""# Engagement {engagement_id}

Working folder created by `dbmodernize init`. Nothing here is committed to the factory
repository: engagement evidence belongs in approved customer-side storage.

## Layout

| Path | Purpose |
| --- | --- |
| `input/engagement.yaml` | Intake: outcomes, trigger, constraints, stakeholders |
| `input/inventory.csv` | Workload inventory, or drop tool exports alongside it |
| `out/` | Generated artifacts and documents |

## Order of work

1. Complete `input/engagement.yaml`. Record unknowns as open questions, never as guesses.
2. Add assessment exports to `input/`.
3. `dbmodernize assess --engagement input/engagement.yaml --input input --out out`
4. `dbmodernize recommend-targets --engagement input/engagement.yaml --input input --out out`
5. `dbmodernize plan-waves --engagement input/engagement.yaml --input input --out out`
6. `dbmodernize render-plan --engagement input/engagement.yaml --input input --out out`

Every artifact produced is a proposal. Approval is a separate, human step.
"""


if __name__ == "__main__":
    sys.exit(run())
