# Contracts

JSON Schema 2020-12 definitions for every artifact the factory produces. These are the
portable contract — usable from any language, any tool, and any CI system. The Pydantic
models in `src/dbmodernize/models/` are the in-process mirror, and
`tests/contract/test_schema_model_alignment.py` fails if the two drift.

## Files

| Contract | Artifact | Enforces |
| --- | --- | --- |
| `common.schema.json` | Shared definitions | The provenance envelope every artifact inherits |
| `engagement.schema.json` | Engagement intake | Outcomes, trigger, constraints, cadence |
| `workload.schema.json` | One database workload | Inventory facts plus inline assessment findings |
| `evidence.schema.json` | One normalized fact | Source, collection date, evidence class, injection findings |
| `target-decision.schema.json` | Target recommendation | Two or more options, at least one rejection, a downtime basis |
| `risk.schema.json` | Risk register entry | Owner, mitigation, contingency, attributed acceptance |
| `migration-wave.schema.json` | A wave | Sequence, dependencies, entry and exit criteria |
| `migration-plan.schema.json` | Plan for a wave | Gated mutating tasks, cutover, rollback, acceptance |
| `approval.schema.json` | One role's signature | Content hash, no self-approval |
| `validation-report.schema.json` | Go / no-go evidence | Checks, tolerances, outcome consistency |
| `github-issue.schema.json` | An actionable work item | Traceability back to evidence and decision |

## The provenance envelope

Every decision-oriented artifact composes `common.schema.json#/$defs/artifactBase`
through `allOf`, which supplies:

`id`, `schema_version`, `artifact_type`, `engagement_id`, `workload_ids`, `created_at`,
`updated_at`, `author`, `evidence_refs`, `assumptions`, `confidence`, `open_questions`,
`risk_ids`, `playbook`, `approvals`, `status`, `supersedes`.

Composition uses `unevaluatedProperties: false` rather than `additionalProperties: false`,
because the latter cannot see through `allOf` and would reject every inherited property.
The effect is the same: unknown properties are rejected, so a typo fails loudly.

## What the schemas enforce, and what they cannot

Schemas enforce shape, enumerations, ranges, and conditional requirements that depend on
a sibling field — for example, a task that declares `changes_environment: true` must also
carry `approval_required: true` and a `rollback_note`.

Schemas cannot express rules that quantify over an array or compare against external
state. Those live in the Pydantic models and are called out in a `$comment`:

| Rule | Where |
| --- | --- |
| Exactly one considered option is `recommended`, at least one `rejected` | `models/decision.py` |
| A blocking validation failure forces `no-go` | `models/validation.py` |
| A `no-go` must produce corrective issues | `models/validation.py` |
| Generated tests alone cannot justify `go` | `models/validation.py` |
| An approver may not be the artifact author | `models/approval.py` |
| Waves may not share workloads or depend on a later wave | `models/planning.py` |
| `near-zero-planned` downtime requires a measured rehearsal | `models/decision.py` |
| Support status cannot be derived from an unknown version | `models/workload.py` |

Both layers run. A fixture that passes the schema but violates a model rule still fails
`make gate`.

## Status lifecycle

```text
draft -> evidence-complete -> recommended -> reviewed -> approved
      -> implementation-ready -> validating -> accepted
                                            -> rejected
any    -> superseded
```

Transitions outside this graph fail validation. `recommended -> approved` additionally
requires a matching approval artifact whose `artifact_hash` still matches the content.

## Changing a contract

1. Edit the schema. Keep it backward compatible within a major `schema_version`.
2. Update the Pydantic model in the same commit.
3. Add a valid fixture under `tests/fixtures/valid/<contract>/` and an invalid one under
   `tests/fixtures/invalid/<contract>/`, named after the rule it violates.
4. Run `make gate`. Contract tests discover fixtures by directory convention, so no test
   registration is needed.
5. A breaking change bumps the major `schema_version` and ships an ADR.
