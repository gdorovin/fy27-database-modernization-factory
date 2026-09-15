# Validation plan — Wave 2 - business critical

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-adatum-group-fy27` |
| Wave | `wave-2-business-critical` |
| As at | 2026-07-06 |
| Checks | 27 |
| Blocking checks | 25 |

## How this plan is used

Each check records an observation against a tolerance. Three rules decide the outcome:

1. A blocking check that fails forces a **no-go**.
2. A blocking check that has not run forbids a **go**. Not run is not a pass.
3. Generated tests are supporting evidence. A `go` cannot rest on them alone.

Checks without a tolerance are judgement calls and name the owner who makes the judgement.

## Checks

### Auditing

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Auditing and diagnostic logging reach their destination | Generate an auditable event and confirm it arrives in the log sink | Event visible in the sink within the agreed interval | Yes |

### Availability

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Failover behaves as designed | Trigger a controlled failover and measure recovery | Recovery within the agreed RTO | Yes |

### Backup restore

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| A restore from backup succeeds | Restore into an isolated environment and verify the data | Restore completes and row counts reconcile | Yes |

### Business acceptance

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Business owner accepts the outcome | Formal acceptance recorded as an approval artifact | Approval recorded by the business owner | Yes |

### Concurrency

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Group finance: concurrency and locking behaviour are acceptable | Run the peak concurrency profile and observe blocking and deadlocks | No sustained blocking beyond the baseline profile | Yes |

### Configuration

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Target configuration matches the approved design | Compare deployed configuration with the infrastructure-as-code definition | Zero unexplained differences | Yes |

### Connectivity

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Every confirmed consumer can connect to the target | Connect from each application host using the production identity and network path | All confirmed consumers connect successfully | Yes |

### Cost sizing

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Observed consumption is consistent with the sizing assumption | Compare observed consumption with the sizing used in the business case | Within the agreed variance, or a documented resize action | No |

### Data reconciliation

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Group finance: row counts and checksums reconcile | Compare row counts and column checksums per table | Zero unreconciled tables | Yes |

### Data types

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Group finance: data types and precision are preserved | Compare column types, precision, scale, and collation | Zero precision or collation differences without a recorded decision | Yes |

### Encryption

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Encryption in transit and at rest is enabled | Inspect the connection and storage encryption settings | Encryption enabled on all paths | Yes |

### Functional

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Group finance: application functional tests pass | Run the application functional suite against the target | Zero failures | Yes |

### Identity

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Authentication and authorization work as designed | Verify managed identity or directory authentication and least-privilege roles | No account holds more privilege than its documented role | Yes |

### Integration

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Group finance: integrations with dependent systems succeed | Exercise each confirmed dependency end to end | Every confirmed dependency succeeds | Yes |

### Inventory

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Every workload in the wave is accounted for | Compare the migrated object inventory with the wave workload list | Zero unaccounted workloads | Yes |

### Monitoring

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Monitoring and alerting are live and routed to an owner | Trigger a test alert and confirm it reaches the on-call rota | Alert received by a named owner | Yes |

### Network isolation

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Network isolation is enforced | Attempt connection from outside the approved network path | Connection refused from every unapproved path | Yes |

### Performance

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Group finance: performance is within tolerance of baseline | Replay the baseline workload and compare latency and throughput | Within 10% of the recorded baseline | Yes |

### Posture

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Security posture and policy compliance show no new high findings | Review posture and policy reporting for the target scope | No new high or critical finding attributable to this migration | Yes |

### Programmability

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Group finance: stored procedures and functions behave identically | Execute the agreed procedure test set and compare results with the source | Identical results for every case in the set | Yes |

### Referential integrity

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Group finance: referential integrity holds | Validate constraints and check for orphaned rows | Zero constraint violations and zero orphans | Yes |

### Regression

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Group finance: regression suite passes | Run the application regression suite against the target | Zero new failures against the source run | Yes |

### Rpo rto

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Measured RPO and RTO meet the agreed targets | Measure during the controlled failover and restore tests | Within the agreed RPO and RTO | Yes |

### Runbooks

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Operational runbooks exist and have been walked through | Operations owner walkthrough of the runbook against the deployed target | Judgement call | No |

### Schema

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Group finance: schema objects reconcile | Compare object counts and definitions between source and target | Zero unexplained differences | Yes |

### Security configuration

| Check | Method | Tolerance | Blocking |
| --- | --- | --- | --- |
| Security configuration matches policy | Compare deployed settings with the playbook security policies | Zero policy deviations without an approved exception | Yes |
| Group finance: controls for SOX are in place and evidenced | Collect control evidence for each scope and review with the security owner | Every required control evidenced | Yes |


## Recording results

For every check, record:

- the observed value,
- the result (`pass`, `fail`, `not-run`, `not-applicable`),
- an evidence reference,
- and, where the result is a judgement call, who made it.

The completed record is a validation report artifact, which is what a go / no-go decision
is taken against.
