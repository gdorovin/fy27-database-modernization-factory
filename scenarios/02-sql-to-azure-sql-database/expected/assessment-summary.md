# Assessment summary — fabrikam-saas

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-fabrikam-saas-fy27` |
| As at | 2026-04-13 |
| Primary trigger | `application-modernization` |
| Workloads assessed | 4 |
| Inventory completeness | low |

## What the customer asked for

1. Ship product changes weekly instead of monthly, without a database change becoming the bottleneck.
2. Stop over-provisioning for a peak that happens four times a year.
3. Give the product team a data foundation they can build features on without asking for infrastructure.

A software product company whose application was written in the last three years and holds no instance-scoped database dependencies. Growth is uneven and the current fixed provisioning is sized for the worst week of the year.

## Inventory completeness

No estate-level coverage evidence was supplied, so completeness is unproven. Sources: csv-inventory.

Completeness is judged `low`. An estate that has
not been proven complete cannot support a claim about total scope, cost, or timeline.

### Evidence sources

| Source | Records |
| --- | --- |
| csv-inventory | 4 |

## Blocking issues

No workload has an open blocking finding.

## Evidence conflicts

No unresolved conflicts between evidence sources.

## Imported content flagged for review

No imported content matched a prompt-injection pattern.

## Workloads

| Workload | Platform | Version | Support | Environment | Criticality | Findings | Ready for a target decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Product core | sql-server | 15.0 | supported | production | high | 0 | Yes |
| Product events | sql-server | 15.0 | supported | production | medium | 0 | Yes |
| Product staging | sql-server | 15.0 | supported | pre-production | low | 0 | Yes |
| Tenant metadata | sql-server | 15.0 | supported | production | high | 0 | Yes |

## Findings by workload

### Product core (`wl-product-core`)

- Sizing: 260.0 GB, measured

- Service level: RPO 15, RTO 60
- Instance features in use: none recorded
- Dependency discovery complete: Yes

No findings recorded.

### Product events (`wl-product-events`)

- Sizing: 2400.0 GB, measured

- Service level: RPO 30, RTO 120
- Instance features in use: none recorded
- Dependency discovery complete: Yes

No findings recorded.

### Product staging (`wl-product-staging`)

- Sizing: 60.0 GB, measured

- Service level: RPO 1440, RTO 2880
- Instance features in use: none recorded
- Dependency discovery complete: Yes

No findings recorded.

### Tenant metadata (`wl-tenant-metadata`)

- Sizing: 45.0 GB, measured

- Service level: RPO 15, RTO 60
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
