# Scenarios

Executable fixtures. Each runs the whole pipeline offline and compares every generated
artifact with a committed expectation.

Two layers of checking, deliberately:

| Layer | Catches |
| --- | --- |
| **Snapshot comparison** | Any behavioural change, visible as a diff in the pull request |
| **Acceptance criteria** in `scenario.yaml` | A snapshot that was regenerated to make a failure disappear |

Either alone is defeatable. Snapshots can be regenerated; acceptance criteria can be
written loosely. Together they are hard to fool by accident.

## The seven

| # | Scenario | The mistake it prevents |
| --- | --- | --- |
| 01 | SQL Server 2016 to Managed Instance | Recommending a destination for a workload whose consumers nobody can name |
| 02 | SQL Server to Azure SQL Database | Reaching for the high-scale tier when neither size nor growth asks for it |
| 03 | PostgreSQL to Flexible Server | Waving extensions through as "compatible" without checking them per version |
| 04 | Oracle heterogeneous modernization | Treating a conversion percentage as a compatibility verdict |
| 05 | Arc bridge to Azure SQL | Counting a governed-in-place workload as modernized |
| 06 | Application, database, and AI | Promising an intelligent outcome the data cannot support |
| 07 | Failed validation and rollback | Describing a rolled-back attempt as a partial success |

## Running them

```bash
dbmodernize validate-scenario scenarios
dbmodernize validate-scenario scenarios/01-sql2016-to-managed-instance
```

No Azure subscription, no database, no model, no network.

## Structure

```text
scenarios/<nn>-<name>/
├── README.md          what it proves, and why the expected outcome is what it is
├── scenario.yaml      engagement path, playbook, acceptance criteria
├── input/             synthetic engagement, inventory, and tool exports
└── expected/          every generated artifact, committed
```

## Acceptance criteria

Declarative, checked by `dbmodernize validate-scenario`. Available kinds:

| Kind | Asserts |
| --- | --- |
| `workload_blocked` | A workload has at least one blocking finding |
| `no_recommendation` | A workload received no decision at all |
| `recommended_target` | A workload's recommended target |
| `option_not_recommended` | A target was considered but not chosen |
| `conversion_required` | A decision records that code must change |
| `wave_count` | The number of waves planned |
| `pilot_max_workloads` | The pilot is small enough to learn from |
| `workload_deferred` | A workload was not scheduled into a wave |
| `validation_outcome` | The go / no-go result |
| `rollback_triggered` | Whether rollback was invoked |
| `issue_matching` | An issue with a matching id was generated |
| `evidence_conflict` | A disagreement was surfaced rather than resolved |
| `injection_detected` | Directive-like imported content was flagged |
| `text_present` / `text_absent` | Specific wording appears, or must not |

## Changing a scenario

```bash
dbmodernize validate-scenario scenarios --update
```

Then **read every line of the diff**. Regenerating to silence a failure defeats the purpose,
and the CLI says so when you do it. If the change is intended, the acceptance criteria
should still pass; if they do not, the behaviour changed in a way the scenario was written
to prevent.

## Adding one

1. Write the README first. If you cannot say which mistake the scenario prevents, it is
   coverage rather than a test.
2. Create synthetic `input/`. Aliases only — `contoso-retail`, `host-pay-a`.
3. Write `scenario.yaml` with at least five acceptance criteria, including a negative one.
4. Generate expectations and review them.
5. Add it to the table above and to `tests/scenarios/test_scenarios.py`.
