# Target decisions — litware-manufacturing

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-litware-manufacturing-fy27` |
| As at | 2026-06-08 |
| Recommendations | 3 |
| Workloads with no recommendation | 0 |

Every entry below is a **recommendation**, not a decision. It becomes a decision when an
architecture review records an approval against it, and the approver cannot be the author.

## Workloads with no recommendation

Every workload received a recommendation.

## Recommendations

### Finance ledger (`wl-finance-ledger`)

| | |
| --- | --- |
| Recommended target | **azure-sql-managed-instance** |
| Disposition | refactor |
| Status | recommended |
| Confidence | medium |
| Requires application change | Yes |
| Requires schema or code conversion | Yes |

Azure-sql-managed-instance scored highest (45) for Finance ledger on the published comparison. Conversion assessment exists for this target, so the scale of the change is known (+10); Converted code requires application remediation and business validation before it can be trusted (-15); Automatic compatibility is not claimed; conversion percentages describe tool output only. This is a recommendation and requires architecture review before it becomes a decision.

#### Options considered

| Target | Verdict | Score | Reasoning |
| --- | --- | --- | --- |
| azure-database-for-postgresql-flexible-server | blocked | 0.0 | Blocked: Conversion was assessed against azure-sql-managed-instance, not against azure-database-for-postgresql-flexible-server. A conversion result does not transfer between destinations. |
| azure-sql-database | blocked | 0.0 | Blocked: Conversion was assessed against azure-sql-managed-instance, not against azure-sql-database. A conversion result does not transfer between destinations. |
| azure-sql-managed-instance | recommended | 45.0 | Conversion assessment exists for this target, so the scale of the change is known (+10); Converted code requires application remediation and business validation before it can be trusted (-15); Automatic compatibility is not claimed; conversion percentages describe tool output only |
| oracle-database-at-azure | rejected | 40.0 | Scored 40 against 45 for azure-sql-managed-instance. A conversion assessment exists, so the engagement has invested in leaving the engine; keeping it retains the licence position that investment is meant to change, and is recorded as the fallback (-15); Oracle-managed infrastructure removes patching and hardware toil (+10); Commercial terms, regional availability, and licence entitlement are unverified inputs that the account team must supply with a date (-10); Engine-native availability features remain available for a critical workload (+5); This keeps the estate on Oracle; it is a relocation and a licensing decision, not a modernization of the engine |
| replace-with-saas | blocked | 0.0 | Blocked: Conversion was assessed against azure-sql-managed-instance, not against replace-with-saas. A conversion result does not transfer between destinations. |
| retain-on-premises | rejected | 30.0 | Scored 30 against 45 for azure-sql-managed-instance. Retaining the workload leaves every current risk in place (-20) |
| self-managed-on-azure-vm | rejected | 37.0 | Scored 37 against 45 for azure-sql-managed-instance. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10); Availability design remains the customer's responsibility on infrastructure (-5) |

#### Why the alternatives were not chosen

- **azure-database-for-postgresql-flexible-server** — Blocked: Conversion was assessed against azure-sql-managed-instance, not against azure-database-for-postgresql-flexible-server. A conversion result does not transfer between destinations.
  - Blockers: Conversion was assessed against azure-sql-managed-instance, not against azure-database-for-postgresql-flexible-server. A conversion result does not transfer between destinations.
- **azure-sql-database** — Blocked: Conversion was assessed against azure-sql-managed-instance, not against azure-sql-database. A conversion result does not transfer between destinations.
  - Blockers: Conversion was assessed against azure-sql-managed-instance, not against azure-sql-database. A conversion result does not transfer between destinations.
- **oracle-database-at-azure** — Scored 40 against 45 for azure-sql-managed-instance. A conversion assessment exists, so the engagement has invested in leaving the engine; keeping it retains the licence position that investment is meant to change, and is recorded as the fallback (-15); Oracle-managed infrastructure removes patching and hardware toil (+10); Commercial terms, regional availability, and licence entitlement are unverified inputs that the account team must supply with a date (-10); Engine-native availability features remain available for a critical workload (+5); This keeps the estate on Oracle; it is a relocation and a licensing decision, not a modernization of the engine.
- **replace-with-saas** — Blocked: Conversion was assessed against azure-sql-managed-instance, not against replace-with-saas. A conversion result does not transfer between destinations.
  - Blockers: Conversion was assessed against azure-sql-managed-instance, not against replace-with-saas. A conversion result does not transfer between destinations.
- **retain-on-premises** — Scored 30 against 45 for azure-sql-managed-instance. Retaining the workload leaves every current risk in place (-20).
- **self-managed-on-azure-vm** — Scored 37 against 45 for azure-sql-managed-instance. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10); Availability design remains the customer's responsibility on infrastructure (-5).

#### Compatibility

- Schema and code conversion is required. Conversion tooling output is not a compatibility verdict; the application must be re-tested.

#### Operations

- Platform-managed patching, backup, and high availability reduce operational load.
- Monitoring and alerting still need to be configured and owned.

#### Security

- Private network access, managed identity, and encryption in transit and at rest are landing-zone requirements and are checked separately.
- In scope for SOX; control evidence must be collected during validation.

#### Performance

- Sizing is based on measured figures; target sizing must still be validated against a baseline comparison after migration.

#### Data residency

- Data residency requirement recorded as us-east.

#### Application impact

- The application must change before it can use this target.
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

- Evidence: ev-csv-inventory-wl-finance-ledger-inventor-53689ee7, ev-ssma-wl-finance-ledger-ssma-conversion-j-5a905ec4
- Assumptions: none recorded.

### Order management (`wl-order-management`)

| | |
| --- | --- |
| Recommended target | **azure-database-for-postgresql-flexible-server** |
| Disposition | refactor |
| Status | recommended |
| Confidence | medium |
| Requires application change | Yes |
| Requires schema or code conversion | Yes |

Azure-database-for-postgresql-flexible-server scored highest (45) for Order management on the published comparison. Conversion assessment exists for this target, so the scale of the change is known (+10); Converted code requires application remediation and business validation before it can be trusted (-15); Automatic compatibility is not claimed; conversion percentages describe tool output only. This is a recommendation and requires architecture review before it becomes a decision.

#### Options considered

| Target | Verdict | Score | Reasoning |
| --- | --- | --- | --- |
| azure-database-for-postgresql-flexible-server | recommended | 45.0 | Conversion assessment exists for this target, so the scale of the change is known (+10); Converted code requires application remediation and business validation before it can be trusted (-15); Automatic compatibility is not claimed; conversion percentages describe tool output only |
| azure-sql-database | blocked | 0.0 | Blocked: Conversion was assessed against azure-database-for-postgresql-flexible-server, not against azure-sql-database. A conversion result does not transfer between destinations. |
| azure-sql-managed-instance | blocked | 0.0 | Blocked: Conversion was assessed against azure-database-for-postgresql-flexible-server, not against azure-sql-managed-instance. A conversion result does not transfer between destinations. |
| oracle-database-at-azure | rejected | 35.0 | Scored 35 against 45 for azure-database-for-postgresql-flexible-server. A conversion assessment exists, so the engagement has invested in leaving the engine; keeping it retains the licence position that investment is meant to change, and is recorded as the fallback (-15); Oracle-managed infrastructure removes patching and hardware toil (+10); Commercial terms, regional availability, and licence entitlement are unverified inputs that the account team must supply with a date (-10); This keeps the estate on Oracle; it is a relocation and a licensing decision, not a modernization of the engine |
| replace-with-saas | blocked | 0.0 | Blocked: Conversion was assessed against azure-database-for-postgresql-flexible-server, not against replace-with-saas. A conversion result does not transfer between destinations. |
| retain-on-premises | rejected | 30.0 | Scored 30 against 45 for azure-database-for-postgresql-flexible-server. Retaining the workload leaves every current risk in place (-20) |
| self-managed-on-azure-vm | rejected | 42.0 | Scored 42 against 45 for azure-database-for-postgresql-flexible-server. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10) |

#### Why the alternatives were not chosen

- **azure-sql-database** — Blocked: Conversion was assessed against azure-database-for-postgresql-flexible-server, not against azure-sql-database. A conversion result does not transfer between destinations.
  - Blockers: Conversion was assessed against azure-database-for-postgresql-flexible-server, not against azure-sql-database. A conversion result does not transfer between destinations.
- **azure-sql-managed-instance** — Blocked: Conversion was assessed against azure-database-for-postgresql-flexible-server, not against azure-sql-managed-instance. A conversion result does not transfer between destinations.
  - Blockers: Conversion was assessed against azure-database-for-postgresql-flexible-server, not against azure-sql-managed-instance. A conversion result does not transfer between destinations.
- **oracle-database-at-azure** — Scored 35 against 45 for azure-database-for-postgresql-flexible-server. A conversion assessment exists, so the engagement has invested in leaving the engine; keeping it retains the licence position that investment is meant to change, and is recorded as the fallback (-15); Oracle-managed infrastructure removes patching and hardware toil (+10); Commercial terms, regional availability, and licence entitlement are unverified inputs that the account team must supply with a date (-10); This keeps the estate on Oracle; it is a relocation and a licensing decision, not a modernization of the engine.
- **replace-with-saas** — Blocked: Conversion was assessed against azure-database-for-postgresql-flexible-server, not against replace-with-saas. A conversion result does not transfer between destinations.
  - Blockers: Conversion was assessed against azure-database-for-postgresql-flexible-server, not against replace-with-saas. A conversion result does not transfer between destinations.
- **retain-on-premises** — Scored 30 against 45 for azure-database-for-postgresql-flexible-server. Retaining the workload leaves every current risk in place (-20).
- **self-managed-on-azure-vm** — Scored 42 against 45 for azure-database-for-postgresql-flexible-server. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10).

#### Compatibility

- Schema and code conversion is required. Conversion tooling output is not a compatibility verdict; the application must be re-tested.

#### Operations

- Platform-managed patching, backup, and high availability reduce operational load.
- Monitoring and alerting still need to be configured and owned.

#### Security

- Private network access, managed identity, and encryption in transit and at rest are landing-zone requirements and are checked separately.

#### Performance

- Sizing is based on measured figures; target sizing must still be validated against a baseline comparison after migration.

#### Data residency

- Data residency requirement recorded as us-east.

#### Application impact

- The application must change before it can use this target.
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

- Evidence: ev-csv-inventory-wl-order-management-invent-6a4e1f19, ev-ssma-wl-order-management-ssma-conversion-cad17b4a
- Assumptions: none recorded.

### Plant maintenance (`wl-plant-maintenance`)

| | |
| --- | --- |
| Recommended target | **oracle-database-at-azure** |
| Disposition | replatform |
| Status | recommended |
| Confidence | medium |
| Requires application change | No |
| Requires schema or code conversion | No |

Oracle-database-at-azure scored highest (70) for Plant maintenance on the published comparison. No conversion assessment exists, so no cross-engine destination can be recommended; keeping the engine removes the hardware and support risk without claiming a compatibility nobody has demonstrated (+20); Oracle-managed infrastructure removes patching and hardware toil (+10); Commercial terms, regional availability, and licence entitlement are unverified inputs that the account team must supply with a date (-10); This keeps the estate on Oracle; it is a relocation and a licensing decision, not a modernization of the engine. This is a recommendation and requires architecture review before it becomes a decision.

#### Options considered

| Target | Verdict | Score | Reasoning |
| --- | --- | --- | --- |
| azure-database-for-postgresql-flexible-server | blocked | 0.0 | Blocked: No schema or code conversion assessment is present. Compatibility across engine families is never assumed; it is demonstrated per schema. |
| azure-sql-database | blocked | 0.0 | Blocked: No schema or code conversion assessment is present. Compatibility across engine families is never assumed; it is demonstrated per schema. |
| azure-sql-managed-instance | blocked | 0.0 | Blocked: No schema or code conversion assessment is present. Compatibility across engine families is never assumed; it is demonstrated per schema. |
| oracle-database-at-azure | recommended | 70.0 | No conversion assessment exists, so no cross-engine destination can be recommended; keeping the engine removes the hardware and support risk without claiming a compatibility nobody has demonstrated (+20); Oracle-managed infrastructure removes patching and hardware toil (+10); Commercial terms, regional availability, and licence entitlement are unverified inputs that the account team must supply with a date (-10); This keeps the estate on Oracle; it is a relocation and a licensing decision, not a modernization of the engine |
| replace-with-saas | blocked | 0.0 | Blocked: No schema or code conversion assessment is present. Compatibility across engine families is never assumed; it is demonstrated per schema. |
| retain-on-premises | rejected | 30.0 | Scored 30 against 70 for oracle-database-at-azure. Retaining the workload leaves every current risk in place (-20) |
| self-managed-on-azure-vm | rejected | 42.0 | Scored 42 against 70 for oracle-database-at-azure. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10) |

#### Why the alternatives were not chosen

- **azure-database-for-postgresql-flexible-server** — Blocked: No schema or code conversion assessment is present. Compatibility across engine families is never assumed; it is demonstrated per schema.
  - Blockers: No schema or code conversion assessment is present. Compatibility across engine families is never assumed; it is demonstrated per schema.
- **azure-sql-database** — Blocked: No schema or code conversion assessment is present. Compatibility across engine families is never assumed; it is demonstrated per schema.
  - Blockers: No schema or code conversion assessment is present. Compatibility across engine families is never assumed; it is demonstrated per schema.
- **azure-sql-managed-instance** — Blocked: No schema or code conversion assessment is present. Compatibility across engine families is never assumed; it is demonstrated per schema.
  - Blockers: No schema or code conversion assessment is present. Compatibility across engine families is never assumed; it is demonstrated per schema.
- **replace-with-saas** — Blocked: No schema or code conversion assessment is present. Compatibility across engine families is never assumed; it is demonstrated per schema.
  - Blockers: No schema or code conversion assessment is present. Compatibility across engine families is never assumed; it is demonstrated per schema.
- **retain-on-premises** — Scored 30 against 70 for oracle-database-at-azure. Retaining the workload leaves every current risk in place (-20).
- **self-managed-on-azure-vm** — Scored 42 against 70 for oracle-database-at-azure. No operating-system dependency was found, so this target keeps patching and backup responsibility without a reason (-18); Full engine control preserves third-party application support (+10).

#### Compatibility

- No compatibility obstacle was found in the available evidence.

#### Operations

- Infrastructure and engine patching are Oracle-managed; database administration, licensing, and the Oracle support relationship remain the customer's.
- Regional availability, private-offer terms, and licence entitlement must be confirmed with the account team and recorded with a date before commitment.

#### Security

- Private network access, managed identity, and encryption in transit and at rest are landing-zone requirements and are checked separately.

#### Performance

- Sizing is based on measured figures; target sizing must still be validated against a baseline comparison after migration.

#### Data residency

- Data residency requirement recorded as us-east.

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

- Evidence: ev-csv-inventory-wl-plant-maintenance-inven-5ce4310b
- Assumptions: none recorded.


> Reference tables were last verified on 2026-09-16. Support status, service capabilities, and limits change. Revalidate against current product documentation before presenting any conclusion drawn from them to a customer.
