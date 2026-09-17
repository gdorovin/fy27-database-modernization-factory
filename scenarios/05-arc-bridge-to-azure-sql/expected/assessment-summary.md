# Assessment summary — adatum-group

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-adatum-group-fy27` |
| As at | 2026-07-06 |
| Primary trigger | `security-or-compliance-finding` |
| Workloads assessed | 4 |
| Inventory completeness | low |

## What the customer asked for

1. Know what database estate actually exists, with evidence rather than a spreadsheet.
2. Bring the whole estate under one security and governance baseline, including the parts that cannot move yet.
3. Restart a migration programme that stalled because nobody could agree on scope.

A group with databases across several business units and two acquisitions. A previous migration attempt stalled when the inventory turned out to be wrong. The security team has an open finding covering the estate as a whole, and it cannot be closed for systems nobody can enumerate.

## Inventory completeness

Compared enrolled instances (3) with the stated estate total (55). Sources: arc-enabled-sql, csv-inventory.

Completeness is judged `low`. An estate that has
not been proven complete cannot support a claim about total scope, cost, or timeline.

### Evidence sources

| Source | Records |
| --- | --- |
| arc-enabled-sql | 4 |
| csv-inventory | 4 |

## Blocking issues

2 workload(s) cannot receive a target recommendation until
the findings below are closed. This is deliberate: recommending a destination from
incomplete evidence produces a decision nobody can defend.

### Acquired unit b sales (`wl-acquired-unit-b-sales`)

- **dependency** — Dependency discovery is incomplete, so the consumers of this database and the blast radius of a cutover are unknown.
  - Evidence class: `observed`
  - Evidence: ev-csv-inventory-wl-acquired-unit-b-sales-i-83530d86
  - Remediation: Run dependency mapping and confirm every consumer with its application owner.
### Legacy warehouse (`wl-legacy-warehouse`)

- **dependency** — Dependency discovery is incomplete, so the consumers of this database and the blast radius of a cutover are unknown.
  - Evidence class: `observed`
  - Evidence: ev-arc-sql-wl-legacy-warehouse-arc-inventor-302ee897, ev-csv-inventory-wl-legacy-warehouse-invent-98e9db73
  - Remediation: Run dependency mapping and confirm every consumer with its application owner.
- **data-quality** — Evidence sources disagree about: data_size_gb. The repository will not choose between them.
  - Evidence class: `observed`
  - Evidence: ev-arc-sql-wl-legacy-warehouse-arc-inventor-302ee897, ev-csv-inventory-wl-legacy-warehouse-invent-98e9db73
  - Remediation: Have the database owner reconcile the sources and record the decision.

## Evidence conflicts

Sources disagree on the following. The repository records the disagreement and does not
choose between them; resolution is a human decision.

| Subject | Attribute | Values | Owner |
| --- | --- | --- | --- |
| `wl-legacy-warehouse` | data_size_gb | 1250.0 / 980 | database-owner |

## Imported content flagged for review

No imported content matched a prompt-injection pattern.

## Workloads

| Workload | Platform | Version | Support | Environment | Criticality | Findings | Ready for a target decision |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Acquired unit b sales | sql-server | 12.0 | end-of-support | production | high | 5 | No |
| Group finance | sql-server | 14.0 | extended-support | production | critical | 3 | Yes |
| Legacy warehouse | sql-server | 11.0 | end-of-support | production | medium | 6 | No |
| Shared services | sql-server | 14.0 | extended-support | production | medium | 1 | Yes |

## Findings by workload

### Acquired unit b sales (`wl-acquired-unit-b-sales`)

- Sizing: 300.0 GB, estimated

- Service level: RPO unstated, RTO unstated (assumed)
- Instance features in use: sql-agent
- Dependency discovery complete: No

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| Dependency discovery is incomplete, so the consumers of this database and the blast radius of a cutover are unknown. | dependency | blocker | observed | Yes |
| Engine version 12.0 is past end of support, so it receives no security fixes and carries audit and cyber exposure. | support-lifecycle | high | derived | No |
| Instance-scoped features are in use (sql-agent). A database-scoped target would require application change. | compatibility | high | observed | No |
| No RPO or RTO has been stated, so no availability design can be justified and no rollback window can be sized. | availability | high | assumption | No |
| Sizing figures are estimates rather than measurements, so they cannot support a capacity or cost commitment. | performance | medium | assumption | No |

### Group finance (`wl-group-finance`)

- Sizing: 540.0 GB, measured

- Service level: RPO 5, RTO 60
- Instance features in use: linked-servers, sql-agent
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| The workload is in scope for SOX, so landing-zone controls and evidence collection must be agreed before migration. | security | medium | user-provided | No |
| Engine version 14.0 is in extended support; the window is finite and should anchor the modernization date. | support-lifecycle | medium | derived | No |
| Instance-scoped features are in use (linked-servers, sql-agent). A database-scoped target would require application change. | compatibility | high | observed | No |

### Legacy warehouse (`wl-legacy-warehouse`)

- Sizing: unknown, measured

- Service level: RPO unstated, RTO unstated (assumed)
- Instance features in use: polybase, sql-agent
- Dependency discovery complete: No

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| Dependency discovery is incomplete, so the consumers of this database and the blast radius of a cutover are unknown. | dependency | blocker | observed | Yes |
| Engine version 11.0 is past end of support, so it receives no security fixes and carries audit and cyber exposure. | support-lifecycle | high | derived | No |
| Evidence sources disagree about: data_size_gb. The repository will not choose between them. | data-quality | blocker | observed | Yes |
| Instance-scoped features are in use (sql-agent). A database-scoped target would require application change. | compatibility | high | observed | No |
| Engine features are in use that no managed SQL target offers (polybase). Every platform-as-a-service target is ruled out until the application stops depending on them; infrastructure targets remain available. | compatibility | high | observed | No |
| No RPO or RTO has been stated, so no availability design can be justified and no rollback window can be sized. | availability | medium | assumption | No |

### Shared services (`wl-shared-services`)

- Sizing: 150.0 GB, measured

- Service level: RPO 30, RTO 120
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| Engine version 14.0 is in extended support; the window is finite and should anchor the modernization date. | support-lifecycle | medium | derived | No |


## Risks raised

| Risk | Category | Likelihood | Impact | Severity | Owner |
| --- | --- | --- | --- | --- | --- |
| Acquired unit b sales: dependency blocker | application | high | high | blocker | application-owner |
| Legacy warehouse: dependency blocker | application | high | high | blocker | application-owner |
| Legacy warehouse: data-quality blocker | data | high | high | blocker | database-owner |

## What this document is not

It is not an approval, a commitment, or a statement of cost. Every recommendation
downstream of it requires architecture review, and every production change requires
documented approval from the business, application, database, security, and operations
owners.

> Reference tables were last verified on 2026-09-16. Support status, service capabilities, and limits change. Revalidate against current product documentation before presenting any conclusion drawn from them to a customer.
