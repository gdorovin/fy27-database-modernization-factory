# Target decisions — fabrikam-saas

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-fabrikam-saas-fy27` |
| As at | 2026-04-13 |
| Recommendations | 4 |
| Workloads with no recommendation | 0 |

Every entry below is a **recommendation**, not a decision. It becomes a decision when an
architecture review records an approval against it, and the approver cannot be the author.

## Workloads with no recommendation

Every workload received a recommendation.

## Recommendations

### Product core (`wl-product-core`)

| | |
| --- | --- |
| Recommended target | **azure-sql-database** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Azure-sql-database scored highest (75) for Product core on the published comparison. No instance-scoped dependencies, so database-level isolation fits (+15); Managed operations remove patching and backup toil (+10). This is a recommendation and requires architecture review before it becomes a decision.

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
| Basis | A budget of 60 minutes has been stated. The class stays short-planned until a rehearsal measures the actual window. |
| Measured | No |

The downtime class is provisional. It stays provisional until a rehearsal produces a
measured figure; no stronger claim is available before then.

#### Cost inputs

No cost inputs were supplied. The repository does not invent cost figures; the business
case needs them from the customer or the account team.

#### Evidence and assumptions

- Evidence: ev-csv-inventory-wl-product-core-inventory--d7dab8f7
- Assumptions: none recorded.

### Product events (`wl-product-events`)

| | |
| --- | --- |
| Recommended target | **azure-sql-database-hyperscale** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Azure-sql-database-hyperscale scored highest (90) for Product events on the published comparison. Data size 2400 GB is in the range Hyperscale exists to serve (+20); Stated growth of 65% per year favours elastic storage (+15); Managed operations remove patching and backup toil (+5). This is a recommendation and requires architecture review before it becomes a decision.

#### Options considered

| Target | Verdict | Score | Reasoning |
| --- | --- | --- | --- |
| azure-arc-enabled-sql-server | rejected | 40.0 | Scored 40 against 90 for azure-sql-database-hyperscale. Evidence is already sufficient to choose a destination, so a bridge adds a step without adding information (-15); Governance and security posture improve without moving the workload (+5); Arc enablement is a bridge, not a completed modernization; the workload has not moved |
| azure-sql-database | rejected | 45.0 | Scored 45 against 90 for azure-sql-database-hyperscale. No instance-scoped dependencies, so database-level isolation fits (+15); Managed operations remove patching and backup toil (+10); Data size 2400 GB is above the point where Hyperscale is the fairer comparison (-20); Stated growth of 65% per year strains a fixed-size tier (-10) |
| azure-sql-database-hyperscale | recommended | 90.0 | Data size 2400 GB is in the range Hyperscale exists to serve (+20); Stated growth of 65% per year favours elastic storage (+15); Managed operations remove patching and backup toil (+5) |
| azure-sql-managed-instance | rejected | 65.0 | Scored 65 against 90 for azure-sql-database-hyperscale. No instance-scoped dependency was found, so instance scope is more surface area than this workload needs (-5); Broad engine compatibility limits application change (+12); Managed operations remove patching and backup toil (+8) |
| retain-on-premises | rejected | 30.0 | Scored 30 against 90 for azure-sql-database-hyperscale. Retaining the workload leaves every current risk in place (-20) |
| sql-server-on-azure-vm | rejected | 42.0 | Scored 42 against 90 for azure-sql-database-hyperscale. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10) |

#### Why the alternatives were not chosen

- **azure-arc-enabled-sql-server** — Scored 40 against 90 for azure-sql-database-hyperscale. Evidence is already sufficient to choose a destination, so a bridge adds a step without adding information (-15); Governance and security posture improve without moving the workload (+5); Arc enablement is a bridge, not a completed modernization; the workload has not moved.
- **azure-sql-database** — Scored 45 against 90 for azure-sql-database-hyperscale. No instance-scoped dependencies, so database-level isolation fits (+15); Managed operations remove patching and backup toil (+10); Data size 2400 GB is above the point where Hyperscale is the fairer comparison (-20); Stated growth of 65% per year strains a fixed-size tier (-10).
- **azure-sql-managed-instance** — Scored 65 against 90 for azure-sql-database-hyperscale. No instance-scoped dependency was found, so instance scope is more surface area than this workload needs (-5); Broad engine compatibility limits application change (+12); Managed operations remove patching and backup toil (+8).
- **retain-on-premises** — Scored 30 against 90 for azure-sql-database-hyperscale. Retaining the workload leaves every current risk in place (-20).
- **sql-server-on-azure-vm** — Scored 42 against 90 for azure-sql-database-hyperscale. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10).

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
| Basis | A budget of 120 minutes has been stated. The class stays short-planned until a rehearsal measures the actual window. |
| Measured | No |

The downtime class is provisional. It stays provisional until a rehearsal produces a
measured figure; no stronger claim is available before then.

#### Cost inputs

No cost inputs were supplied. The repository does not invent cost figures; the business
case needs them from the customer or the account team.

#### Evidence and assumptions

- Evidence: ev-csv-inventory-wl-product-events-inventor-d0657a84
- Assumptions: none recorded.

### Product staging (`wl-product-staging`)

| | |
| --- | --- |
| Recommended target | **azure-sql-database** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Azure-sql-database scored highest (75) for Product staging on the published comparison. No instance-scoped dependencies, so database-level isolation fits (+15); Managed operations remove patching and backup toil (+10). This is a recommendation and requires architecture review before it becomes a decision.

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

- Evidence: ev-csv-inventory-wl-product-staging-invento-b829061d
- Assumptions: none recorded.

### Tenant metadata (`wl-tenant-metadata`)

| | |
| --- | --- |
| Recommended target | **azure-sql-database** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Azure-sql-database scored highest (75) for Tenant metadata on the published comparison. No instance-scoped dependencies, so database-level isolation fits (+15); Managed operations remove patching and backup toil (+10). This is a recommendation and requires architecture review before it becomes a decision.

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
| Basis | A budget of 60 minutes has been stated. The class stays short-planned until a rehearsal measures the actual window. |
| Measured | No |

The downtime class is provisional. It stays provisional until a rehearsal produces a
measured figure; no stronger claim is available before then.

#### Cost inputs

No cost inputs were supplied. The repository does not invent cost figures; the business
case needs them from the customer or the account team.

#### Evidence and assumptions

- Evidence: ev-csv-inventory-wl-tenant-metadata-invento-82223d4e
- Assumptions: none recorded.


> Reference tables were last verified on 2026-09-15. Support status, service capabilities, and limits change. Revalidate against current product documentation before presenting any conclusion drawn from them to a customer.
