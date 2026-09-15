"""Run a scenario end to end and compare it with committed expectations.

Two layers of checking:

* **Snapshot equality.** Every generated artifact must match the file committed under
  ``expected/``. This makes any behavioural change visible in a pull request diff.
* **Acceptance criteria.** Declarative assertions in ``scenario.yaml`` that say what the
  scenario is *for*. Snapshots catch drift; acceptance criteria catch a snapshot that was
  regenerated to make a failure disappear.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from dbmodernize.errors import FindingSet, InputNotFoundError
from dbmodernize.pipeline import PipelineResult, run_pipeline
from dbmodernize.utils.io import read_text, read_yaml, write_json, write_text, write_yaml

SCENARIO_FILE = "scenario.yaml"
INPUT_DIR = "input"
EXPECTED_DIR = "expected"


@dataclass(slots=True)
class ScenarioSpec:
    directory: Path
    engagement: Path
    evidence_dir: Path
    playbook_dir: Path
    validation_report: Path | None
    acceptance: list[dict[str, Any]]
    title: str


def load_spec(repo_root: Path, scenario_dir: Path) -> ScenarioSpec:
    config_path = scenario_dir / SCENARIO_FILE
    if not config_path.is_file():
        raise InputNotFoundError(f"{scenario_dir} has no {SCENARIO_FILE}")
    config = read_yaml(config_path) or {}

    engagement = scenario_dir / config.get("engagement", f"{INPUT_DIR}/engagement.yaml")
    evidence_dir = scenario_dir / config.get("evidence_dir", INPUT_DIR)
    playbook_dir = repo_root / config.get("playbook", "playbooks/default")
    report_value = config.get("validation_report")
    validation_report = scenario_dir / report_value if report_value else None

    return ScenarioSpec(
        directory=scenario_dir,
        engagement=engagement,
        evidence_dir=evidence_dir,
        playbook_dir=playbook_dir,
        validation_report=validation_report,
        acceptance=list(config.get("acceptance", [])),
        title=str(config.get("title", scenario_dir.name)),
    )


def run_scenario(repo_root: Path, scenario_dir: Path) -> tuple[PipelineResult, ScenarioSpec]:
    spec = load_spec(repo_root, scenario_dir)
    result = run_pipeline(
        repo_root=repo_root,
        engagement_path=spec.engagement,
        evidence_dir=spec.evidence_dir,
        playbook_dir=spec.playbook_dir,
        validation_report_path=spec.validation_report,
    )
    return result, spec


def validate_scenario(repo_root: Path, scenario_dir: Path, update: bool = False) -> FindingSet:
    findings = FindingSet()
    result, spec = run_scenario(repo_root, scenario_dir)
    expected_dir = scenario_dir / EXPECTED_DIR

    if update:
        _write_expectations(expected_dir, result)
        findings.add(
            rule="SCENARIO-UPDATED",
            message=(
                f"Expectations rewritten for {scenario_dir.name}. Review every line of the "
                "diff; regenerating to silence a failure defeats the purpose of the snapshot."
            ),
            path=str(expected_dir),
            severity="warning",
        )
    else:
        findings.extend(_compare(expected_dir, result, scenario_dir))

    findings.extend(_check_acceptance(spec, result))
    return findings


def validate_scenarios_tree(
    repo_root: Path, scenarios_root: Path, update: bool = False
) -> FindingSet:
    findings = FindingSet()
    if not scenarios_root.is_dir():
        findings.add(
            rule="SCENARIO-ROOT-MISSING",
            message=f"Scenarios directory not found: {scenarios_root}",
            path=str(scenarios_root),
        )
        return findings

    directories = sorted(
        d for d in scenarios_root.iterdir() if d.is_dir() and (d / SCENARIO_FILE).is_file()
    )
    if not directories:
        findings.add(
            rule="SCENARIO-ROOT-EMPTY",
            message=f"No scenarios found under {scenarios_root}",
            path=str(scenarios_root),
        )
    for directory in directories:
        findings.extend(validate_scenario(repo_root, directory, update=update))
    return findings


def _write_expectations(expected_dir: Path, result: PipelineResult) -> None:
    expected_dir.mkdir(parents=True, exist_ok=True)
    for name, payload in sorted(result.structured.items()):
        path = expected_dir / name
        if name.endswith(".json"):
            write_json(path, payload, force=True)
        else:
            write_yaml(path, payload, force=True)
    for name, text in sorted(result.documents.items()):
        write_text(expected_dir / name, text, force=True)


def _compare(expected_dir: Path, result: PipelineResult, scenario_dir: Path) -> FindingSet:
    findings = FindingSet()
    if not expected_dir.is_dir():
        findings.add(
            rule="SCENARIO-NO-EXPECTATIONS",
            message=(
                f"{scenario_dir.name} has no expected/ directory. Generate it with "
                "'dbmodernize validate-scenario <dir> --update' and review the output."
            ),
            path=str(expected_dir),
        )
        return findings

    produced = set(result.structured) | set(result.documents)
    committed = {p.name for p in expected_dir.iterdir() if p.is_file()}

    for name in sorted(produced - committed):
        findings.add(
            rule="SCENARIO-MISSING-EXPECTATION",
            message=f"Pipeline produced {name} but no expectation is committed",
            path=str(expected_dir / name),
        )
    for name in sorted(committed - produced):
        findings.add(
            rule="SCENARIO-STALE-EXPECTATION",
            message=f"{name} is committed but the pipeline no longer produces it",
            path=str(expected_dir / name),
        )

    for name in sorted(produced & committed):
        path = expected_dir / name
        if name.endswith(".json"):
            actual = result.structured[name]
            expected = json.loads(read_text(path))
        elif name.endswith(".yaml"):
            actual = result.structured[name]
            expected = yaml.safe_load(read_text(path))
        else:
            actual = result.documents[name]
            expected = read_text(path)

        if actual != expected:
            findings.add(
                rule="SCENARIO-MISMATCH",
                message=(
                    f"{name} differs from the committed expectation. "
                    + _first_difference(actual, expected)
                ),
                path=str(path),
                hint=(
                    "If the change is intended, re-run with --update and review every line "
                    "of the diff before committing."
                ),
            )
    return findings


def _first_difference(actual: Any, expected: Any) -> str:
    if isinstance(actual, str) and isinstance(expected, str):
        actual_lines = actual.splitlines()
        expected_lines = expected.splitlines()
        for index, (left, right) in enumerate(zip(actual_lines, expected_lines, strict=False), 1):
            if left != right:
                return f"First difference at line {index}: got {left!r}, expected {right!r}."
        return f"Line count differs: produced {len(actual_lines)}, expected {len(expected_lines)}."
    return _first_structural_difference(actual, expected, "")


def _first_structural_difference(actual: Any, expected: Any, path: str) -> str:
    if type(actual) is not type(expected):
        return (
            f"Type differs at {path or '<root>'}: "
            f"{type(actual).__name__} vs {type(expected).__name__}."
        )
    if isinstance(actual, dict) and isinstance(expected, dict):
        for key in sorted(set(actual) | set(expected)):
            if key not in actual:
                return f"Missing key at {path}/{key}."
            if key not in expected:
                return f"Unexpected key at {path}/{key}."
            if actual[key] != expected[key]:
                return _first_structural_difference(actual[key], expected[key], f"{path}/{key}")
    if isinstance(actual, list) and isinstance(expected, list):
        if len(actual) != len(expected):
            return f"List length differs at {path}: {len(actual)} vs {len(expected)}."
        for index, (left, right) in enumerate(zip(actual, expected, strict=True)):
            if left != right:
                return _first_structural_difference(left, right, f"{path}[{index}]")
    return f"Value differs at {path or '<root>'}: {actual!r} vs {expected!r}."


def _check_acceptance(spec: ScenarioSpec, result: PipelineResult) -> FindingSet:
    findings = FindingSet()
    for index, criterion in enumerate(spec.acceptance):
        kind = str(criterion.get("kind", ""))
        handler = _ACCEPTANCE.get(kind)
        if handler is None:
            findings.add(
                rule="SCENARIO-UNKNOWN-CRITERION",
                message=(
                    f"acceptance[{index}] has unknown kind {kind!r}. Known kinds: "
                    + ", ".join(sorted(_ACCEPTANCE))
                ),
                path=str(spec.directory / SCENARIO_FILE),
            )
            continue
        message = handler(criterion, result)
        if message:
            findings.add(
                rule="SCENARIO-ACCEPTANCE",
                message=f"acceptance[{index}] ({kind}) failed: {message}",
                path=str(spec.directory / SCENARIO_FILE),
            )
    return findings


def _c_workload_blocked(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    workload_id = str(criterion["workload"])
    workload = result.inventory.get(workload_id)
    if workload is None:
        return f"workload {workload_id} not found"
    if not workload.blocking_findings:
        return f"{workload_id} has no blocking findings"
    return None


def _c_no_recommendation(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    workload_id = str(criterion["workload"])
    if result.decisions.get(workload_id) is not None:
        return f"{workload_id} received a target recommendation but should not have"
    return None


def _c_recommended_target(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    workload_id = str(criterion["workload"])
    expected = str(criterion["target"])
    decision = result.decisions.get(workload_id)
    if decision is None:
        return f"{workload_id} has no target decision"
    if decision.recommended_target.value != expected:
        return f"{workload_id} recommends {decision.recommended_target.value}, expected {expected}"
    return None


def _c_option_not_recommended(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    workload_id = str(criterion["workload"])
    target = str(criterion["target"])
    decision = result.decisions.get(workload_id)
    if decision is None:
        return f"{workload_id} has no target decision"
    option = next((o for o in decision.considered_options if o.target.value == target), None)
    if option is None:
        return f"{target} was not considered for {workload_id}"
    if option.verdict.value == "recommended":
        return f"{target} was recommended for {workload_id} but should not have been"
    return None


def _c_conversion_required(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    workload_id = str(criterion["workload"])
    decision = result.decisions.get(workload_id)
    if decision is None:
        return f"{workload_id} has no target decision"
    if not decision.conversion_required:
        return f"{workload_id} does not record conversion_required"
    return None


def _c_wave_count(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    expected = int(criterion["value"])
    actual = len(result.waves.waves)
    return None if actual == expected else f"expected {expected} waves, found {actual}"


def _c_pilot_max(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    limit = int(criterion["value"])
    pilots = [wave for wave in result.waves.waves if wave.is_pilot]
    if not pilots:
        return "no pilot wave was created"
    size = len(pilots[0].workload_ids)
    return None if size <= limit else f"pilot contains {size} workloads, limit is {limit}"


def _c_validation_outcome(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    expected = str(criterion["value"])
    if result.validation_report is None:
        return "scenario declares no validation report"
    actual = result.validation_report.outcome.value
    return None if actual == expected else f"outcome is {actual}, expected {expected}"


def _c_rollback_triggered(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    if result.validation_report is None:
        return "scenario declares no validation report"
    expected = bool(criterion.get("value", True))
    actual = result.validation_report.rollback_triggered
    return None if actual == expected else f"rollback_triggered is {actual}, expected {expected}"


def _c_issue_matching(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    needle = str(criterion["id_contains"])
    if not any(needle in issue.id for issue in result.issues.issues):
        return f"no generated issue id contains {needle!r}"
    return None


def _c_text_absent(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    name = str(criterion["file"])
    needle = str(criterion["value"]).lower()
    document = result.documents.get(name)
    if document is None:
        return f"{name} was not produced"
    if needle in document.lower():
        return f"{name} contains forbidden text {needle!r}"
    return None


def _c_text_present(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    name = str(criterion["file"])
    needle = str(criterion["value"]).lower()
    document = result.documents.get(name)
    if document is None:
        return f"{name} was not produced"
    if needle not in document.lower():
        return f"{name} does not contain {needle!r}"
    return None


def _c_evidence_conflict(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    attribute = str(criterion["attribute"])
    if not any(c.attribute == attribute for c in result.bundle.unresolved_conflicts):
        return f"no unresolved conflict recorded for attribute {attribute!r}"
    return None


def _c_injection_detected(
    criterion: dict[str, Any],  # noqa: ARG001 - uniform handler signature
    result: PipelineResult,
) -> str | None:
    if not result.bundle.injection_flagged:
        return "no evidence record was flagged for directive-like content"
    return None


def _c_deferred(criterion: dict[str, Any], result: PipelineResult) -> str | None:
    workload_id = str(criterion["workload"])
    if workload_id not in result.waves.deferred_workload_ids:
        return f"{workload_id} was not deferred from wave planning"
    return None


_ACCEPTANCE: dict[str, Any] = {
    "workload_blocked": _c_workload_blocked,
    "no_recommendation": _c_no_recommendation,
    "recommended_target": _c_recommended_target,
    "option_not_recommended": _c_option_not_recommended,
    "conversion_required": _c_conversion_required,
    "wave_count": _c_wave_count,
    "pilot_max_workloads": _c_pilot_max,
    "validation_outcome": _c_validation_outcome,
    "rollback_triggered": _c_rollback_triggered,
    "issue_matching": _c_issue_matching,
    "text_absent": _c_text_absent,
    "text_present": _c_text_present,
    "evidence_conflict": _c_evidence_conflict,
    "injection_detected": _c_injection_detected,
    "workload_deferred": _c_deferred,
}

ACCEPTANCE_KINDS = frozenset(_ACCEPTANCE)


__all__ = [
    "ACCEPTANCE_KINDS",
    "EXPECTED_DIR",
    "INPUT_DIR",
    "SCENARIO_FILE",
    "ScenarioSpec",
    "load_spec",
    "run_scenario",
    "validate_scenario",
    "validate_scenarios_tree",
]
