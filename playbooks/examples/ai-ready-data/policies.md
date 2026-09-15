# AI-ready data playbook — policies

The default policy set, plus the data-governance controls an intelligent scenario depends
on. The additions cluster in `data` and `validation`, because that is where these
engagements actually fail.

## Policies

| ID | Category | Subject | Directive | Requirement | Applies to |
| --- | --- | --- | --- | --- | --- |
| SEC-001 | security | network.public-endpoint | prohibited | Database endpoints are not reachable from the public internet. | all |
| SEC-002 | security | data.encryption-at-rest | required | Encryption at rest is enabled on every target and every derived copy. | all |
| SEC-003 | security | data.encryption-in-transit | required | Connections enforce encryption in transit with an explicit minimum protocol version. | all |
| SEC-004 | security | secrets.storage | required | Secrets are held in a managed secret store. | all |
| SEC-005 | security | posture.baseline | required | Posture reporting covers the target scope and a baseline is recorded. | all |
| SEC-006 | security | security.derived-access-model | required | Any index, cache, or embedding built from source data enforces an equivalent access model. An inherited obligation is not an inherited permission. | all |
| IAM-001 | identity | auth.method | required | Applications and serving layers authenticate with a managed or directory identity. | all |
| IAM-002 | identity | auth.least-privilege | required | Every principal holds the minimum privilege its role needs, including service principals used by a serving layer. | all |
| IAM-003 | identity | auth.break-glass | required | A break-glass account exists, is monitored, and its use raises an alert. | production |
| NET-001 | networking | network.private-endpoint | required | Private connectivity for database access from application and serving tiers. | all |
| NET-002 | networking | network.name-resolution | required | Private name resolution is configured and tested before cutover. | all |
| NET-003 | networking | network.segmentation | required | Network rules permit only documented tiers and administrative paths. | all |
| DATA-001 | data | data.classification | required | Every workload and every derived copy carries a data classification. | all |
| DATA-002 | data | data.residency | required | Residency requirements block any target or serving location that cannot satisfy them. | all |
| DATA-003 | data | data.reconciliation | required | Row counts and checksums reconcile before cutover is considered complete. | all |
| DATA-004 | data | data.customer-evidence | prohibited | Real customer exports and personal data are never committed to a repository. | all |
| DATA-005 | data | data.system-of-record | required | Every entity in scope has exactly one named system of record with a named owner. An attribute with two systems of record has no correct answer. | all |
| DATA-006 | data | data.quality-measured | required | Completeness, consistency, duplication, and timeliness are measured and recorded before any intelligent scenario is built. | all |
| DATA-007 | data | data.semantics-documented | required | Field names and coded values are documented where a reader would otherwise have to guess. | all |
| DATA-008 | data | data.deletion-propagation | required | Deletion obligations propagate to every derived copy, index, cache, and embedding, and the propagation is tested. | all |
| DATA-009 | data | data.copy-control | prohibited | No uncontrolled copy of customer data is created. Every copy has an owner, a purpose, and a retention decision. | all |
| OBS-001 | observability | monitoring.alerting | required | Monitoring and alerting are live and routed to a named owner. | all |
| OBS-002 | observability | monitoring.diagnostics | required | Diagnostic and audit logs reach a retained sink, and delivery is verified. | all |
| OBS-003 | observability | monitoring.baseline-comparison | required | A source baseline exists and the post-migration comparison is recorded. | all |
| OBS-004 | observability | monitoring.serving-observability | required | Queries from a serving layer are attributable to a principal and observable in the same way as application queries. | all |
| AVL-001 | availability | availability.rpo-rto | required | RPO and RTO are stated by the business owner. | all |
| AVL-002 | availability | availability.failover-test | required | Failover is tested and the recovery time measured. | production |
| AVL-003 | availability | availability.backup-restore | required | A restore is performed and verified. | all |
| AVL-004 | availability | availability.downtime-claim | prohibited | Zero-downtime claims are not made. "Near-zero planned downtime" requires a measured rehearsal. | all |
| AVL-005 | availability | availability.serving-headroom | required | The operational system has measured headroom for the additional read pattern, or a separate serving path exists. | all |
| VAL-001 | validation | validation.blocking-checks | required | Every blocking check has a recorded observation before a go decision. | all |
| VAL-002 | validation | validation.generated-tests | prohibited | Generated tests alone are not accepted as migration proof. | all |
| VAL-003 | validation | validation.rollback-rehearsal | required | The rollback path is rehearsed before cutover. | production |
| VAL-004 | validation | validation.business-acceptance | required | Business and application owners accept the outcome before a wave is closed. | all |
| VAL-005 | validation | validation.readiness-verdict | required | An AI or analytics readiness verdict is recorded, with its conditions, before any intelligent scenario is scoped. | all |
| VAL-006 | validation | validation.readiness-claim | prohibited | No artifact asserts that an estate is AI-ready. The verdict is conditional and names its conditions. | all |
| OPS-001 | operations | operations.runbook | required | An operational runbook exists and has been walked through. | all |
| OPS-002 | operations | operations.change-approval | required | Any environment-changing action carries approval, a dry run, and a documented rollback. | all |
| OPS-003 | operations | operations.decommission | prohibited | Source systems are not decommissioned until hypercare completes and acceptance is recorded. | all |
| COMP-001 | compliance | compliance.control-evidence | required | Control evidence is collected during validation. | all |
| COMP-002 | compliance | compliance.product-claims | required | Support status, limits, preview state, and commercial terms are dated references. | all |
| COMP-003 | compliance | compliance.purpose-limitation | required | Each derived copy records the purpose it was created for, and is reviewed against it. | all |
| NAME-001 | naming | naming.convention | required | Resource names follow the agreed convention. | all |
| COST-001 | cost | cost.sizing-basis | required | Any cost or capacity commitment names the measured basis it rests on. | all |

## Exceptions

None open. An exception to `DATA-005`, `DATA-008`, or `VAL-006` additionally requires the
privacy officer, because those three are the ones whose failure is discovered by a customer
rather than by a test.

| ID | Policy ID | Scope | Justification | Owner role | Approver role | Approver principal | Compensating controls | Granted on | Expires on | Review on |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
