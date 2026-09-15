# Executive brief — woodgrove-services

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it. This brief introduces no fact that is not already recorded in an
> underlying artifact.

**As at 2026-08-10.** Engagement `eng-woodgrove-services-fy27`.

## The outcome being pursued

1. Let a customer service agent answer a question in one step instead of checking four systems.
2. Release application changes without a database release becoming a separate project.
3. Be able to trust the answer a customer is given, which means trusting the data behind it.

A services business modernizing a long-lived application alongside its database, with a stated ambition to put an assistant in front of customer data. The data quality and ownership questions that ambition depends on have not been answered, and the customer has asked to be told honestly whether they are ready.

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
| azure-sql-database | 3 |

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
| An agent can answer a common question without leaving one system. | Yes | Service desk observation study |
| Every customer attribute has a named system of record and owner. | No | Data ownership register |
