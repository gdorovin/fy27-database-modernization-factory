# Validation report — wave-2-business-critical

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-proseware-billing-fy27` |
| Report | `vr-wave-2-business-critical` |
| Wave | `wave-2-business-critical` |
| Migration plan | `plan-wave-2-business-critical` |
| Executed | 2026-09-07 01:10 to 05:50 |
| **Outcome** | **NO-GO** |
| Rollback triggered | Yes |

> **Outcome: no-go.** The documented rollback path applies. This attempt did not succeed,
> and nothing in this report should be read as a partial success. Corrective issues are
> listed below and must be closed before another attempt is scheduled.

## Result summary

| Result | Count |
| --- | --- |
| Pass | 5 |
| Fail | 2 |
| Not run | 2 |
| Not applicable | 0 |

## Blocking failures

Each of these forces a no-go on its own.

| Check | Category | Tolerance | Baseline | Observed |
| --- | --- | --- | --- | --- |
| Overnight billing run completes within tolerance of baseline | performance | Within 10% of the recorded baseline | 3 h 40 m, completing at 04:40 | 5 h 25 m, completing at 06:25, a 48% regression past the 06:00 constraint |
| Invoice dispatch integration succeeds end to end | integration | Every confirmed dependency succeeds | 14 of 14 passing on source | 13 of 14 passing; dispatch acknowledgement callback timed out |

## Blocking checks that did not run

A check that did not run is not a pass. While any of these remain, `go` is not available.

- Billing history row counts and checksums reconcile (data-reconciliation)
- Business owner accepts the outcome (business-acceptance)

## Business acceptance

| | |
| --- | --- |
| Business owner accepted | No |
| Application owner accepted | No |
| Accepted on | — |

Conditions:

- Acceptance is withheld until the billing run completes inside the overnight window on the target.

## All checks

### Backup restore

| Check | Result | Tolerance | Baseline | Observed | Blocking | Generated test |
| --- | --- | --- | --- | --- | --- | --- |
| Restore from backup succeeds | pass | Restore completes and row counts reconcile | Restore in 42 minutes on source | Restore completed in 38 minutes, counts reconciled | Yes | No |

### Business acceptance

| Check | Result | Tolerance | Baseline | Observed | Blocking | Generated test |
| --- | --- | --- | --- | --- | --- | --- |
| Business owner accepts the outcome | not-run | Approval recorded by the business owner | — | — | Yes | No |

### Connectivity

| Check | Result | Tolerance | Baseline | Observed | Blocking | Generated test |
| --- | --- | --- | --- | --- | --- | --- |
| Every confirmed consumer connects to the target | pass | All confirmed consumers connect | 6 consumers | 6 of 6 consumers connected | Yes | No |

### Data reconciliation

| Check | Result | Tolerance | Baseline | Observed | Blocking | Generated test |
| --- | --- | --- | --- | --- | --- | --- |
| Billing history row counts and checksums reconcile | not-run | Zero unreconciled tables | 1.2 billion rows across 38 tables | — | Yes | No |

### Integration

| Check | Result | Tolerance | Baseline | Observed | Blocking | Generated test |
| --- | --- | --- | --- | --- | --- | --- |
| Invoice dispatch integration succeeds end to end | fail | Every confirmed dependency succeeds | 14 of 14 passing on source | 13 of 14 passing; dispatch acknowledgement callback timed out | Yes | No |

### Performance

| Check | Result | Tolerance | Baseline | Observed | Blocking | Generated test |
| --- | --- | --- | --- | --- | --- | --- |
| Overnight billing run completes within tolerance of baseline | fail | Within 10% of the recorded baseline | 3 h 40 m, completing at 04:40 | 5 h 25 m, completing at 06:25, a 48% regression past the 06:00 constraint | Yes | No |

### Programmability

| Check | Result | Tolerance | Baseline | Observed | Blocking | Generated test |
| --- | --- | --- | --- | --- | --- | --- |
| Generated procedure comparison suite | pass | Identical results for every generated case | 412 generated cases | 412 of 412 matched | No | Yes |

### Schema

| Check | Result | Tolerance | Baseline | Observed | Blocking | Generated test |
| --- | --- | --- | --- | --- | --- | --- |
| Schema objects reconcile between source and target | pass | Zero unexplained differences | 1,412 objects | 1,412 objects, zero differences | Yes | No |

### Security configuration

| Check | Result | Tolerance | Baseline | Observed | Blocking | Generated test |
| --- | --- | --- | --- | --- | --- | --- |
| Security configuration matches policy | pass | Zero deviations without an approved exception | Policy set SEC-001 to SEC-005 | Zero deviations | Yes | No |


## Rollback

Reason: Billing run latency regression exceeded the agreed tolerance and one blocking integration test failed. Data reconciliation had not completed when the rollback decision window closed.

Evidence was preserved before the rollback ran, per the rollback plan. Review it before
scheduling another attempt.

## Corrective work

- `issue-wave-2-billing-latency-regression`
- `issue-wave-2-invoice-dispatch-integration-failure`
- `issue-wave-2-history-reconciliation-incomplete`

## Evidence

- Evidence: _none cited_
- Playbook: `playbooks/default` v1.0.0
