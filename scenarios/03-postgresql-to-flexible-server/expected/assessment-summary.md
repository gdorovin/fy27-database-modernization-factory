# Assessment summary — tailwind-logistics

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-tailwind-logistics-fy27` |
| As at | 2026-05-11 |
| Primary trigger | `unsupported-open-source-version` |
| Workloads assessed | 3 |
| Inventory completeness | low |

## What the customer asked for

1. Get off database versions that no longer receive security fixes.
2. Have a failover story that has actually been tested rather than assumed.
3. Stop the team maintaining replication scripts that only two people understand.

Self-managed PostgreSQL on virtual machines, several versions behind, with high availability implemented by in-house scripting. A recent security review flagged both the version and the absence of tested recovery.

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
| Partner integration | postgresql | 12.4 | end-of-support | production | high | 3 | Yes |
| Routing engine | postgresql | 11.9 | end-of-support | production | critical | 2 | Yes |
| Tracking history | postgresql | 11.9 | end-of-support | production | medium | 2 | Yes |

## Findings by workload

### Partner integration (`wl-partner-integration`)

- Sizing: 95.0 GB, measured

- Service level: RPO 15, RTO 60
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| The workload is in scope for GDPR, so landing-zone controls and evidence collection must be agreed before migration. | security | medium | user-provided | No |
| Engine version 12.4 is past end of support, so it receives no security fixes and carries audit and cyber exposure. | support-lifecycle | high | derived | No |
| Extensions or plugins are in use (pg_stat_statements, pgcrypto). Availability on the managed service must be verified per extension and per version; it cannot be assumed. | compatibility | high | observed | No |

### Routing engine (`wl-routing-engine`)

- Sizing: 410.0 GB, measured

- Service level: RPO 5, RTO 30
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| Engine version 11.9 is past end of support, so it receives no security fixes and carries audit and cyber exposure. | support-lifecycle | high | derived | No |
| Extensions or plugins are in use (pg_cron, pg_stat_statements, postgis). Availability on the managed service must be verified per extension and per version; it cannot be assumed. | compatibility | high | observed | No |

### Tracking history (`wl-tracking-history`)

- Sizing: 1900.0 GB, measured

- Service level: RPO 30, RTO 120
- Instance features in use: none recorded
- Dependency discovery complete: Yes

| Finding | Category | Severity | Evidence class | Blocking |
| --- | --- | --- | --- | --- |
| Engine version 11.9 is past end of support, so it receives no security fixes and carries audit and cyber exposure. | support-lifecycle | high | derived | No |
| Extensions or plugins are in use (pg_partman, pg_stat_statements). Availability on the managed service must be verified per extension and per version; it cannot be assumed. | compatibility | high | observed | No |


## Risks raised

No risks were derived from this assessment.

## What this document is not

It is not an approval, a commitment, or a statement of cost. Every recommendation
downstream of it requires architecture review, and every production change requires
documented approval from the business, application, database, security, and operations
owners.

> Reference tables were last verified on 2026-09-15. Support status, service capabilities, and limits change. Revalidate against current product documentation before presenting any conclusion drawn from them to a customer.
