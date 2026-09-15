# Target decisions — northwind-retail

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-northwind-retail-fy27` |
| As at | 2026-03-02 |
| Recommendations | 4 |
| Workloads with no recommendation | 1 |

Every entry below is a **recommendation**, not a decision. It becomes a decision when an
architecture review records an approval against it, and the approver cannot be the author.

## Workloads with no recommendation

These workloads have open blocking findings. No target is proposed for them, because a
target chosen from incomplete evidence is a guess wearing a decision's clothes.

- `wl-store-operations` — Store operations

## Recommendations

### Customer portal (`wl-customer-portal`)

| | |
| --- | --- |
| Recommended target | **azure-sql-database** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Azure-sql-database scored highest (75) for Customer portal on the published comparison. No instance-scoped dependencies, so database-level isolation fits (+15); Managed operations remove patching and backup toil (+10). This is a recommendation and requires architecture review before it becomes a decision.

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

- Data residency requirement recorded as eu-west.

#### Application impact

- No application change is implied by the target itself.
- Connection strings, retry logic, and driver versions must be reviewed.

#### Downtime approach

| | |
| --- | --- |
| Method | Continuous replication with a planned application cutover window. |
| Expected class | `short-planned` |
| Basis | A budget of 240 minutes has been stated. The class stays short-planned until a rehearsal measures the actual window. |
| Measured | No |

The downtime class is provisional. It stays provisional until a rehearsal produces a
measured figure; no stronger claim is available before then.

#### Cost inputs

No cost inputs were supplied. The repository does not invent cost figures; the business
case needs them from the customer or the account team.

#### Evidence and assumptions

- Evidence: ev-csv-inventory-wl-customer-portal-invento-d137d37c
- Assumptions: none recorded.

### Payments core (`wl-payments-core`)

| | |
| --- | --- |
| Recommended target | **azure-sql-managed-instance** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Azure-sql-managed-instance scored highest (95) for Payments core on the published comparison. Instance-scoped features in use are available at instance scope: cross-database-queries, service-broker, sql-agent (+25); Broad engine compatibility limits application change (+12); Managed operations remove patching and backup toil (+8). This is a recommendation and requires architecture review before it becomes a decision.

#### Options considered

| Target | Verdict | Score | Reasoning |
| --- | --- | --- | --- |
| azure-arc-enabled-sql-server | rejected | 40.0 | Scored 40 against 95 for azure-sql-managed-instance. Evidence is already sufficient to choose a destination, so a bridge adds a step without adding information (-15); Governance and security posture improve without moving the workload (+5); Arc enablement is a bridge, not a completed modernization; the workload has not moved |
| azure-sql-database | blocked | 0.0 | Blocked: Instance-scoped features are in use and are not available at database scope: cross-database-queries, service-broker, sql-agent |
| azure-sql-database-hyperscale | blocked | 0.0 | Blocked: Instance-scoped features are in use and are not available at database scope: cross-database-queries, service-broker, sql-agent |
| azure-sql-managed-instance | recommended | 95.0 | Instance-scoped features in use are available at instance scope: cross-database-queries, service-broker, sql-agent (+25); Broad engine compatibility limits application change (+12); Managed operations remove patching and backup toil (+8) |
| retain-on-premises | rejected | 30.0 | Scored 30 against 95 for azure-sql-managed-instance. Retaining the workload leaves every current risk in place (-20) |
| sql-server-on-azure-vm | rejected | 37.0 | Scored 37 against 95 for azure-sql-managed-instance. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10); Availability design remains the customer's responsibility on infrastructure (-5) |

#### Why the alternatives were not chosen

- **azure-arc-enabled-sql-server** — Scored 40 against 95 for azure-sql-managed-instance. Evidence is already sufficient to choose a destination, so a bridge adds a step without adding information (-15); Governance and security posture improve without moving the workload (+5); Arc enablement is a bridge, not a completed modernization; the workload has not moved.
- **azure-sql-database** — Blocked: Instance-scoped features are in use and are not available at database scope: cross-database-queries, service-broker, sql-agent.
  - Blockers: Instance-scoped features are in use and are not available at database scope: cross-database-queries, service-broker, sql-agent
- **azure-sql-database-hyperscale** — Blocked: Instance-scoped features are in use and are not available at database scope: cross-database-queries, service-broker, sql-agent.
  - Blockers: Instance-scoped features are in use and are not available at database scope: cross-database-queries, service-broker, sql-agent
- **retain-on-premises** — Scored 30 against 95 for azure-sql-managed-instance. Retaining the workload leaves every current risk in place (-20).
- **sql-server-on-azure-vm** — Scored 37 against 95 for azure-sql-managed-instance. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10); Availability design remains the customer's responsibility on infrastructure (-5).

#### Compatibility

- Instance-scoped features observed in use: cross-database-queries, service-broker, sql-agent.

#### Operations

- Platform-managed patching, backup, and high availability reduce operational load.
- Monitoring and alerting still need to be configured and owned.

#### Security

- Private network access, managed identity, and encryption in transit and at rest are landing-zone requirements and are checked separately.
- In scope for PCI-DSS; control evidence must be collected during validation.

#### Performance

- Sizing is based on measured figures; target sizing must still be validated against a baseline comparison after migration.

#### Data residency

- Data residency requirement recorded as eu-west.

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

- Evidence: ev-arc-sql-wl-payments-core-arc-inventory-j-4e50fc1d, ev-csv-inventory-wl-payments-core-inventory-00ccb289
- Assumptions: none recorded.

### Reporting sandbox (`wl-reporting-sandbox`)

| | |
| --- | --- |
| Recommended target | **azure-sql-database** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Azure-sql-database scored highest (75) for Reporting sandbox on the published comparison. No instance-scoped dependencies, so database-level isolation fits (+15); Managed operations remove patching and backup toil (+10). This is a recommendation and requires architecture review before it becomes a decision.

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

- Data residency requirement recorded as eu-west.

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

- Evidence: ev-csv-inventory-wl-reporting-sandbox-inven-7d87e5a8
- Assumptions: none recorded.

### Store operations (`wl-store-operations`)

| | |
| --- | --- |
| Recommended target | **azure-arc-enabled-sql-server** |
| Disposition | retain |
| Status | recommended |
| Confidence | low |
| Requires application change | No |
| Requires schema or code conversion | No |

No destination can be recommended for Store operations while blocking evidence is open, so every migration target is blocked. azure-arc-enabled-sql-server is proposed as an interim posture only: it governs the workload where it stands and does not move it. It must not be recorded as completed modernization. Evidence is incomplete, and Arc gives continuous inventory, assessment, and governance while that is fixed (+25); Governance and security posture improve without moving the workload (+5); Arc enablement is a bridge, not a completed modernization; the workload has not moved.

#### Options considered

| Target | Verdict | Score | Reasoning |
| --- | --- | --- | --- |
| azure-arc-enabled-sql-server | recommended | 80.0 | Evidence is incomplete, and Arc gives continuous inventory, assessment, and governance while that is fixed (+25); Governance and security posture improve without moving the workload (+5); Arc enablement is a bridge, not a completed modernization; the workload has not moved |
| azure-sql-database | blocked | 0.0 | Cannot be recommended while blocking evidence is open. Choosing a destination now would commit the engagement to a decision the evidence does not support. |
| azure-sql-database-hyperscale | blocked | 0.0 | Cannot be recommended while blocking evidence is open. Choosing a destination now would commit the engagement to a decision the evidence does not support. |
| azure-sql-managed-instance | blocked | 0.0 | Cannot be recommended while blocking evidence is open. Choosing a destination now would commit the engagement to a decision the evidence does not support. |
| retain-on-premises | rejected | 40.0 | Scored 40 against 80 for azure-arc-enabled-sql-server. Retaining the workload leaves every current risk in place (-20); Open blocking findings mean any move would be made on incomplete evidence (+10) |
| sql-server-on-azure-vm | blocked | 0.0 | Cannot be recommended while blocking evidence is open. Choosing a destination now would commit the engagement to a decision the evidence does not support. |

#### Why the alternatives were not chosen

- **azure-sql-database** — Cannot be recommended while blocking evidence is open. Choosing a destination now would commit the engagement to a decision the evidence does not support.
  - Blockers: wl-store-operations-r-dependencies-unknown
- **azure-sql-database-hyperscale** — Cannot be recommended while blocking evidence is open. Choosing a destination now would commit the engagement to a decision the evidence does not support.
  - Blockers: wl-store-operations-r-dependencies-unknown
- **azure-sql-managed-instance** — Cannot be recommended while blocking evidence is open. Choosing a destination now would commit the engagement to a decision the evidence does not support.
  - Blockers: wl-store-operations-r-dependencies-unknown
- **retain-on-premises** — Scored 40 against 80 for azure-arc-enabled-sql-server. Retaining the workload leaves every current risk in place (-20); Open blocking findings mean any move would be made on incomplete evidence (+10).
- **sql-server-on-azure-vm** — Cannot be recommended while blocking evidence is open. Choosing a destination now would commit the engagement to a decision the evidence does not support.
  - Blockers: wl-store-operations-r-dependencies-unknown

#### Compatibility

- Instance-scoped features observed in use: sql-agent.

#### Operations

- The workload stays where it is. This delivers inventory, assessment, and governance, not modernization.
- A follow-on decision is still required for the destination.

#### Security

- Private network access, managed identity, and encryption in transit and at rest are landing-zone requirements and are checked separately.

#### Performance

- Sizing is based on measured figures; target sizing must still be validated against a baseline comparison after migration.

#### Data residency

- Data residency requirement recorded as eu-west.

#### Application impact

- No application change is implied by the target itself.
- Connection strings, retry logic, and driver versions must be reviewed.
- Dependency discovery is incomplete, so this impact assessment is provisional.

#### Downtime approach

| | |
| --- | --- |
| Method | To be selected once a planned-downtime budget is agreed. |
| Expected class | `unknown` |
| Basis | No planned-downtime budget has been agreed, so no method can be justified. |
| Measured | No |

The downtime class is provisional. It stays provisional until a rehearsal produces a
measured figure; no stronger claim is available before then.

#### Cost inputs

No cost inputs were supplied. The repository does not invent cost figures; the business
case needs them from the customer or the account team.

#### Evidence and assumptions

- Evidence: ev-arc-sql-wl-store-operations-arc-inventor-101d0af9, ev-csv-inventory-wl-store-operations-invent-65706cdf
- Assumptions: none recorded.
- Open questions:
  - Dependency discovery is incomplete, so the consumers of this database and the blast radius of a cutover are unknown. This must be resolved before a destination can be recommended. (owner: database-owner, blocking)


> Reference tables were last verified on 2026-09-15. Support status, service capabilities, and limits change. Revalidate against current product documentation before presenting any conclusion drawn from them to a customer.
