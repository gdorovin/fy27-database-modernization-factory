# Assessment summary — litware-manufacturing

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-litware-manufacturing-fy27` |
| As at | 2026-06-08 |
| Primary trigger | `oracle-cost-or-audit-pressure` |
| Workloads assessed | 3 |
| Inventory completeness | low |

## What the customer asked for

1. Reduce the annual cost and audit exposure of the current database estate.
2. Keep the plant running; nothing here is worth a production stoppage.
3. Understand which systems can realistically move, and which should be left alone.

A manufacturer under licensing and audit pressure on its Oracle estate. Several schemas carry substantial PL/SQL, and the plant systems are supported by a vendor whose terms have not been reviewed. The customer wants an honest disposition per system, not a programme that assumes everything moves.

## Inventory completeness

No estate-level coverage evidence was supplied, so completeness is unproven. Sources: csv-inventory, ssma.

Completeness is judged `low`. An estate that has
not been proven complete cannot support a claim about total scope, cost, or timeline.

### Evidence sources

| Source | Records |
| --- | --- |
| csv-inventory | 3 |
| ssma | 2 |

## Blocking issues

No workload has an open blocking finding.

## Evidence conflicts

No unresolved conflicts between evidence sources.

## Imported content flagged for review

No imported content matched a prompt-injection pattern.

## Workloads

| Workload | Platform | Version | Support | Environment | Criticality | Findings | Ready for a target decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Finance ledger | oracle | 19.3 | unknown | production | critical | 2 | Yes |
| Order management | oracle | 19.3 | unknown | production | high | 1 | Yes |
| Plant maintenance | oracle | 12.2 | unknown | production | high | 0 | Yes |

## Findings by workload

### Finance ledger (`wl-finance-ledger`)

- Sizing: 480.0 GB, measured

- Service level: RPO 5, RTO 60
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| The workload is in scope for SOX, so landing-zone controls and evidence collection must be agreed before migration. | security | medium | user-provided | No |
| Schema and code conversion is required: 76 object(s) need manual work and 12 failed to convert. Automatic conversion covered 85.0% of objects. A conversion percentage is not a compatibility verdict; converted code still has to be tested against the application. | compatibility | high | observed | No |

### Order management (`wl-order-management`)

- Sizing: 720.0 GB, measured

- Service level: RPO 15, RTO 120
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| Schema and code conversion is required: 133 object(s) need manual work and 20 failed to convert. Automatic conversion covered 84.1% of objects. A conversion percentage is not a compatibility verdict; converted code still has to be tested against the application. | compatibility | high | observed | No |

### Plant maintenance (`wl-plant-maintenance`)

- Sizing: 210.0 GB, measured

- Service level: RPO 30, RTO 240
- Instance features in use: none recorded
- Dependency discovery complete: Yes

No findings recorded.


## Risks raised

No risks were derived from this assessment.

## What this document is not

It is not an approval, a commitment, or a statement of cost. Every recommendation
downstream of it requires architecture review, and every production change requires
documented approval from the business, application, database, security, and operations
owners.

> Reference tables were last verified on 2026-09-15. Support status, service capabilities, and limits change. Revalidate against current product documentation before presenting any conclusion drawn from them to a customer.
