# Executive brief — adatum-group

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it. This brief introduces no fact that is not already recorded in an
> underlying artifact.

**As at 2026-07-06.** Engagement `eng-adatum-group-fy27`.

## The outcome being pursued

1. Know what database estate actually exists, with evidence rather than a spreadsheet.
2. Bring the whole estate under one security and governance baseline, including the parts that cannot move yet.
3. Restart a migration programme that stalled because nobody could agree on scope.

A group with databases across several business units and two acquisitions. A previous migration attempt stalled when the inventory turned out to be wrong. The security team has an open finding covering the estate as a whole, and it cannot be closed for systems nobody can enumerate.

## Where the work stands

| | |
| --- | --- |
| Workloads assessed | 4 |
| Targets recommended | 4 |
| Awaiting evidence | 2 |
| Waves planned | 2 |
| Inventory completeness | low |

2 workload(s) have no recommendation because evidence is
outstanding. That is a deliberate stop, not a delay: a target chosen without the evidence
would have to be revisited later, usually after money has been spent against it.

## Proposed destinations

| Target | Workloads |
| --- | --- |
| azure-arc-enabled-sql-server | 2 |
| azure-sql-database | 1 |
| azure-sql-managed-instance | 1 |

Not every workload moves to the same place, and retaining, retiring, or replacing a
workload is a legitimate outcome rather than a failure to migrate.

## Sequence

| # | Wave | Workloads | Pilot |
| --- | --- | --- | --- |
| 1 | Wave 1 - pilot | 1 | Yes |
| 2 | Wave 2 - business critical | 1 | No |

## What could go wrong

| Risk | Severity | Owner | Mitigation |
| --- | --- | --- | --- |
| Acquired unit b sales: dependency blocker | blocker | application-owner | Run dependency mapping and confirm every consumer with its application owner. |
| Legacy warehouse: dependency blocker | blocker | application-owner | Run dependency mapping and confirm every consumer with its application owner. |
| Legacy warehouse: data-quality blocker | blocker | database-owner | Have the database owner reconcile the sources and record the decision. |

## Decisions needed from the sponsor

1. Confirm the outcomes above are the ones being measured.
2. Name the approvers for each of the five cutover roles.
3. Agree the planned-downtime budget for business-critical workloads.
4. Fund the evidence gathering that is currently blocking recommendations.

## What this brief is not

It is not a commitment to a date, a cost, or a downtime figure. Where a figure is not
recorded here, it is because it has not been measured, and estimating it would create
confidence the evidence does not support.

## How success will be judged

| Measure | Baseline known | Measured by |
| --- | --- | --- |
| Inventory completeness is evidenced rather than estimated. | Yes | Enrolled instance count reconciled against the CMDB |
| Every database reports against the security baseline. | No | Posture reporting coverage |
