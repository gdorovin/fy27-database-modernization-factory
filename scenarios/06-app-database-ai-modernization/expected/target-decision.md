# Target decisions — woodgrove-services

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-woodgrove-services-fy27` |
| As at | 2026-08-10 |
| Recommendations | 3 |
| Workloads with no recommendation | 0 |

Every entry below is a **recommendation**, not a decision. It becomes a decision when an
architecture review records an approval against it, and the approver cannot be the author.

## Workloads with no recommendation

Every workload received a recommendation.

## Recommendations

### Case management (`wl-case-management`)

| | |
| --- | --- |
| Recommended target | **azure-sql-database** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Azure-sql-database scored highest (75) for Case management on the published comparison. No instance-scoped dependencies, so database-level isolation fits (+15); Managed operations remove patching and backup toil (+10). This is a recommendation and requires architecture review before it becomes a decision.

#### Options considered

| Target | Verdict | Score | Reasoning |
| --- | --- | --- | --- |
| azure-arc-enabled-sql-server | rejected | 40.0 | Scored 40 against 75 for azure-sql-database. Evidence is already sufficient to choose a destination, so a bridge adds a step without adding information (-15); Governance and security posture improve without moving the workload (+5); Arc enablement is a bridge, not a completed modernization; the workload has not moved |
| azure-sql-database | recommended | 75.0 | No instance-scoped dependencies, so database-level isolation fits (+15); Managed operations remove patching and backup toil (+10) |
| azure-sql-database-hyperscale | rejected | 30.0 | Scored 30 against 75 for azure-sql-database. Neither size nor growth justifies Hyperscale; choosing it here would add capability nobody asked for (-25); Managed operations remove patching and backup toil (+5) |
| azure-sql-managed-instance | rejected | 65.0 | Scored 65 against 75 for azure-sql-database. No instance-scoped dependency was found, so instance scope is more surface area than this workload needs (-5); Broad engine compatibility limits application change (+12); Managed operations remove patching and backup toil (+8) |
| retain-on-premises | rejected | 30.0 | Scored 30 against 75 for azure-sql-database. Retaining the workload leaves every current risk in place (-20) |
| sql-server-on-azure-vm | rejected | 42.0 | Scored 42 against 75 for azure-sql-database. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10) |

#### Why the alternatives were not chosen

- **azure-arc-enabled-sql-server** — Scored 40 against 75 for azure-sql-database. Evidence is already sufficient to choose a destination, so a bridge adds a step without adding information (-15); Governance and security posture improve without moving the workload (+5); Arc enablement is a bridge, not a completed modernization; the workload has not moved.
- **azure-sql-database-hyperscale** — Scored 30 against 75 for azure-sql-database. Neither size nor growth justifies Hyperscale; choosing it here would add capability nobody asked for (-25); Managed operations remove patching and backup toil (+5).
- **azure-sql-managed-instance** — Scored 65 against 75 for azure-sql-database. No instance-scoped dependency was found, so instance scope is more surface area than this workload needs (-5); Broad engine compatibility limits application change (+12); Managed operations remove patching and backup toil (+8).
- **retain-on-premises** — Scored 30 against 75 for azure-sql-database. Retaining the workload leaves every current risk in place (-20).
- **sql-server-on-azure-vm** — Scored 42 against 75 for azure-sql-database. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10).

#### Compatibility

- No compatibility obstacle was found in the available evidence.

#### Operations

- Platform-managed patching, backup, and high availability reduce operational load.
- Monitoring and alerting still need to be configured and owned.

#### Security

- Private network access, managed identity, and encryption in transit and at rest are landing-zone requirements and are checked separately.
- In scope for GDPR; control evidence must be collected during validation.

#### Performance

- Sizing is based on measured figures; target sizing must still be validated against a baseline comparison after migration.

#### Data residency

- Data residency requirement recorded as uk-south.

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

- Evidence: ev-csv-inventory-wl-case-management-invento-63b6a2aa
- Assumptions: none recorded.

### Customer master (`wl-customer-master`)

| | |
| --- | --- |
| Recommended target | **azure-sql-database** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Azure-sql-database scored highest (75) for Customer master on the published comparison. No instance-scoped dependencies, so database-level isolation fits (+15); Managed operations remove patching and backup toil (+10). This is a recommendation and requires architecture review before it becomes a decision.

#### Options considered

| Target | Verdict | Score | Reasoning |
| --- | --- | --- | --- |
| azure-arc-enabled-sql-server | rejected | 40.0 | Scored 40 against 75 for azure-sql-database. Evidence is already sufficient to choose a destination, so a bridge adds a step without adding information (-15); Governance and security posture improve without moving the workload (+5); Arc enablement is a bridge, not a completed modernization; the workload has not moved |
| azure-sql-database | recommended | 75.0 | No instance-scoped dependencies, so database-level isolation fits (+15); Managed operations remove patching and backup toil (+10) |
| azure-sql-database-hyperscale | rejected | 30.0 | Scored 30 against 75 for azure-sql-database. Neither size nor growth justifies Hyperscale; choosing it here would add capability nobody asked for (-25); Managed operations remove patching and backup toil (+5) |
| azure-sql-managed-instance | rejected | 65.0 | Scored 65 against 75 for azure-sql-database. No instance-scoped dependency was found, so instance scope is more surface area than this workload needs (-5); Broad engine compatibility limits application change (+12); Managed operations remove patching and backup toil (+8) |
| retain-on-premises | rejected | 30.0 | Scored 30 against 75 for azure-sql-database. Retaining the workload leaves every current risk in place (-20) |
| sql-server-on-azure-vm | rejected | 37.0 | Scored 37 against 75 for azure-sql-database. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10); Availability design remains the customer's responsibility on infrastructure (-5) |

#### Why the alternatives were not chosen

- **azure-arc-enabled-sql-server** — Scored 40 against 75 for azure-sql-database. Evidence is already sufficient to choose a destination, so a bridge adds a step without adding information (-15); Governance and security posture improve without moving the workload (+5); Arc enablement is a bridge, not a completed modernization; the workload has not moved.
- **azure-sql-database-hyperscale** — Scored 30 against 75 for azure-sql-database. Neither size nor growth justifies Hyperscale; choosing it here would add capability nobody asked for (-25); Managed operations remove patching and backup toil (+5).
- **azure-sql-managed-instance** — Scored 65 against 75 for azure-sql-database. No instance-scoped dependency was found, so instance scope is more surface area than this workload needs (-5); Broad engine compatibility limits application change (+12); Managed operations remove patching and backup toil (+8).
- **retain-on-premises** — Scored 30 against 75 for azure-sql-database. Retaining the workload leaves every current risk in place (-20).
- **sql-server-on-azure-vm** — Scored 37 against 75 for azure-sql-database. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10); Availability design remains the customer's responsibility on infrastructure (-5).

#### Compatibility

- No compatibility obstacle was found in the available evidence.

#### Operations

- Platform-managed patching, backup, and high availability reduce operational load.
- Monitoring and alerting still need to be configured and owned.

#### Security

- Private network access, managed identity, and encryption in transit and at rest are landing-zone requirements and are checked separately.
- In scope for GDPR; control evidence must be collected during validation.

#### Performance

- Sizing is based on measured figures; target sizing must still be validated against a baseline comparison after migration.

#### Data residency

- Data residency requirement recorded as uk-south.

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

- Evidence: ev-csv-inventory-wl-customer-master-invento-9768c3a2
- Assumptions: none recorded.

### Reporting copy (`wl-reporting-copy`)

| | |
| --- | --- |
| Recommended target | **azure-sql-database** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Azure-sql-database scored highest (75) for Reporting copy on the published comparison. No instance-scoped dependencies, so database-level isolation fits (+15); Managed operations remove patching and backup toil (+10). This is a recommendation and requires architecture review before it becomes a decision.

#### Options considered

| Target | Verdict | Score | Reasoning |
| --- | --- | --- | --- |
| azure-arc-enabled-sql-server | rejected | 40.0 | Scored 40 against 75 for azure-sql-database. Evidence is already sufficient to choose a destination, so a bridge adds a step without adding information (-15); Governance and security posture improve without moving the workload (+5); Arc enablement is a bridge, not a completed modernization; the workload has not moved |
| azure-sql-database | recommended | 75.0 | No instance-scoped dependencies, so database-level isolation fits (+15); Managed operations remove patching and backup toil (+10) |
| azure-sql-database-hyperscale | rejected | 30.0 | Scored 30 against 75 for azure-sql-database. Neither size nor growth justifies Hyperscale; choosing it here would add capability nobody asked for (-25); Managed operations remove patching and backup toil (+5) |
| azure-sql-managed-instance | rejected | 65.0 | Scored 65 against 75 for azure-sql-database. No instance-scoped dependency was found, so instance scope is more surface area than this workload needs (-5); Broad engine compatibility limits application change (+12); Managed operations remove patching and backup toil (+8) |
| retain-on-premises | rejected | 30.0 | Scored 30 against 75 for azure-sql-database. Retaining the workload leaves every current risk in place (-20) |
| sql-server-on-azure-vm | rejected | 42.0 | Scored 42 against 75 for azure-sql-database. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10) |

#### Why the alternatives were not chosen

- **azure-arc-enabled-sql-server** — Scored 40 against 75 for azure-sql-database. Evidence is already sufficient to choose a destination, so a bridge adds a step without adding information (-15); Governance and security posture improve without moving the workload (+5); Arc enablement is a bridge, not a completed modernization; the workload has not moved.
- **azure-sql-database-hyperscale** — Scored 30 against 75 for azure-sql-database. Neither size nor growth justifies Hyperscale; choosing it here would add capability nobody asked for (-25); Managed operations remove patching and backup toil (+5).
- **azure-sql-managed-instance** — Scored 65 against 75 for azure-sql-database. No instance-scoped dependency was found, so instance scope is more surface area than this workload needs (-5); Broad engine compatibility limits application change (+12); Managed operations remove patching and backup toil (+8).
- **retain-on-premises** — Scored 30 against 75 for azure-sql-database. Retaining the workload leaves every current risk in place (-20).
- **sql-server-on-azure-vm** — Scored 42 against 75 for azure-sql-database. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10).

#### Compatibility

- No compatibility obstacle was found in the available evidence.

#### Operations

- Platform-managed patching, backup, and high availability reduce operational load.
- Monitoring and alerting still need to be configured and owned.

#### Security

- Private network access, managed identity, and encryption in transit and at rest are landing-zone requirements and are checked separately.

#### Performance

- Sizing is based on measured figures; target sizing must still be validated against a baseline comparison after migration.

#### Data residency

- Data residency requirement recorded as uk-south.

#### Application impact

- No application change is implied by the target itself.
- Connection strings, retry logic, and driver versions must be reviewed.

#### Downtime approach

| | |
| --- | --- |
| Method | Continuous replication with a planned application cutover window. |
| Expected class | `short-planned` |
| Basis | A budget of 480 minutes has been stated. The class stays short-planned until a rehearsal measures the actual window. |
| Measured | No |

The downtime class is provisional. It stays provisional until a rehearsal produces a
measured figure; no stronger claim is available before then.

#### Cost inputs

No cost inputs were supplied. The repository does not invent cost figures; the business
case needs them from the customer or the account team.

#### Evidence and assumptions

- Evidence: ev-csv-inventory-wl-reporting-copy-inventor-dceef091
- Assumptions: none recorded.


> Reference tables were last verified on 2026-09-15. Support status, service capabilities, and limits change. Revalidate against current product documentation before presenting any conclusion drawn from them to a customer.
