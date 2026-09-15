# Assessment summary — northwind-retail

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-northwind-retail-fy27` |
| As at | 2026-03-02 |
| Primary trigger | `license-or-ea-renewal` |
| Workloads assessed | 4 |
| Inventory completeness | low |

## What the customer asked for

1. Remove unsupported database versions from the payment path before the next audit cycle.
2. Stop losing two database engineers to weekend patching every month.
3. Recover from a database failure inside the hour the business has always assumed but never tested.

A retail estate running on an engine version that no longer receives security fixes, with a renewal twelve months out and an open audit finding. Nobody currently has a confirmed list of which applications read from the payment database.

## Inventory completeness

Compared enrolled instances (2) with the stated estate total (12). Sources: arc-enabled-sql, csv-inventory.

Completeness is judged `low`. An estate that has
not been proven complete cannot support a claim about total scope, cost, or timeline.

### Evidence sources

| Source | Records |
| --- | --- |
| arc-enabled-sql | 3 |
| csv-inventory | 4 |

## Blocking issues

1 workload(s) cannot receive a target recommendation until
the findings below are closed. This is deliberate: recommending a destination from
incomplete evidence produces a decision nobody can defend.

### Store operations (`wl-store-operations`)

- **dependency** — Dependency discovery is incomplete, so the consumers of this database and the blast radius of a cutover are unknown.
  - Evidence class: `observed`
  - Evidence: ev-arc-sql-wl-store-operations-arc-inventor-101d0af9, ev-csv-inventory-wl-store-operations-invent-65706cdf
  - Remediation: Run dependency mapping and confirm every consumer with its application owner.

## Evidence conflicts

No unresolved conflicts between evidence sources.

## Imported content flagged for review

No imported content matched a prompt-injection pattern.

## Workloads

| Workload | Platform | Version | Support | Environment | Criticality | Findings | Ready for a target decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Customer portal | sql-server | 13.0 | end-of-support | production | medium | 1 | Yes |
| Payments core | sql-server | 13.0 | end-of-support | production | critical | 3 | Yes |
| Reporting sandbox | sql-server | 13.0 | end-of-support | test | low | 1 | Yes |
| Store operations | sql-server | 13.0 | end-of-support | production | high | 4 | No |

## Findings by workload

### Customer portal (`wl-customer-portal`)

- Sizing: 180.0 GB, measured

- Service level: RPO 30, RTO 120
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| Engine version 13.0 is past end of support, so it receives no security fixes and carries audit and cyber exposure. | support-lifecycle | high | derived | No |

### Payments core (`wl-payments-core`)

- Sizing: 820.0 GB, measured

- Service level: RPO 5, RTO 60
- Instance features in use: cross-database-queries, service-broker, sql-agent
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| The workload is in scope for PCI-DSS, so landing-zone controls and evidence collection must be agreed before migration. | security | medium | user-provided | No |
| Engine version 13.0 is past end of support, so it receives no security fixes and carries audit and cyber exposure. | support-lifecycle | high | derived | No |
| Instance-scoped features are in use (cross-database-queries, service-broker, sql-agent). A database-scoped target would require application change. | compatibility | high | observed | No |

### Reporting sandbox (`wl-reporting-sandbox`)

- Sizing: 40.0 GB, measured

- Service level: RPO 1440, RTO 2880
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| Engine version 13.0 is past end of support, so it receives no security fixes and carries audit and cyber exposure. | support-lifecycle | high | derived | No |

### Store operations (`wl-store-operations`)

- Sizing: 640.0 GB, measured

- Service level: RPO unstated, RTO unstated (assumed)
- Instance features in use: sql-agent
- Dependency discovery complete: No

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| Dependency discovery is incomplete, so the consumers of this database and the blast radius of a cutover are unknown. | dependency | blocker | observed | Yes |
| Engine version 13.0 is past end of support, so it receives no security fixes and carries audit and cyber exposure. | support-lifecycle | high | derived | No |
| Instance-scoped features are in use (sql-agent). A database-scoped target would require application change. | compatibility | high | observed | No |
| No RPO or RTO has been stated, so no availability design can be justified and no rollback window can be sized. | availability | high | assumption | No |


## Risks raised

| Risk | Category | Likelihood | Impact | Severity | Owner |
| --- | --- | --- | --- | --- | --- |
| Store operations: dependency blocker | application | high | high | blocker | application-owner |

## What this document is not

It is not an approval, a commitment, or a statement of cost. Every recommendation
downstream of it requires architecture review, and every production change requires
documented approval from the business, application, database, security, and operations
owners.

> Reference tables were last verified on 2026-09-15. Support status, service capabilities, and limits change. Revalidate against current product documentation before presenting any conclusion drawn from them to a customer.
