# Executive brief — litware-manufacturing

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it. This brief introduces no fact that is not already recorded in an
> underlying artifact.

**As at 2026-06-08.** Engagement `eng-litware-manufacturing-fy27`.

## The outcome being pursued

1. Reduce the annual cost and audit exposure of the current database estate.
2. Keep the plant running; nothing here is worth a production stoppage.
3. Understand which systems can realistically move, and which should be left alone.

A manufacturer under licensing and audit pressure on its Oracle estate. Several schemas carry substantial PL/SQL, and the plant systems are supported by a vendor whose terms have not been reviewed. The customer wants an honest disposition per system, not a programme that assumes everything moves.

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
| azure-database-for-postgresql-flexible-server | 1 |
| azure-sql-managed-instance | 1 |
| retain-on-premises | 1 |

Not every workload moves to the same place, and retaining, retiring, or replacing a
workload is a legitimate outcome rather than a failure to migrate.

## Sequence

| # | Wave | Workloads | Pilot |
| --- | --- | --- | --- |
| 1 | Wave 1 - pilot | 1 | Yes |
| 2 | Wave 2 - business critical | 1 | No |

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
| Annual licensing and audit exposure falls. | No | Finance reporting, once the baseline is supplied |
| No production line stoppage is attributable to this programme. | Yes | Plant incident records |
