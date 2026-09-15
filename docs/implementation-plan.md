# Implementation plan

Status: living document. Updated as phases complete.

## Phase 0 findings (inspection)

The repository was empty before this work started.

| Check | Result |
| --- | --- |
| Existing files | None. `git init -b main` produced an empty repository. |
| Python | 3.12.13 available on PATH. |
| Git | 2.55.0. |
| Azure subscription | Not assumed. Core must run fully offline. |
| LLM availability | Not assumed. Core must run without a model. |

No pre-existing content had to be preserved.

## Assumptions

These are decisions taken so implementation could proceed without blocking questions.
Each is reversible.

| ID | Assumption | Rationale | Reversal cost |
| --- | --- | --- | --- |
| A-001 | Python 3.12 + Typer + Pydantic v2 + JSON Schema 2020-12 | Stated in the brief; widely available | Low |
| A-002 | `dbmodernize` CLI is the only supported entry point for the deterministic pipeline | One surface to test and document | Low |
| A-003 | Scoring for target recommendation is rule-based and configurable, never model-based | Keeps CI deterministic and auditable | Medium |
| A-004 | Scenario expectations are committed as files and compared exactly | Makes regressions visible in diffs | Low |
| A-005 | Playbook policy IDs are strings of the form `SEC-001`, `NET-002`, etc. | Enables duplicate/conflict detection | Low |
| A-006 | CODEOWNERS teams are placeholders (`@REPLACE-ME-ORG/...`) | Repository has no real org yet | Low |
| A-007 | GitHub issue creation is generation-only by default | Safety boundary in the brief | Low |
| A-008 | Confidence is an enum (`low`/`medium`/`high`), not a float | Avoids false precision in evidence handling | Medium |
| A-009 | `near-zero planned downtime` is the strongest downtime claim permitted, and only with a cited method | Safety boundary in the brief | Low |
| A-010 | Product/commercial claims live in dated reference blocks with a `verified_on` date | Facts age; the repository must show when | Low |

## Phase order and completion criteria

| Phase | Content | Done when |
| --- | --- | --- |
| 0 | Inspection, plan, assumptions | This file exists and lists assumptions |
| 1 | Packaging, dev container, lint/type/test config, CLI skeleton, global instructions | `dbmodernize --help` works; lint, types, smoke test pass |
| 2 | JSON Schemas, Pydantic models, default playbook, playbook validator | Every schema has positive and negative fixtures; conflicting and duplicate policies fail |
| 3 | Templates, renderers, evidence normalization, issue generation | Same input yields byte-identical output; overwrite protection works |
| 4 | 17 Agent Skills | Every skill passes structural validation; invoke/do-not-invoke classified |
| 5 | 8 agents | Least-privilege tools enforced; no self-approval |
| 6 | 7 scenarios | Each runs offline against committed expectations; Scenario 07 yields no-go |
| 7 | CI, security, evaluation workflows | Deterministic gates on PR; model evals separate |
| 8 | Documentation and diagrams | Tree matches docs; commands verified |
| 9 | Optional adapters and Bicep | Present, labelled optional, mockable, not required by core |

## Out of scope

Deliberately not built, and documented as such in the README:

- Executing a migration.
- Performing a cutover.
- Deleting or modifying source systems.
- Creating live GitHub issues without explicit confirmation.
- Deploying Azure infrastructure from the core CLI.
- Asserting current pricing, funding eligibility, or preview status as fact.

## Traceability

Every artifact carries `evidence_refs`, `assumptions`, `confidence`, and `playbook_version`.
The chain is verified by `dbmodernize validate-scenario`:

```
source evidence -> normalized evidence -> assessment finding -> target decision
  -> migration wave -> migration plan -> validation report -> approval -> issue
```
