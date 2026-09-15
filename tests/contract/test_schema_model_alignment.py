"""Schemas and Pydantic models must not drift apart.

The schema is the portable contract; the model is the in-process one. When they disagree,
an artifact can validate in one language and fail in another, which is the worst kind of
bug to debug because both sides look correct in isolation.
"""

from __future__ import annotations

from pathlib import Path

from dbmodernize.models import SCHEMA_MODELS
from dbmodernize.validators.schema import collect_properties, collect_required, load_schemas

#: Properties the model derives or fixes rather than accepting from input.
MODEL_ONLY: dict[str, set[str]] = {}

#: Properties the schema carries that the model supplies with a constant.
SCHEMA_ONLY: dict[str, set[str]] = {}


def test_property_names_match(repo_root: Path) -> None:
    schemas = load_schemas(repo_root)
    problems: list[str] = []

    for name, model in SCHEMA_MODELS.items():
        schema_properties = collect_properties(schemas[name], schemas)
        model_fields = set(model.model_fields)

        only_in_schema = schema_properties - model_fields - SCHEMA_ONLY.get(name, set())
        only_in_model = model_fields - schema_properties - MODEL_ONLY.get(name, set())

        if only_in_schema:
            problems.append(f"{name}: in schema but not in the model: {sorted(only_in_schema)}")
        if only_in_model:
            problems.append(f"{name}: in the model but not in the schema: {sorted(only_in_model)}")

    assert not problems, "\n".join(problems)


def test_required_fields_match(repo_root: Path) -> None:
    """A field required by one layer and optional in the other is a latent bug."""
    schemas = load_schemas(repo_root)
    problems: list[str] = []

    for name, model in SCHEMA_MODELS.items():
        schema_required = collect_required(schemas[name], schemas)
        model_required = {
            field_name for field_name, field in model.model_fields.items() if field.is_required()
        }

        only_in_schema = schema_required - model_required
        only_in_model = model_required - schema_required

        if only_in_schema:
            problems.append(
                f"{name}: required by the schema but optional in the model: "
                f"{sorted(only_in_schema)}"
            )
        if only_in_model:
            problems.append(
                f"{name}: required by the model but optional in the schema: {sorted(only_in_model)}"
            )

    assert not problems, "\n".join(problems)


def test_every_artifact_schema_closes_its_object(repo_root: Path) -> None:
    """Composition needs ``unevaluatedProperties``; a flat object needs ``additionalProperties``."""
    schemas = load_schemas(repo_root)
    problems: list[str] = []

    for name in sorted(SCHEMA_MODELS):
        schema = schemas[name]
        closed = (
            schema.get("additionalProperties") is False
            or schema.get("unevaluatedProperties") is False
        )
        if not closed:
            problems.append(
                f"{name}: neither additionalProperties nor unevaluatedProperties is false, "
                "so a typo would be accepted silently"
            )

    assert not problems, "\n".join(problems)


def test_composed_schemas_do_not_use_additional_properties(repo_root: Path) -> None:
    """``additionalProperties`` cannot see through a composing ``allOf``.

    Only composition matters here. An ``allOf`` used purely for an ``if``/``then``
    conditional introduces no properties, so ``additionalProperties: false`` remains
    correct alongside it.
    """
    schemas = load_schemas(repo_root)
    problems: list[str] = []

    for name in sorted(SCHEMA_MODELS):
        schema = schemas[name]
        composes = any("$ref" in branch for branch in schema.get("allOf", []))
        if composes and schema.get("additionalProperties") is False:
            problems.append(
                f"{name}: composes another schema with allOf but closes with "
                "additionalProperties, which would reject every inherited property. "
                "Use unevaluatedProperties instead."
            )

    assert not problems, "\n".join(problems)
