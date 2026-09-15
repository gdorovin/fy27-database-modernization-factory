# Executive brief — northwind-retail

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it. This brief introduces no fact that is not already recorded in an
> underlying artifact.

**As at 2026-03-02.** Engagement `eng-northwind-retail-fy27`.

## The outcome being pursued

1. Remove unsupported database versions from the payment path before the next audit cycle.
2. Stop losing two database engineers to weekend patching every month.
3. Recover from a database failure inside the hour the business has always assumed but never tested.

A retail estate running on an engine version that no longer receives security fixes, with a renewal twelve months out and an open audit finding. Nobody currently has a confirmed list of which applications read from the payment database.

## Where the work stands

| | |
| --- | --- |
| Workloads assessed | 4 |
| Targets recommended | 4 |
| Awaiting evidence | 1 |
| Waves planned | 2 |
| Inventory completeness | low |

1 workload(s) have no recommendation because evidence is
outstanding. That is a deliberate stop, not a delay: a target chosen without the evidence
would have to be revisited later, usually after money has been spent against it.

## Proposed destinations

| Target | Workloads |
| --- | --- |
| azure-arc-enabled-sql-server | 1 |
| azure-sql-database | 2 |
| azure-sql-managed-instance | 1 |

Not every workload moves to the same place, and retaining, retiring, or replacing a
workload is a legitimate outcome rather than a failure to migrate.

## Sequence

| # | Wave | Workloads | Pilot |
| --- | --- | --- | --- |
| 1 | Wave 1 - pilot | 1 | Yes |
| 2 | Wave 2 - business critical | 2 | No |

## What could go wrong

| Risk | Severity | Owner | Mitigation |
| --- | --- | --- | --- |
| Store operations: dependency blocker | blocker | application-owner | Run dependency mapping and confirm every consumer with its application owner. |

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
| No unsupported database version remains in the payment path. | No | Estate inventory report |
| Weekend maintenance effort falls measurably. | No | Operations time recording |
| A recovery test completes inside the agreed RTO. | No | Controlled failover test |
