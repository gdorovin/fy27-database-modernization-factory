"""Contract tests: schemas are valid, fixtures behave, and examples are honest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from dbmodernize.models import SCHEMA_MODELS
from dbmodernize.validators.schema import (
    check_schema_self_validity,
    get_validator,
    load_schemas,
    validate_instance,
)

#: ``common`` holds shared definitions and is not an artifact in its own right.
NON_ARTIFACT_SCHEMAS = frozenset({"common"})


def artifact_schemas(repo_root: Path) -> list[str]:
    return sorted(set(load_schemas(repo_root)) - NON_ARTIFACT_SCHEMAS)


def test_every_schema_is_itself_a_valid_schema(repo_root: Path) -> None:
    findings = check_schema_self_validity(repo_root)
    assert findings.ok, [f.render() for f in findings.errors]


def test_every_artifact_schema_has_a_model(repo_root: Path) -> None:
    """A schema without a model is a contract nothing in-process enforces."""
    missing = [name for name in artifact_schemas(repo_root) if name not in SCHEMA_MODELS]
    assert not missing, f"Schemas with no Pydantic model: {missing}"


def test_schema_examples_validate_against_their_own_schema(repo_root: Path) -> None:
    """An example that does not validate teaches the wrong shape to every reader."""
    schemas = load_schemas(repo_root)
    checked = 0

    for name in artifact_schemas(repo_root):
        for index, example in enumerate(schemas[name].get("examples", [])):
            findings = validate_instance(
                repo_root, name, example, f"contracts/{name}.schema.json#/examples/{index}"
            )
            assert findings.ok, [f.render() for f in findings.errors]
            checked += 1

    assert checked > 0, "No schema examples were found to check"


def test_schema_examples_validate_against_their_model(repo_root: Path) -> None:
    schemas = load_schemas(repo_root)

    for name in artifact_schemas(repo_root):
        model = SCHEMA_MODELS[name]
        for index, example in enumerate(schemas[name].get("examples", [])):
            try:
                model.model_validate(example)
            except ValidationError as error:  # pragma: no cover - failure path
                pytest.fail(f"{name} example {index} fails its model: {error}")


def _fixture_cases(root: Path) -> list[tuple[str, Path]]:
    if not root.is_dir():
        return []
    return sorted(
        (directory.name, path)
        for directory in root.iterdir()
        if directory.is_dir()
        for path in directory.glob("*.json")
    )


def test_valid_fixtures_pass_schema_and_model(repo_root: Path, fixtures_dir: Path) -> None:
    cases = _fixture_cases(fixtures_dir / "valid")
    assert cases, "No valid fixtures found"

    for contract, path in cases:
        instance: Any = json.loads(path.read_text(encoding="utf-8"))
        findings = validate_instance(repo_root, contract, instance, str(path))
        assert findings.ok, [f.render() for f in findings.errors]
        SCHEMA_MODELS[contract].model_validate(instance)


def test_invalid_fixtures_are_rejected_for_the_right_reason(
    repo_root: Path, fixtures_dir: Path
) -> None:
    """Rejection is not enough. A fixture that fails for an accidental reason tests nothing.

    ``expected-reasons.json`` pins the substring the failure must mention, so a fixture
    that starts failing for a different reason is caught rather than quietly counted.
    """
    cases = _fixture_cases(fixtures_dir / "invalid")
    assert cases, "No invalid fixtures found"

    expected: dict[str, str] = json.loads(
        (fixtures_dir / "invalid" / "expected-reasons.json").read_text(encoding="utf-8")
    )

    for contract, path in cases:
        key = f"{contract}/{path.stem}"
        assert key in expected, f"{key} has no entry in expected-reasons.json"

        instance: Any = json.loads(path.read_text(encoding="utf-8"))
        messages: list[str] = [
            finding.message
            for finding in validate_instance(repo_root, contract, instance, str(path))
        ]
        try:
            SCHEMA_MODELS[contract].model_validate(instance)
        except ValidationError as error:
            messages.append(str(error))

        assert messages, (
            f"{key} was accepted by both the schema and the model. "
            "An invalid fixture that validates proves nothing."
        )
        combined = " ".join(messages).lower()
        assert expected[key].lower() in combined, (
            f"{key} was rejected, but not for the expected reason "
            f"{expected[key]!r}. Got: {combined[:400]}"
        )


def test_every_contract_has_both_a_valid_and_an_invalid_fixture(
    repo_root: Path, fixtures_dir: Path
) -> None:
    """A contract with only happy-path coverage has untested constraints."""
    schemas = set(artifact_schemas(repo_root))
    valid = {contract for contract, _ in _fixture_cases(fixtures_dir / "valid")}
    invalid = {contract for contract, _ in _fixture_cases(fixtures_dir / "invalid")}

    with_examples = {name for name in schemas if load_schemas(repo_root)[name].get("examples")}
    missing_valid = schemas - valid - with_examples
    missing_invalid = schemas - invalid

    assert not missing_valid, f"No valid fixture or schema example for: {sorted(missing_valid)}"
    assert not missing_invalid, f"No invalid fixture for: {sorted(missing_invalid)}"


def test_additional_properties_are_rejected(repo_root: Path) -> None:
    """A typo must be an error, not a silent no-op."""
    schemas = load_schemas(repo_root)

    for name in artifact_schemas(repo_root):
        examples = schemas[name].get("examples")
        if not examples:
            continue
        polluted = {**examples[0], "definitely_not_a_real_field": "surprise"}
        validator = get_validator(repo_root, name)
        errors = list(validator.iter_errors(polluted))
        assert errors, f"{name} accepts an unknown property"
