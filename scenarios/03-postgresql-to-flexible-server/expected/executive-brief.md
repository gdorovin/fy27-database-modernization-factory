# Executive brief — tailwind-logistics

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it. This brief introduces no fact that is not already recorded in an
> underlying artifact.

**As at 2026-05-11.** Engagement `eng-tailwind-logistics-fy27`.

## The outcome being pursued

1. Get off database versions that no longer receive security fixes.
2. Have a failover story that has actually been tested rather than assumed.
3. Stop the team maintaining replication scripts that only two people understand.

Self-managed PostgreSQL on virtual machines, several versions behind, with high availability implemented by in-house scripting. A recent security review flagged both the version and the absence of tested recovery.

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
| azure-database-for-postgresql-flexible-server | 3 |

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
| Every database runs a version that receives security fixes. | Yes | Estate inventory report |
| A failover test has been performed and the recovery time recorded. | Yes | Failover test records |
