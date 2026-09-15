---
applyTo: "tests/**"
---

# Tests

## Determinism

Default CI must never need an Azure subscription, a live database, a language model, a paid
API, or customer data. Anything that does is marked `optional_integration` or `model_eval`
and excluded from the merge gate.

- No wall-clock time in an assertion. Pin dates through the engagement's `as_of`.
- No network. No randomness. No dependence on dictionary or filesystem ordering.
- No test that passes or fails based on which machine ran it.

## Assertions

Assert on the **value**, not on the absence of an exception.

```python
# Weak: passes even if the comparison is empty.
assert decision is not None

# Strong: states what the code is for.
assert decision.recommended_target is AzureTarget.SQL_MANAGED_INSTANCE
assert any(o.verdict is OptionVerdict.BLOCKED for o in decision.considered_options)
```

A test that would still pass with the feature deleted is not a test.

## Negative tests

Every safety property has a test proving it *fails* when violated. Those matter more than
the happy path, because the happy path is what everyone checks by hand anyway.

- A blocking validation failure forces `no-go`.
- An author cannot approve their own artifact.
- A path escaping the root is rejected.
- An expired policy exception fails validation.
- A target decision with one option is rejected.

## Fixtures

- Synthetic only. Always.
- Named after what they represent: `missing-evidence.json`, not `case3.json`.
- Valid fixtures in `tests/fixtures/valid/<contract>/`, invalid in
  `tests/fixtures/invalid/<contract>/`. Contract tests discover them by convention.
- An invalid fixture violates exactly **one** rule, so a failure names the cause.

## Snapshots

- Regenerate deliberately: `dbmodernize validate-scenario scenarios --update`.
- Review every line of the resulting diff. Regenerating to make a failure disappear is the
  exact behaviour snapshots exist to prevent, and the CLI says so when you do it.
- Scenario acceptance criteria are the backstop: they assert the behaviour the snapshot is
  supposed to encode, so a silently regenerated snapshot still fails.

## Structure

| Directory | Holds |
| --- | --- |
| `tests/unit/` | Pure functions, models, scoring, adapters |
| `tests/contract/` | Schema validity, fixtures, schema/model alignment |
| `tests/repository/` | Structure and safety rules |
| `tests/skills/` | Skill structure and invoke classification |
| `tests/agents/` | Agent structure and least privilege |
| `tests/playbooks/` | Playbook parsing, conflicts, exceptions |
| `tests/scenarios/` | End-to-end scenario execution |
| `tests/security/` | Path traversal, archives, redaction, injection |
| `tests/integration/` | Cross-module flows that stay offline |
| `tests/evals/` | Datasets and rubrics for optional model evaluation |

## Speed

The fast gate runs in seconds. Mark anything slower `@pytest.mark.slow`. A gate people
skip is not a gate.
