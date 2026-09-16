# Migration plan — Wave 2 - business critical

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-adatum-group-fy27` |
| Plan | `plan-wave-2-business-critical` |
| Wave | `wave-2-business-critical` (sequence 2) |
| As at | 2026-07-06 |
| Playbook | `playbooks/default` v1.0.0 |
| Target decisions | td-wl-group-finance |
| Tasks that change an environment | 6 |

Move the highest-criticality workloads last, with the fullest validation and rehearsal.

## Workloads and targets

| Workload | Target | Disposition | Application change | Conversion |
| --- | --- | --- | --- | --- |
| Group finance | azure-sql-managed-instance | replatform | No | No |

## Approval gates

Every task marked as changing an environment requires a recorded approval before it runs,
and documents how to undo it. Production cutover additionally requires all five owner
roles. Nothing in this repository executes any of it.

- **Provision the non-production target environment** (`wave-2-business-critical-t-provision-nonprod`, build) — owner architect
  - Rollback: Delete the non-production resource group. No production system is affected at this step.
  - Dry run first: `az deployment group what-if --template-file infra/bicep/main.bicep`
- **Seed the non-production target** (`wave-2-business-critical-t-seed-nonprod`, migrate) — owner database-owner
  - Rollback: Stop replication and drop the non-production target databases.
- **Rehearse the cutover and measure the window** (`wave-2-business-critical-t-rehearse-cutover`, migrate) — owner delivery-lead
  - Rollback: Restore the non-production target from the pre-rehearsal snapshot.
- **Rehearse the rollback** (`wave-2-business-critical-t-rehearse-rollback`, migrate) — owner operations-owner
  - Rollback: This task is the rollback rehearsal; failure means the plan is not ready.
- **Provision the production target** (`wave-2-business-critical-t-production-provision`, cutover) — owner architect
  - Rollback: Leave the source serving traffic and remove the unused production target. No traffic has moved at this point.
  - Dry run first: `az deployment group what-if --template-file infra/bicep/main.bicep`
- **Execute the cutover** (`wave-2-business-critical-t-execute-cutover`, cutover) — owner delivery-lead
  - Rollback: Invoke the documented rollback: restore application configuration to the source, confirm write availability, and reconcile any data written to the target during the window.

## Phases

### 1. Prepare

Establish readiness and close every entry criterion before anything moves.

| Task | Kind | Owner | Depends on | Changes environment | Approval |
| --- | --- | --- | --- | --- | --- |
| Confirm landing zone readiness | prepare | architect | — | No | No |
| Capture the source performance and behaviour baseline | prepare | database-owner | — | No | No |
| Confirm application dependencies with their owners | prepare | application-owner | wave-2-business-critical-t-landing-zone | No | No |

#### Confirm landing zone readiness

Verify subscription, identity, network, private connectivity, DNS, policy, logging, backup, and disaster-recovery ownership for the target scope.

- Identifier: `wave-2-business-critical-t-landing-zone`
- Owner: architect
- Dry run: `dbmodernize validate-playbook playbooks/default`
- Policies applied: IAM-001, IAM-002, IAM-003, NET-001, NET-002, NET-003, SEC-001, SEC-002, SEC-003, SEC-004, SEC-005

#### Capture the source performance and behaviour baseline

Record query latency, throughput, concurrency, and error rates over a representative period. Without this baseline, no post-migration comparison can be made and no regression can be proven.

- Identifier: `wave-2-business-critical-t-baseline`
- Owner: database-owner

#### Confirm application dependencies with their owners

Walk the dependency list with each application owner and record confirmation. Unconfirmed consumers are the usual cause of a failed cutover.

- Identifier: `wave-2-business-critical-t-dependency-confirm`
- Owner: application-owner

### 2. Build

Stand up the target and make the application able to use it.

| Task | Kind | Owner | Depends on | Changes environment | Approval |
| --- | --- | --- | --- | --- | --- |
| Provision the non-production target environment | build | architect | wave-2-business-critical-t-landing-zone | Yes | Yes |

#### Provision the non-production target environment

Deploy the target configuration to a non-production subscription using infrastructure as code, reviewing the what-if output before applying.

- Identifier: `wave-2-business-critical-t-provision-nonprod`
- Owner: architect
- Dry run: `az deployment group what-if --template-file infra/bicep/main.bicep`
- Rollback: Delete the non-production resource group. No production system is affected at this step.
- Policies applied: IAM-001, IAM-002, IAM-003, SEC-001, SEC-002, SEC-003, SEC-004, SEC-005

### 3. Migrate

Move data into the non-production target and rehearse the cutover.

| Task | Kind | Owner | Depends on | Changes environment | Approval |
| --- | --- | --- | --- | --- | --- |
| Seed the non-production target | migrate | database-owner | wave-2-business-critical-t-provision-nonprod | Yes | Yes |
| Rehearse the cutover and measure the window | migrate | delivery-lead | wave-2-business-critical-t-seed-nonprod | Yes | Yes |
| Rehearse the rollback | migrate | operations-owner | wave-2-business-critical-t-rehearse-cutover | Yes | Yes |

#### Seed the non-production target

Perform an initial data load and start continuous replication.

- Identifier: `wave-2-business-critical-t-seed-nonprod`
- Owner: database-owner
- Rollback: Stop replication and drop the non-production target databases.

#### Rehearse the cutover and measure the window

Run the full cutover sequence against non-production and measure the actual downtime. Until this produces a number, downtime expectations stay at short-planned rather than near-zero.

- Identifier: `wave-2-business-critical-t-rehearse-cutover`
- Owner: delivery-lead
- Rollback: Restore the non-production target from the pre-rehearsal snapshot.

#### Rehearse the rollback

Execute the documented rollback against non-production and confirm the source returns to service within the decision window.

- Identifier: `wave-2-business-critical-t-rehearse-rollback`
- Owner: operations-owner
- Rollback: This task is the rollback rehearsal; failure means the plan is not ready.

### 4. Validate

Produce the evidence a go / no-go decision will rest on.

| Task | Kind | Owner | Depends on | Changes environment | Approval |
| --- | --- | --- | --- | --- | --- |
| Execute the validation plan | validate | delivery-lead | wave-2-business-critical-t-rehearse-rollback | No | No |
| Review validation evidence and decide go / no-go | validate | architect | wave-2-business-critical-t-run-validation | No | No |

#### Execute the validation plan

Run every check in the validation plan and record the observed value against its tolerance. A check with no recorded observation counts as not run, not as a pass.

- Identifier: `wave-2-business-critical-t-run-validation`
- Owner: delivery-lead
- Dry run: `dbmodernize render-report --wave wave-2-business-critical`
- Policies applied: VAL-001, VAL-002, VAL-003, VAL-004

#### Review validation evidence and decide go / no-go

Review the validation report with all five approval roles. A blocking failure forces a no-go; an un-run blocking check forbids a go.

- Identifier: `wave-2-business-critical-t-review-validation`
- Owner: architect

### 5. Cutover

Move production traffic, with an explicit decision point before doing so.

| Task | Kind | Owner | Depends on | Changes environment | Approval |
| --- | --- | --- | --- | --- | --- |
| Provision the production target | cutover | architect | wave-2-business-critical-t-review-validation | Yes | Yes |
| Execute the cutover | cutover | delivery-lead | wave-2-business-critical-t-production-provision | Yes | Yes |

#### Provision the production target

Deploy the reviewed infrastructure to production after a what-if review. Requires the recorded approval of all five owner roles.

- Identifier: `wave-2-business-critical-t-production-provision`
- Owner: architect
- Dry run: `az deployment group what-if --template-file infra/bicep/main.bicep`
- Rollback: Leave the source serving traffic and remove the unused production target. No traffic has moved at this point.

#### Execute the cutover

Apply the write freeze, drain replication, switch the application, and verify the smoke tests inside the agreed window.

- Identifier: `wave-2-business-critical-t-execute-cutover`
- Owner: delivery-lead
- Rollback: Invoke the documented rollback: restore application configuration to the source, confirm write availability, and reconcile any data written to the target during the window.

### 6. Stabilize

Hold the workload under observation before anything is decommissioned.

| Task | Kind | Owner | Depends on | Changes environment | Approval |
| --- | --- | --- | --- | --- | --- |
| Run the hypercare period | stabilize | operations-owner | wave-2-business-critical-t-execute-cutover | No | No |
| Decide whether to decommission the source | decommission | business-owner | wave-2-business-critical-t-hypercare | No | No |

#### Run the hypercare period

Monitor performance, errors, and cost against baseline for the agreed period, with the rollback path still available throughout.

- Identifier: `wave-2-business-critical-t-hypercare`
- Owner: operations-owner

#### Decide whether to decommission the source

Only after hypercare completes and business acceptance is recorded. This repository never decommissions anything; the decision and the execution are both human.

- Identifier: `wave-2-business-critical-t-decommission-decision`
- Owner: business-owner


## Acceptance criteria

| Criterion | Verified by | Owner | Automated |
| --- | --- | --- | --- |
| Agreed functional and integration tests pass against the target. | Test results attached to the validation report | application-owner | Yes |
| Performance is within the agreed tolerance of the recorded baseline. | Baseline comparison in the validation report | database-owner | Yes |
| Security configuration, identity, network isolation, and auditing match policy. | Security checks in the validation report | security-owner | Yes |
| The business owner accepts the outcome against the engagement success measures. | Approval artifact recorded in the ledger | business-owner | No |

## Cutover and rollback

The cutover plan and the rollback plan are separate documents so they can be read under
pressure without scrolling past anything else:

- `cutover-plan-2.md`
- `rollback-plan-2.md`

## Validation

Validation for this wave is defined in `validation-plan-2.md`. A blocking check
that has not run is not a pass, and generated tests are supporting evidence rather than
proof.

## Evidence and provenance

- Evidence: ev-arc-sql-wl-group-finance-arc-inventory-j-8ca5ffc2, ev-csv-inventory-wl-group-finance-inventory-579278e0
- Risks: _none linked_
- Policies in force: AVL-001, AVL-002, AVL-003, AVL-004, COMP-001, COMP-002, COST-001, COST-002, DATA-001, DATA-002, DATA-003, DATA-004, IAM-001, IAM-002, IAM-003, NAME-001, NET-001, NET-002, NET-003, OBS-001, OBS-002, OBS-003, OPS-001, OPS-002, OPS-003, SEC-001, SEC-002, SEC-003, SEC-004, SEC-005, VAL-001, VAL-002, VAL-003, VAL-004
> Reference tables were last verified on 2026-09-15. Support status, service capabilities, and limits change. Revalidate against current product documentation before presenting any conclusion drawn from them to a customer.
