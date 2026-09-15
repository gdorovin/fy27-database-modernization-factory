# Renewal-led SQL playbook — policies

The default policy set, plus the few controls that stop time pressure from eroding the
standard of proof. Note what is *not* relaxed: every validation policy here is at least as
strict as the default, because the validation gate is the one thing a deadline must not be
allowed to move.

## Policies

| ID | Category | Subject | Directive | Requirement | Applies to |
| --- | --- | --- | --- | --- | --- |
| SEC-001 | security | network.public-endpoint | prohibited | Database endpoints are not reachable from the public internet. | all |
| SEC-002 | security | data.encryption-at-rest | required | Encryption at rest is enabled on every target. | all |
| SEC-003 | security | data.encryption-in-transit | required | Connections enforce encryption in transit with an explicit minimum protocol version. | all |
| SEC-004 | security | secrets.storage | required | Secrets are held in a managed secret store. | all |
| SEC-005 | security | posture.baseline | required | Posture reporting is enabled and a baseline recorded before migration. | all |
| IAM-001 | identity | auth.method | required | Applications authenticate with a managed or directory identity. | all |
| IAM-002 | identity | auth.least-privilege | required | Every principal holds the minimum privilege its role needs. | all |
| IAM-003 | identity | auth.break-glass | required | A break-glass account exists, is monitored, and its use raises an alert. | production |
| NET-001 | networking | network.private-endpoint | required | Private connectivity for database access from application tiers. | all |
| NET-002 | networking | network.name-resolution | required | Private name resolution is configured and tested before cutover. | all |
| NET-003 | networking | network.segmentation | required | Network rules permit only documented application tiers and administrative paths. | all |
| DATA-001 | data | data.classification | required | Every workload carries a data classification before migration. | all |
| DATA-002 | data | data.residency | required | Residency requirements block any target that cannot satisfy them. | all |
| DATA-003 | data | data.reconciliation | required | Row counts and checksums reconcile before cutover is considered complete. | all |
| DATA-004 | data | data.customer-evidence | prohibited | Real customer exports and personal data are never committed to a repository. | all |
| OBS-001 | observability | monitoring.alerting | required | Monitoring and alerting are live and routed to a named owner. | all |
| OBS-002 | observability | monitoring.diagnostics | required | Diagnostic and audit logs reach a retained sink, and delivery is verified. | all |
| OBS-003 | observability | monitoring.baseline-comparison | required | A source baseline exists and the post-migration comparison is recorded. | all |
| AVL-001 | availability | availability.rpo-rto | required | RPO and RTO are stated by the business owner before an availability design is chosen. | all |
| AVL-002 | availability | availability.failover-test | required | Failover is tested and the recovery time measured. | production |
| AVL-003 | availability | availability.backup-restore | required | A restore is performed and verified. | all |
| AVL-004 | availability | availability.downtime-claim | prohibited | Zero-downtime claims are not made. "Near-zero planned downtime" requires a measured rehearsal. | all |
| VAL-001 | validation | validation.blocking-checks | required | Every blocking check has a recorded observation before a go decision. Schedule pressure does not change this. | all |
| VAL-002 | validation | validation.generated-tests | prohibited | Generated tests alone are not accepted as migration proof. | all |
| VAL-003 | validation | validation.rollback-rehearsal | required | The rollback path is rehearsed and measured before cutover. | all |
| VAL-004 | validation | validation.business-acceptance | required | Business and application owners accept the outcome before a wave is closed. | all |
| VAL-005 | validation | validation.scope-not-standard | required | Where the date is at risk, the wave scope reduces. The validation standard does not. | all |
| OPS-001 | operations | operations.runbook | required | An operational runbook exists and has been walked through. | all |
| OPS-002 | operations | operations.change-approval | required | Any environment-changing action carries approval, a dry run, and a documented rollback. | all |
| OPS-003 | operations | operations.decommission | prohibited | Source systems are not decommissioned until hypercare completes and acceptance is recorded. | all |
| OPS-004 | operations | operations.staging-step-review | required | Where a target is chosen because it completes in time rather than because it is the intended end state, the decision records that and carries a review date. | all |
| COMP-001 | compliance | compliance.control-evidence | required | Control evidence is collected during validation. | all |
| COMP-002 | compliance | compliance.product-claims | required | Support status, limits, and commercial terms are dated references, revalidated before use. | all |
| COST-001 | cost | cost.sizing-basis | required | Any cost or capacity commitment names the measured basis it rests on. | all |
| COST-002 | cost | cost.deferral-impact | required | Every deferred workload records its renewal or support-cost impact, so deferral is a priced decision rather than an open question. | all |
| NAME-001 | naming | naming.convention | required | Resource names follow the agreed convention. | all |

## Exceptions

Ninety days is the ceiling, and an exception granted close to the date must expire after it
rather than before — otherwise it lapses during the busiest week of the engagement.

| ID | Policy ID | Scope | Justification | Owner role | Approver role | Approver principal | Compensating controls | Granted on | Expires on | Review on |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
