---
applyTo: "contracts/**/*.json"
---

# Schemas

## Shape

- JSON Schema 2020-12. Every file declares `$schema`, `$id`, `title`, and a `description`
  that says what the artifact is *for*, not what fields it has.
- Objects close: `additionalProperties: false`, or `unevaluatedProperties: false` where the
  schema composes with `allOf`. The latter is required because `additionalProperties`
  cannot see through composition and would reject every inherited property.
- Every decision-oriented artifact composes `common.schema.json#/$defs/artifactBase`, so
  provenance cannot be omitted by accident.
- `examples` contains at least one realistic, synthetic instance that validates.

## Descriptions carry the reasoning

A description is the only place a future reader learns why a constraint exists. Prefer:

```json
"description": "Null means unknown. Never guess a version; an unknown version is itself a finding."
```

over `"description": "The version."`

## Compatibility

- Within a major `schema_version`, changes are backward compatible: new optional fields,
  widened enums, relaxed constraints.
- Breaking changes bump the major version and ship an ADR.
- Never remove a field without a deprecation period and a migration note.
- Never repurpose a field name. Add a new one and deprecate the old.

## Fixtures

Every schema has at least one valid fixture in `tests/fixtures/valid/<name>/` and one
invalid fixture in `tests/fixtures/invalid/<name>/`, named after the rule it violates —
`missing-evidence.json`, not `bad-2.json`. Contract tests discover them by directory
convention, so no registration is needed.

## What belongs here, and what does not

Schemas express shape, enumerations, ranges, and conditional requirements that depend on a
sibling field.

Schemas cannot express a rule that quantifies over an array or compares against external
state. Those live in the Pydantic model, and the schema carries a `$comment` saying so, so
that a reader of the schema alone is not misled into thinking it is the whole contract.

## Model alignment

`tests/contract/test_schema_model_alignment.py` fails if a schema and its Pydantic model
disagree on property names or required fields. Change both in the same commit.
