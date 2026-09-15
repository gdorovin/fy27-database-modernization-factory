# Assessment summary — proseware-billing

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-proseware-billing-fy27` |
| As at | 2026-09-07 |
| Primary trigger | `aging-hardware` |
| Workloads assessed | 3 |
| Inventory completeness | low |

## What the customer asked for

1. Replace hardware that is out of warranty before it fails on its own schedule.
2. Keep billing runs completing inside the overnight window they have always fitted into.
3. Be able to undo a change quickly if the billing run is affected.

A billing platform on hardware past warranty. The overnight billing run is the constraint that matters: if it does not finish before the business day, invoices are late and the finance close slips.

## Inventory completeness

No estate-level coverage evidence was supplied, so completeness is unproven. Sources: csv-inventory.

Completeness is judged `low`. An estate that has
not been proven complete cannot support a claim about total scope, cost, or timeline.

### Evidence sources

| Source | Records |
| --- | --- |
| csv-inventory | 3 |

## Blocking issues

No workload has an open blocking finding.

## Evidence conflicts

No unresolved conflicts between evidence sources.

## Imported content flagged for review

No imported content matched a prompt-injection pattern.

## Workloads

| Workload | Platform | Version | Support | Environment | Criticality | Findings | Ready for a target decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Billing engine | sql-server | 14.0 | extended-support | production | critical | 1 | Yes |
| Billing history | sql-server | 14.0 | extended-support | production | high | 1 | Yes |
| Billing sandbox | sql-server | 14.0 | extended-support | test | low | 1 | Yes |

## Findings by workload

### Billing engine (`wl-billing-engine`)

- Sizing: 480.0 GB, measured

- Service level: RPO 5, RTO 60
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| Engine version 14.0 is in extended support; the window is finite and should anchor the modernization date. | support-lifecycle | medium | derived | No |

### Billing history (`wl-billing-history`)

- Sizing: 1450.0 GB, measured

- Service level: RPO 15, RTO 120
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| Engine version 14.0 is in extended support; the window is finite and should anchor the modernization date. | support-lifecycle | medium | derived | No |

### Billing sandbox (`wl-billing-sandbox`)

- Sizing: 80.0 GB, measured

- Service level: RPO 1440, RTO 2880
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| Engine version 14.0 is in extended support; the window is finite and should anchor the modernization date. | support-lifecycle | medium | derived | No |


## Risks raised

No risks were derived from this assessment.

## What this document is not

It is not an approval, a commitment, or a statement of cost. Every recommendation
downstream of it requires architecture review, and every production change requires
documented approval from the business, application, database, security, and operations
owners.

> Reference tables were last verified on 2026-09-15. Support status, service capabilities, and limits change. Revalidate against current product documentation before presenting any conclusion drawn from them to a customer.
