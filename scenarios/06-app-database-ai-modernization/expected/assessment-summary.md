# Assessment summary — woodgrove-services

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-woodgrove-services-fy27` |
| As at | 2026-08-10 |
| Primary trigger | `application-modernization` |
| Workloads assessed | 3 |
| Inventory completeness | low |

## What the customer asked for

1. Let a customer service agent answer a question in one step instead of checking four systems.
2. Release application changes without a database release becoming a separate project.
3. Be able to trust the answer a customer is given, which means trusting the data behind it.

A services business modernizing a long-lived application alongside its database, with a stated ambition to put an assistant in front of customer data. The data quality and ownership questions that ambition depends on have not been answered, and the customer has asked to be told honestly whether they are ready.

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
| Case management | sql-server | 13.0 | end-of-support | production | high | 2 | Yes |
| Customer master | sql-server | 13.0 | end-of-support | production | critical | 2 | Yes |
| Reporting copy | sql-server | 13.0 | end-of-support | pre-production | low | 2 | Yes |

## Findings by workload

### Case management (`wl-case-management`)

- Sizing: 310.0 GB, measured

- Service level: RPO 15, RTO 60
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| The workload is in scope for GDPR, so landing-zone controls and evidence collection must be agreed before migration. | security | medium | user-provided | No |
| Engine version 13.0 is past end of support, so it receives no security fixes and carries audit and cyber exposure. | support-lifecycle | high | derived | No |

### Customer master (`wl-customer-master`)

- Sizing: 95.0 GB, measured

- Service level: RPO 5, RTO 30
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| The workload is in scope for GDPR, so landing-zone controls and evidence collection must be agreed before migration. | security | medium | user-provided | No |
| Engine version 13.0 is past end of support, so it receives no security fixes and carries audit and cyber exposure. | support-lifecycle | high | derived | No |

### Reporting copy (`wl-reporting-copy`)

- Sizing: 340.0 GB, measured

- Service level: RPO 1440, RTO 2880
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| Engine version 13.0 is past end of support, so it receives no security fixes and carries audit and cyber exposure. | support-lifecycle | high | derived | No |
| The source evidence carried fields this repository did not read: row 4: cells beyond the header (so it can move separately.). Any gap reported below may therefore be a gap in the adapter rather than in the estate, and the two look identical from here. | data-quality | medium | observed | No |


## Risks raised

No risks were derived from this assessment.

## What this document is not

It is not an approval, a commitment, or a statement of cost. Every recommendation
downstream of it requires architecture review, and every production change requires
documented approval from the business, application, database, security, and operations
owners.

> Reference tables were last verified on 2026-09-16. Support status, service capabilities, and limits change. Revalidate against current product documentation before presenting any conclusion drawn from them to a customer.
