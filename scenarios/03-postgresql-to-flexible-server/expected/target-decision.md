# Target decisions — tailwind-logistics

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-tailwind-logistics-fy27` |
| As at | 2026-05-11 |
| Recommendations | 3 |
| Workloads with no recommendation | 0 |

Every entry below is a **recommendation**, not a decision. It becomes a decision when an
architecture review records an approval against it, and the approver cannot be the author.

## Workloads with no recommendation

Every workload received a recommendation.

## Recommendations

### Partner integration (`wl-partner-integration`)

| | |
| --- | --- |
| Recommended target | **azure-database-for-postgresql-flexible-server** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Azure-database-for-postgresql-flexible-server scored highest (68) for Partner integration on the published comparison. Managed flexible server is the default for this engine family (+20); Built-in high availability, backup, and patching reduce operational load (+10); Extensions in use must be verified per extension and per version before this target can be confirmed: pg_stat_statements, pgcrypto (-12). This is a recommendation and requires architecture review before it becomes a decision.

#### Options considered

| Target | Verdict | Score | Reasoning |
| --- | --- | --- | --- |
| azure-database-for-postgresql-flexible-server | recommended | 68.0 | Managed flexible server is the default for this engine family (+20); Built-in high availability, backup, and patching reduce operational load (+10); Extensions in use must be verified per extension and per version before this target can be confirmed: pg_stat_statements, pgcrypto (-12) |
| retain-on-premises | rejected | 30.0 | Scored 30 against 68 for azure-database-for-postgresql-flexible-server. Retaining the workload leaves every current risk in place (-20) |
| self-managed-on-azure-vm | rejected | 42.0 | Scored 42 against 68 for azure-database-for-postgresql-flexible-server. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10) |

#### Why the alternatives were not chosen

- **retain-on-premises** — Scored 30 against 68 for azure-database-for-postgresql-flexible-server. Retaining the workload leaves every current risk in place (-20).
- **self-managed-on-azure-vm** — Scored 42 against 68 for azure-database-for-postgresql-flexible-server. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10).

#### Compatibility

- Extension availability must be verified per extension and per version: pg_stat_statements, pgcrypto

#### Operations

- Platform-managed patching, backup, and high availability reduce operational load.
- Monitoring and alerting still need to be configured and owned.

#### Security

- Private network access, managed identity, and encryption in transit and at rest are landing-zone requirements and are checked separately.
- In scope for GDPR; control evidence must be collected during validation.

#### Performance

- Sizing is based on measured figures; target sizing must still be validated against a baseline comparison after migration.

#### Data residency

- Data residency requirement recorded as eu-north.

#### Application impact

- No application change is implied by the target itself.
- Connection strings, retry logic, and driver versions must be reviewed.

#### Downtime approach

| | |
| --- | --- |
| Method | Continuous replication with a planned application cutover window. |
| Expected class | `short-planned` |
| Basis | A budget of 90 minutes has been stated. The class stays short-planned until a rehearsal measures the actual window. |
| Measured | No |

The downtime class is provisional. It stays provisional until a rehearsal produces a
measured figure; no stronger claim is available before then.

#### Cost inputs

No cost inputs were supplied. The repository does not invent cost figures; the business
case needs them from the customer or the account team.

#### Evidence and assumptions

- Evidence: ev-csv-inventory-wl-partner-integration-inv-cbf84850
- Assumptions: none recorded.

### Routing engine (`wl-routing-engine`)

| | |
| --- | --- |
| Recommended target | **azure-database-for-postgresql-flexible-server** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Azure-database-for-postgresql-flexible-server scored highest (68) for Routing engine on the published comparison. Managed flexible server is the default for this engine family (+20); Built-in high availability, backup, and patching reduce operational load (+10); Extensions in use must be verified per extension and per version before this target can be confirmed: pg_cron, pg_stat_statements, postgis (-12). This is a recommendation and requires architecture review before it becomes a decision.

#### Options considered

| Target | Verdict | Score | Reasoning |
| --- | --- | --- | --- |
| azure-database-for-postgresql-flexible-server | recommended | 68.0 | Managed flexible server is the default for this engine family (+20); Built-in high availability, backup, and patching reduce operational load (+10); Extensions in use must be verified per extension and per version before this target can be confirmed: pg_cron, pg_stat_statements, postgis (-12) |
| retain-on-premises | rejected | 30.0 | Scored 30 against 68 for azure-database-for-postgresql-flexible-server. Retaining the workload leaves every current risk in place (-20) |
| self-managed-on-azure-vm | rejected | 37.0 | Scored 37 against 68 for azure-database-for-postgresql-flexible-server. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10); Availability design remains the customer's responsibility on infrastructure (-5) |

#### Why the alternatives were not chosen

- **retain-on-premises** — Scored 30 against 68 for azure-database-for-postgresql-flexible-server. Retaining the workload leaves every current risk in place (-20).
- **self-managed-on-azure-vm** — Scored 37 against 68 for azure-database-for-postgresql-flexible-server. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10); Availability design remains the customer's responsibility on infrastructure (-5).

#### Compatibility

- Extension availability must be verified per extension and per version: pg_cron, pg_stat_statements, postgis

#### Operations

- Platform-managed patching, backup, and high availability reduce operational load.
- Monitoring and alerting still need to be configured and owned.

#### Security

- Private network access, managed identity, and encryption in transit and at rest are landing-zone requirements and are checked separately.

#### Performance

- Sizing is based on measured figures; target sizing must still be validated against a baseline comparison after migration.

#### Data residency

- Data residency requirement recorded as eu-north.

#### Application impact

- No application change is implied by the target itself.
- Connection strings, retry logic, and driver versions must be reviewed.

#### Downtime approach

| | |
| --- | --- |
| Method | Continuous replication with a planned application cutover window. |
| Expected class | `short-planned` |
| Basis | A budget of 45 minutes has been stated. The class stays short-planned until a rehearsal measures the actual window. |
| Measured | No |

The downtime class is provisional. It stays provisional until a rehearsal produces a
measured figure; no stronger claim is available before then.

#### Cost inputs

No cost inputs were supplied. The repository does not invent cost figures; the business
case needs them from the customer or the account team.

#### Evidence and assumptions

- Evidence: ev-csv-inventory-wl-routing-engine-inventor-2fe4c575
- Assumptions: none recorded.

### Tracking history (`wl-tracking-history`)

| | |
| --- | --- |
| Recommended target | **azure-database-for-postgresql-flexible-server** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Azure-database-for-postgresql-flexible-server scored highest (68) for Tracking history on the published comparison. Managed flexible server is the default for this engine family (+20); Built-in high availability, backup, and patching reduce operational load (+10); Extensions in use must be verified per extension and per version before this target can be confirmed: pg_partman, pg_stat_statements (-12). This is a recommendation and requires architecture review before it becomes a decision.

#### Options considered

| Target | Verdict | Score | Reasoning |
| --- | --- | --- | --- |
| azure-database-for-postgresql-flexible-server | recommended | 68.0 | Managed flexible server is the default for this engine family (+20); Built-in high availability, backup, and patching reduce operational load (+10); Extensions in use must be verified per extension and per version before this target can be confirmed: pg_partman, pg_stat_statements (-12) |
| retain-on-premises | rejected | 30.0 | Scored 30 against 68 for azure-database-for-postgresql-flexible-server. Retaining the workload leaves every current risk in place (-20) |
| self-managed-on-azure-vm | rejected | 42.0 | Scored 42 against 68 for azure-database-for-postgresql-flexible-server. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10) |

#### Why the alternatives were not chosen

- **retain-on-premises** — Scored 30 against 68 for azure-database-for-postgresql-flexible-server. Retaining the workload leaves every current risk in place (-20).
- **self-managed-on-azure-vm** — Scored 42 against 68 for azure-database-for-postgresql-flexible-server. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10).

#### Compatibility

- Extension availability must be verified per extension and per version: pg_partman, pg_stat_statements

#### Operations

- Platform-managed patching, backup, and high availability reduce operational load.
- Monitoring and alerting still need to be configured and owned.

#### Security

- Private network access, managed identity, and encryption in transit and at rest are landing-zone requirements and are checked separately.

#### Performance

- Sizing is based on measured figures; target sizing must still be validated against a baseline comparison after migration.

#### Data residency

- Data residency requirement recorded as eu-north.

#### Application impact

- No application change is implied by the target itself.
- Connection strings, retry logic, and driver versions must be reviewed.

#### Downtime approach

| | |
| --- | --- |
| Method | Continuous replication with a planned application cutover window. |
| Expected class | `short-planned` |
| Basis | A budget of 180 minutes has been stated. The class stays short-planned until a rehearsal measures the actual window. |
| Measured | No |

The downtime class is provisional. It stays provisional until a rehearsal produces a
measured figure; no stronger claim is available before then.

#### Cost inputs

No cost inputs were supplied. The repository does not invent cost figures; the business
case needs them from the customer or the account team.

#### Evidence and assumptions

- Evidence: ev-csv-inventory-wl-tracking-history-invent-a97e4782
- Assumptions: none recorded.


> Reference tables were last verified on 2026-09-16. Support status, service capabilities, and limits change. Revalidate against current product documentation before presenting any conclusion drawn from them to a customer.
