# Default playbook — policies

Each policy has a stable `ID`, a `Subject` key, and a `Directive`. Two policies sharing a
subject and scope with opposing directives are a conflict, and a conflict fails validation
rather than being resolved silently — the repository will not choose between two rules
the organisation has not reconciled.

Directives: `required`, `prohibited`, `recommended`, `discouraged`.

Generated plans record the policy IDs they applied, so a reader can reconstruct which
version of this file produced a given decision.

## Policies

| ID | Category | Subject | Directive | Requirement | Applies to |
| --- | --- | --- | --- | --- | --- |
| SEC-001 | security | network.public-endpoint | prohibited | Database endpoints are not reachable from the public internet. Access is over private connectivity only. | all |
| SEC-002 | security | data.encryption-at-rest | required | Encryption at rest is enabled on every target. | all |
| SEC-003 | security | data.encryption-in-transit | required | Connections enforce encryption in transit, and the minimum protocol version is set explicitly rather than left to default. | all |
| SEC-004 | security | secrets.storage | required | Secrets are held in a managed secret store. No credential appears in code, configuration, pipeline logs, or an artifact in this repository. | all |
| SEC-005 | security | posture.baseline | required | Security posture reporting is enabled for the target scope, and a new high or critical finding blocks acceptance. | all |
| IAM-001 | identity | auth.method | required | Applications authenticate with a managed identity or directory identity. Shared SQL logins require an approved exception. | all |
| IAM-002 | identity | auth.least-privilege | required | Every principal holds the minimum privilege its documented role needs, and the mapping is reviewable. | all |
| IAM-003 | identity | auth.break-glass | required | A break-glass account exists, is monitored, and its use raises an alert. | production |
| NET-001 | networking | network.private-endpoint | required | Private connectivity is used for database access from application tiers. | all |
| NET-002 | networking | network.name-resolution | required | Private name resolution is configured and tested before cutover, not discovered during it. | all |
| NET-003 | networking | network.segmentation | required | Network rules permit only the application tiers and administrative paths that have been documented. | all |
| DATA-001 | data | data.classification | required | Every workload carries a data classification, and it is recorded before migration begins. | all |
| DATA-002 | data | data.residency | required | Where a residency requirement exists, any target that cannot satisfy it is blocked rather than scored down. | all |
| DATA-003 | data | data.reconciliation | required | Row counts and checksums reconcile before cutover is considered complete. | all |
| DATA-004 | data | data.customer-evidence | prohibited | Real customer exports, production data, and personal data are never committed to this repository. Evidence is referenced by manifest. | all |
| OBS-001 | observability | monitoring.alerting | required | Monitoring and alerting are live, routed to a named owner, and tested with a real alert before acceptance. | all |
| OBS-002 | observability | monitoring.diagnostics | required | Diagnostic and audit logs are sent to a retained sink, and delivery is verified. | all |
| OBS-003 | observability | monitoring.baseline-comparison | required | A source baseline exists and the post-migration comparison is recorded. Without a baseline, "no regression" is an opinion. | all |
| AVL-001 | availability | availability.rpo-rto | required | RPO and RTO are stated by the business owner before an availability design is chosen. | all |
| AVL-002 | availability | availability.failover-test | required | Failover behaviour is tested and the recovery time measured, not assumed from a service description. | production |
| AVL-003 | availability | availability.backup-restore | required | A restore is performed and verified. A backup that has never been restored is not a backup. | all |
| AVL-004 | availability | availability.downtime-claim | prohibited | Zero-downtime claims are not made. "Near-zero planned downtime" requires a measured rehearsal and a named method. | all |
| VAL-001 | validation | validation.blocking-checks | required | Every blocking validation check has a recorded observation before a go decision. Not run is not a pass. | all |
| VAL-002 | validation | validation.generated-tests | prohibited | Generated tests alone are not accepted as migration proof. They are supporting evidence beside independently executed checks. | all |
| VAL-003 | validation | validation.rollback-rehearsal | required | The rollback path is rehearsed before cutover, and the rehearsal is recorded. | production |
| VAL-004 | validation | validation.business-acceptance | required | Business and application owners accept the outcome before a wave is closed. | all |
| OPS-001 | operations | operations.runbook | required | An operational runbook exists and has been walked through with the operations owner. | all |
| OPS-002 | operations | operations.change-approval | required | Any action that changes an environment carries a recorded approval, a dry-run or what-if first where technically possible, and a documented rollback. | all |
| OPS-003 | operations | operations.decommission | prohibited | Source systems are not decommissioned until hypercare completes and business acceptance is recorded. | all |
| COMP-001 | compliance | compliance.control-evidence | required | For workloads in a compliance scope, control evidence is collected during validation rather than reconstructed afterwards. | all |
| COMP-002 | compliance | compliance.product-claims | required | Support status, service limits, preview status, and commercial terms are recorded as dated references and revalidated before customer use. | all |
| NAME-001 | naming | naming.convention | required | Resource names follow the agreed convention and carry the environment and workload identifiers. | all |
| COST-001 | cost | cost.sizing-basis | required | Any cost or capacity commitment names the measured basis it rests on. Estimated sizing does not support a commitment. | all |
| COST-002 | cost | cost.observation | recommended | Observed consumption is compared with the sizing assumption during hypercare, and a resize action is raised where they differ. | all |

## Exceptions

This baseline grants none, and that is the correct state for a baseline. An exception is a
named deviation for a named system with a named owner and a fixed end date. None of those
things exist until an engagement does, so an exception shipped in a reusable playbook is
either meaningless or, worse, silently inherited by every customer who copies the file.

An exception is a time-boxed, compensated deviation. Every field below is mandatory, and an
exception without an expiry date is rejected outright. Expired exceptions fail validation
rather than lapsing quietly into permanence, and an exception running more than 90 days from
its grant date raises a warning — an exception long enough to outlive the people who agreed
to it is a policy change wearing an exception's clothes.

To grant one, add a table with these columns. The row below shows the shape; it is prose in
a fenced block, not a parsed row, so nothing here is in force.

| ID | Policy ID | Scope | Justification | Owner role | Approver role | Approver principal | Compensating controls | Granted on | Expires on | Review on |

```text
| EX-001 | IAM-001 | Legacy reporting tool, non-production only.
| The vendor has no directory-auth support in the supported version, and replacing the
  tool is out of scope for this wave.
| database-owner | security-owner | security-owner-a
| Credential held in the managed secret store; rotated every 30 days; access restricted
  to the reporting subnet; use alerted
| 2026-01-15 | 2026-04-15 | 2026-03-15 |
```

The approver role must differ from the owner role. Requesting a deviation and approving it
cannot be the same act, and validation rejects a playbook where it is.
