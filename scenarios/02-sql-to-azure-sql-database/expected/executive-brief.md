# Executive brief — fabrikam-saas

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it. This brief introduces no fact that is not already recorded in an
> underlying artifact.

**As at 2026-04-13.** Engagement `eng-fabrikam-saas-fy27`.

## The outcome being pursued

1. Ship product changes weekly instead of monthly, without a database change becoming the bottleneck.
2. Stop over-provisioning for a peak that happens four times a year.
3. Give the product team a data foundation they can build features on without asking for infrastructure.

A software product company whose application was written in the last three years and holds no instance-scoped database dependencies. Growth is uneven and the current fixed provisioning is sized for the worst week of the year.

## Where the work stands

| | |
| --- | --- |
| Workloads assessed | 4 |
| Targets recommended | 4 |
| Awaiting evidence | 0 |
| Waves planned | 2 |
| Inventory completeness | low |


## Proposed destinations

| Target | Workloads |
| --- | --- |
| azure-sql-database | 3 |
| azure-sql-database-hyperscale | 1 |

Not every workload moves to the same place, and retaining, retiring, or replacing a
workload is a legitimate outcome rather than a failure to migrate.

## Sequence

| # | Wave | Workloads | Pilot |
| --- | --- | --- | --- |
| 1 | Wave 1 - pilot | 1 | Yes |
| 2 | Wave 2 - business critical | 3 | No |

## What could go wrong

No high-severity risks are currently open.

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
| Database changes stop blocking the weekly release. | Yes | Release pipeline records |
| Peak capacity is available without provisioning for it year-round. | No | Consumption reporting during the seasonal peak |
