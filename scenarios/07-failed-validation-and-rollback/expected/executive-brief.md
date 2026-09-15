# Executive brief — proseware-billing

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it. This brief introduces no fact that is not already recorded in an
> underlying artifact.

**As at 2026-09-07.** Engagement `eng-proseware-billing-fy27`.

## The outcome being pursued

1. Replace hardware that is out of warranty before it fails on its own schedule.
2. Keep billing runs completing inside the overnight window they have always fitted into.
3. Be able to undo a change quickly if the billing run is affected.

A billing platform on hardware past warranty. The overnight billing run is the constraint that matters: if it does not finish before the business day, invoices are late and the finance close slips.

## Where the work stands

| | |
| --- | --- |
| Workloads assessed | 3 |
| Targets recommended | 3 |
| Awaiting evidence | 0 |
| Waves planned | 2 |
| Inventory completeness | low |


## Proposed destinations

| Target | Workloads |
| --- | --- |
| azure-sql-database | 2 |
| azure-sql-database-hyperscale | 1 |

Not every workload moves to the same place, and retaining, retiring, or replacing a
workload is a legitimate outcome rather than a failure to migrate.

## Sequence

| # | Wave | Workloads | Pilot |
| --- | --- | --- | --- |
| 1 | Wave 1 - pilot | 1 | Yes |
| 2 | Wave 2 - business critical | 2 | No |

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
| The overnight billing run completes before 06:00. | Yes | Batch scheduler records |
