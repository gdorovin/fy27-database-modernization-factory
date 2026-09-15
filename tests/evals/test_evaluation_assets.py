"""Deterministic checks over the evaluation assets.

No model runs here. These verify that the rubric is wired to checks that exist, that the
datasets stay consistent with the repository, and that a dimension cannot quietly stop being
enforced. Model-based evaluation is a separate, non-gating workflow.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from dbmodernize.validators.scenario import ACCEPTANCE_KINDS

EVALS = Path(__file__).parent


def _load(relative: str) -> dict[str, Any]:
    return yaml.safe_load((EVALS / relative).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def rubric() -> dict[str, Any]:
    return _load("rubrics/modernization-quality.yaml")


@pytest.fixture(scope="module")
def refusals() -> dict[str, Any]:
    return _load("datasets/refusal-boundaries.yaml")


@pytest.fixture(scope="module")
def selection() -> dict[str, Any]:
    return _load("datasets/skill-selection.yaml")


@pytest.fixture(scope="module")
def outcomes() -> dict[str, Any]:
    return _load("expected/scenario-outcomes.yaml")


REQUIRED_DIMENSIONS = frozenset(
    {
        "factual-grounding",
        "evidence-traceability",
        "completeness",
        "target-selection-quality",
        "policy-adherence",
        "risk-identification",
        "cutover-rollback-completeness",
        "safety",
        "no-fabrication",
        "unknown-handling",
        "skill-activation",
        "refusal",
        "executive-usefulness",
    }
)


class TestRubric:
    def test_every_required_dimension_is_covered(self, rubric: dict[str, Any]) -> None:
        present = {dimension["id"] for dimension in rubric["dimensions"]}
        assert present >= REQUIRED_DIMENSIONS, (
            f"Missing rubric dimensions: {sorted(REQUIRED_DIMENSIONS - present)}"
        )

    def test_every_dimension_names_a_deterministic_check(self, rubric: dict[str, Any]) -> None:
        """A dimension evaluated only by a model is a dimension nothing enforces."""
        for dimension in rubric["dimensions"]:
            check = dimension.get("deterministic")
            assert check, f"{dimension['id']} has no deterministic check"
            assert check["kind"] in {"test", "acceptance", "scenario"}
            assert check["reference"]

    def test_deterministic_references_resolve(
        self, rubric: dict[str, Any], repo_root: Path
    ) -> None:
        """A rubric pointing at a test that no longer exists is worse than no rubric."""
        problems: list[str] = []

        for dimension in rubric["dimensions"]:
            check = dimension["deterministic"]
            reference = str(check["reference"])

            if check["kind"] == "test":
                path_part = reference.split("::")[0]
                test_name = reference.split("::")[-1]
                path = repo_root / path_part
                if not path.is_file():
                    problems.append(f"{dimension['id']}: no such file {path_part}")
                elif f"def {test_name}(" not in path.read_text(encoding="utf-8"):
                    problems.append(f"{dimension['id']}: {path_part} has no {test_name}")
            elif check["kind"] == "acceptance":
                if reference not in ACCEPTANCE_KINDS:
                    problems.append(f"{dimension['id']}: unknown acceptance kind {reference}")
            else:
                if not (repo_root / "scenarios" / reference).is_dir():
                    problems.append(f"{dimension['id']}: no such scenario {reference}")

        assert not problems, "\n".join(problems)

    def test_every_dimension_describes_its_failure_mode(self, rubric: dict[str, Any]) -> None:
        """Naming the failure is what makes a rubric usable by a human reviewer."""
        for dimension in rubric["dimensions"]:
            assert dimension.get("failure_looks_like"), f"{dimension['id']} names no failure"
            assert len(dimension["model_guidance"]) > 60

    def test_evaluator_configuration_must_differ_from_generation(
        self, rubric: dict[str, Any]
    ) -> None:
        note = rubric["evaluator_note"].lower()
        assert "different configuration" in note
        assert "self-consistency" in note


class TestRefusalDataset:
    def test_it_contains_both_refusals_and_compliance(self, refusals: dict[str, Any]) -> None:
        """A dataset of refusals alone rewards a model that refuses everything."""
        expectations = {case["expected"] for case in refusals["cases"]}
        assert expectations == {"refuse", "comply"}

    def test_every_refusal_names_a_boundary_and_an_alternative(
        self, refusals: dict[str, Any]
    ) -> None:
        for case in refusals["cases"]:
            if case["expected"] != "refuse":
                continue
            assert case["boundary"], f"{case['id']} names no boundary"
            assert case["must_mention"], f"{case['id']} says nothing about why"
            assert case["safe_alternative"], f"{case['id']} refuses without offering a way forward"

    def test_refusals_cover_every_documented_safety_boundary(
        self, refusals: dict[str, Any]
    ) -> None:
        covered = " ".join(case["boundary"].lower() for case in refusals["cases"])
        for topic in (
            "production",
            "cutover",
            "deletion",
            "cost",
            "downtime",
            "self-approval",
            "instructions",
        ):
            assert topic in covered, f"No refusal case covers {topic}"

    def test_case_ids_are_unique(self, refusals: dict[str, Any]) -> None:
        ids = [case["id"] for case in refusals["cases"]]
        assert len(ids) == len(set(ids))


class TestSkillSelectionDataset:
    def test_every_named_skill_exists(self, selection: dict[str, Any], repo_root: Path) -> None:
        available = {d.name for d in (repo_root / ".github" / "skills").iterdir() if d.is_dir()}
        for case in selection["cases"]:
            named = [case["expected"], *case.get("also_acceptable", [])]
            for skill in named:
                if skill is None:
                    continue
                assert skill in available, f"{case['id']} names unknown skill {skill}"

    def test_every_skill_is_exercised_by_at_least_one_case(
        self, selection: dict[str, Any], repo_root: Path
    ) -> None:
        """A skill nothing selects is a skill nobody will ever reach."""
        available = {d.name for d in (repo_root / ".github" / "skills").iterdir() if d.is_dir()}
        exercised = {case["expected"] for case in selection["cases"] if case["expected"]}
        assert available <= exercised, f"Never selected: {sorted(available - exercised)}"

    def test_an_ambiguous_case_expects_a_question_rather_than_a_guess(
        self, selection: dict[str, Any]
    ) -> None:
        ambiguous = [case for case in selection["cases"] if case["expected"] is None]
        assert ambiguous, "the dataset needs at least one genuinely ambiguous request"
        for case in ambiguous:
            assert len(case["also_acceptable"]) >= 2
            assert "ask" in case["boundary_note"].lower()

    def test_cross_family_confusion_is_covered(self, selection: dict[str, Any]) -> None:
        """Choosing a platform skill for the wrong engine family is the classic error."""
        notes = " ".join(case["boundary_note"].lower() for case in selection["cases"])
        assert "cross-family" in notes or "wrong engine family" in notes


class TestScenarioOutcomes:
    def test_every_scenario_has_expectations(
        self, outcomes: dict[str, Any], scenario_dirs: list[Path]
    ) -> None:
        declared = set(outcomes["scenarios"])
        actual = {directory.name for directory in scenario_dirs}
        assert declared == actual, f"Mismatch: {declared ^ actual}"

    def test_every_scenario_states_both_what_must_and_must_not_hold(
        self, outcomes: dict[str, Any]
    ) -> None:
        """Only stating what must hold lets an over-eager output pass."""
        for name, expectations in outcomes["scenarios"].items():
            assert expectations["must_hold"], f"{name} states nothing that must hold"
            assert expectations["must_not_hold"], f"{name} states nothing that must not"

    def test_expectations_are_written_as_checkable_sentences(
        self, outcomes: dict[str, Any]
    ) -> None:
        for name, expectations in outcomes["scenarios"].items():
            for sentence in expectations["must_hold"] + expectations["must_not_hold"]:
                assert len(sentence) > 20, f"{name}: {sentence!r} is too vague to check"
                assert not re.search(r"(?i)\b(good|nice|appropriate|reasonable)\b", sentence), (
                    f"{name}: {sentence!r} uses a word nobody can evaluate"
                )


def test_no_model_evaluation_runs_in_the_default_gate() -> None:
    """Non-deterministic scoring must never decide whether a change merges."""
    for path in EVALS.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "model_eval" in text and "pytest.mark.model_eval" in text:
            assert "skipif" in text or "pytest.importorskip" in text, (
                f"{path.name}: a model-eval test must be skippable without a model"
            )
