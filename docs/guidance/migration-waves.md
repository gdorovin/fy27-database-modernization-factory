# Migration waves

> **verified_on: 2026-09-15.** Nothing on this page depends on a product capability, but the
> wave thresholds in `src/dbmodernize/scoring/waves.py` are a design choice and should be
> reviewed against real delivery experience.

## Two rules do most of the work

**Coupled workloads move together.** A cutover that moves half a dependency pair produces a
system that half-works, which is harder to recover from than either whole option: rollback
is ambiguous, and the failure is intermittent.

**The pilot is genuinely small.** A pilot exists to find problems cheaply. A pilot
containing the payment database de-risks nothing — it just moves the risk earlier and gives
it a friendlier name.

The planner enforces both. Dependency groups are computed from confirmed dependencies, and a
pilot is sequence 1 with at most two workloads.

## What is not scheduled

A wave moves workloads. These do not belong in one:

| Case | Why |
| --- | --- |
| Open blocking finding | Scheduling an unknown blast radius |
| Disposition is `retain` | Nothing is moving |
| Disposition is `retire` | Nothing is moving |
| Disposition is `replace` | A different programme, with its own plan |

All of them appear in `deferred_workload_ids`. Counting a retained or Arc-governed workload
as scheduled overstates progress, and overstated progress is discovered at the worst point in
the calendar.

## Ordering

Risk rank is criticality plus environment, lowest first:

| Criticality | | Environment | |
| --- | --- | --- | --- |
| low | 0 | development, test | 0 |
| medium | 1 | pre-production | 1 |
| high | 2 | disaster recovery, unknown | 2 |
| critical | 3 | production | 3 |

Bands: low risk (≤2), medium risk (≤4), business critical (everything else). Each wave
depends on the one before it, so lessons flow forward instead of being rediscovered.

## Criteria that can be checked

Entry and exit criteria name a verification method. Prose that cannot be checked is not a
criterion, and at the gate it becomes a negotiation.

Generated entry criteria:

- Every workload has an approved target decision.
- No workload has an open blocking finding.
- The rollback path has been rehearsed in a non-production environment.

Generated exit criteria:

- All blocking validation checks pass and none is left un-run.
- Business and application owners have accepted.
- Monitoring, alerting, and the runbook are live and owned.
- For a pilot: lessons captured and the plan updated.

That last one is the entire justification for having a pilot. A pilot that finishes without
changing the plan either learned nothing or ignored what it learned.

## Prerequisites

Added automatically when the evidence calls for them:

- Landing zone readiness passes for the subscriptions in scope.
- A non-production environment mirroring the target exists.
- Security owner has confirmed control requirements, where a compliance scope exists.
- A performance baseline exists, where sizing is estimated.

Without a baseline, "no regression" is an opinion.

## When the date is at risk

Scope moves. The gate does not.

Fewer workloads in the wave is a legitimate response. A shorter validation, a waived blocking
check, or an un-rehearsed rollback is not — those trade a visible schedule problem for an
invisible quality one, and the invisible one surfaces after the go decision.

## When everything is coupled

Sometimes no small, low-risk group exists. Say so, and raise it as a risk.

Relabelling a business-critical workload as a pilot does not make it one. If the estate
genuinely cannot be piloted, the sponsor should know that before committing to a date.

## Running it

```bash
dbmodernize plan-waves --engagement input/engagement.yaml --input input --out out
```

The model rejects a plan where waves share a workload, where a wave depends on a later wave,
where a pilot is not sequence 1, or where a pilot is too large. Those are structural errors
rather than warnings, because each one produces a plan that cannot be executed as written.
