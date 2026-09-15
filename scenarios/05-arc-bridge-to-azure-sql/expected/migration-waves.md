# Migration waves — adatum-group

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-adatum-group-fy27` |
| As at | 2026-07-06 |
| Waves | 2 |
| Deferred workloads | 2 |

Waves are ordered lowest risk first, and workloads that depend on each other stay
together. Splitting a dependency pair across waves produces a cutover that half-works,
which is harder to recover from than either whole option.

## Deferred workloads

These workloads are not yet assignable, normally because a blocking finding is open.

- `wl-acquired-unit-b-sales` — Acquired unit b sales
- `wl-legacy-warehouse` — Legacy warehouse

## Sequence

| # | Wave | Pilot | Workloads | Depends on |
| --- | --- | --- | --- | --- |
| 1 | Wave 1 - pilot | Yes | 1 | — |
| 2 | Wave 2 - business critical | No | 1 | wave-1-pilot |

## Wave 1 - pilot

Prove the migration method, the validation gate, and the rollback path on the lowest-risk workloads before anything else moves.

| | |
| --- | --- |
| Identifier | `wave-1-pilot` |
| Sequence | 1 |
| Pilot | Yes |
| Owners | delivery-lead, database-owner, application-owner |
| Rollback required | Yes |

### Workloads

- `wl-shared-services` — Shared services

### Prerequisites

- Landing zone readiness check passes for the subscriptions in scope.
- A non-production environment exists that mirrors the target configuration.

### Entry criteria

| Criterion | Verified by | Owner | Automated |
| --- | --- | --- | --- |
| Every workload in the wave has an approved target decision. | dbmodernize validate-scenario, plus the approval ledger | architect | Yes |
| No workload in the wave has an open blocking finding. | dbmodernize assess re-run against current evidence | database-owner | Yes |
| The rollback path has been rehearsed in a non-production environment. | Rehearsal record attached to the wave as evidence | operations-owner | No |

### Exit criteria

| Criterion | Verified by | Owner | Automated |
| --- | --- | --- | --- |
| All blocking validation checks pass and none is left un-run. | dbmodernize render-report against the wave validation report | delivery-lead | Yes |
| Business and application owners have accepted the outcome. | Approval artifacts recorded in the ledger | business-owner | Yes |
| Monitoring, alerting, and the operational runbook are live and owned. | Operations owner sign-off with links to the alert rules | operations-owner | No |
| Lessons from the pilot are recorded and the plan for later waves is updated to reflect them. | Updated migration plan artifact referencing the pilot report | delivery-lead | No |

## Wave 2 - business critical

Move the highest-criticality workloads last, with the fullest validation and rehearsal.

| | |
| --- | --- |
| Identifier | `wave-2-business-critical` |
| Sequence | 2 |
| Pilot | No |
| Owners | delivery-lead, database-owner, application-owner |
| Rollback required | Yes |

### Workloads

- `wl-group-finance` — Group finance

### Prerequisites

- Landing zone readiness check passes for the subscriptions in scope.
- A non-production environment exists that mirrors the target configuration.
- Security owner has confirmed control requirements for the compliance scopes in this wave.

### Entry criteria

| Criterion | Verified by | Owner | Automated |
| --- | --- | --- | --- |
| Every workload in the wave has an approved target decision. | dbmodernize validate-scenario, plus the approval ledger | architect | Yes |
| No workload in the wave has an open blocking finding. | dbmodernize assess re-run against current evidence | database-owner | Yes |
| The rollback path has been rehearsed in a non-production environment. | Rehearsal record attached to the wave as evidence | operations-owner | No |

### Exit criteria

| Criterion | Verified by | Owner | Automated |
| --- | --- | --- | --- |
| All blocking validation checks pass and none is left un-run. | dbmodernize render-report against the wave validation report | delivery-lead | Yes |
| Business and application owners have accepted the outcome. | Approval artifacts recorded in the ledger | business-owner | Yes |
| Monitoring, alerting, and the operational runbook are live and owned. | Operations owner sign-off with links to the alert rules | operations-owner | No |

