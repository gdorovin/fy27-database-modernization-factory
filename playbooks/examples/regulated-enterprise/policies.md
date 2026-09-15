# Regulated enterprise playbook — policies

The default policy set, plus the controls a supervised estate needs. Where a policy here
shares a subject with the default, it is stricter rather than contradictory — a
contradiction would fail validation, which is the intended behaviour.

## Policies

| ID | Category | Subject | Directive | Requirement | Applies to |
| --- | --- | --- | --- | --- | --- |
| SEC-001 | security | network.public-endpoint | prohibited | Database endpoints are not reachable from the public internet, in any environment including development. | all |
| SEC-002 | security | data.encryption-at-rest | required | Encryption at rest is enabled, with key management evidenced. | all |
| SEC-003 | security | data.encryption-in-transit | required | Connections enforce encryption in transit with an explicitly set minimum protocol version. | all |
| SEC-004 | security | secrets.storage | required | Secrets are held in a managed secret store with access logged and reviewed. | all |
| SEC-005 | security | posture.baseline | required | A posture baseline is recorded before migration, so any new finding afterwards is attributable. | all |
| SEC-006 | security | security.penetration-test | required | A penetration test covering the new access path is completed before production acceptance. | production |
| IAM-001 | identity | auth.method | required | Applications authenticate with a managed or directory identity. Shared logins require a compliance-approved exception. | all |
| IAM-002 | identity | auth.least-privilege | required | Every principal holds the minimum privilege its documented role needs, and the mapping is reviewed quarterly. | all |
| IAM-003 | identity | auth.break-glass | required | A break-glass account exists, is monitored, and its use raises an alert to the security owner within the hour. | all |
| IAM-004 | identity | auth.segregation | required | The principal that proposes a change may not be the principal that approves it, and the trail shows both. | all |
| NET-001 | networking | network.private-endpoint | required | Private connectivity for all database access from application tiers. | all |
| NET-002 | networking | network.name-resolution | required | Private name resolution is configured and tested from the application subnet before cutover. | all |
| NET-003 | networking | network.segmentation | required | Network rules permit only documented application tiers and administrative paths. | all |
| NET-004 | networking | network.egress | required | Outbound access from the data tier is restricted and logged. | all |
| DATA-001 | data | data.classification | required | Every workload carries a classification agreed with the compliance officer before migration. | all |
| DATA-002 | data | data.residency | required | Residency requirements block any target that cannot satisfy them. Residency is never weighed against cost or convenience. | all |
| DATA-003 | data | data.reconciliation | required | Row counts and checksums reconcile, and the reconciliation output is retained as audit evidence. | all |
| DATA-004 | data | data.customer-evidence | prohibited | Real customer exports and personal data are never committed to a repository. Evidence is referenced by manifest. | all |
| DATA-005 | data | data.retention | required | Retention and deletion obligations propagate to every derived copy, index, and backup. | all |
| OBS-001 | observability | monitoring.alerting | required | Monitoring and alerting are live, routed to a named owner, and tested with a real alert. | all |
| OBS-002 | observability | monitoring.diagnostics | required | Diagnostic and audit logs reach a retained sink, with retention meeting the supervisory minimum. | all |
| OBS-003 | observability | monitoring.baseline-comparison | required | A source baseline exists and the post-migration comparison is retained. | all |
| OBS-004 | observability | monitoring.audit-immutability | required | Audit logs are protected against modification by the operators of the system they describe. | all |
| AVL-001 | availability | availability.rpo-rto | required | RPO and RTO are stated by the business owner and agreed with the compliance officer. | all |
| AVL-002 | availability | availability.failover-test | required | Failover is tested and the recovery time measured, at least annually. | all |
| AVL-003 | availability | availability.backup-restore | required | A restore is performed and verified before production acceptance, and annually thereafter. | all |
| AVL-004 | availability | availability.downtime-claim | prohibited | Zero-downtime claims are not made. "Near-zero planned downtime" requires a measured rehearsal and a named method. | all |
| VAL-001 | validation | validation.blocking-checks | required | Every blocking validation check has a recorded observation before a go decision. | all |
| VAL-002 | validation | validation.generated-tests | prohibited | Generated tests alone are not accepted as migration proof. | all |
| VAL-003 | validation | validation.rollback-rehearsal | required | The rollback path is rehearsed and the duration measured before cutover. | all |
| VAL-004 | validation | validation.business-acceptance | required | Business and application owners accept the outcome before a wave is closed. | all |
| VAL-005 | validation | validation.evidence-retention | required | Validation evidence is retained for the supervisory retention period, not the project's. | all |
| OPS-001 | operations | operations.runbook | required | An operational runbook exists and has been walked through with the operations owner. | all |
| OPS-002 | operations | operations.change-approval | required | Any environment-changing action carries a recorded approval, a what-if or dry run first, and a documented rollback. | all |
| OPS-003 | operations | operations.decommission | prohibited | Source systems are not decommissioned until hypercare completes, acceptance is recorded, and the retention decision is settled. | all |
| COMP-001 | compliance | compliance.control-evidence | required | Control evidence is collected during validation, not reconstructed afterwards. | all |
| COMP-002 | compliance | compliance.product-claims | required | Support status, limits, preview state, and commercial terms are dated references, revalidated before use. | all |
| COMP-003 | compliance | compliance.supervisory-notification | required | Material changes to a supervised system are notified per the applicable regime, before cutover. | production |
| NAME-001 | naming | naming.convention | required | Resource names follow the agreed convention and carry environment and workload identifiers. | all |
| COST-001 | cost | cost.sizing-basis | required | Any cost or capacity commitment names the measured basis it rests on. | all |

## Exceptions

An exception here additionally requires the compliance officer, and the ceiling is 90 days.
There are none open.

| ID | Policy ID | Scope | Justification | Owner role | Approver role | Approver principal | Compensating controls | Granted on | Expires on | Review on |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
