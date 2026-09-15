# Rollback plan — Wave 2 - business critical

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-northwind-retail-fy27` |
| Wave | `wave-2-business-critical` |
| Plan | `plan-wave-2-business-critical` |
| As at | 2026-03-02 |
| Owner | operations-owner |
| Rehearsed | No |

> **This rollback has not been rehearsed.** An unrehearsed rollback is a hypothesis. The
> wave entry criteria require a rehearsal before cutover.

## Triggers

Any one of these triggers a rollback decision. They are thresholds, not opinions, so the
decision does not depend on who is in the room at 03:00.

| Trigger | Verified by | Owner | Automated |
| --- | --- | --- | --- |
| Post-cutover performance regresses beyond the agreed tolerance against baseline. | Baseline comparison from the validation report | database-owner | Yes |
| Any blocking application integration test fails after cutover. | Integration test results captured as evidence | application-owner | Yes |
| Data reconciliation is incomplete or shows an unexplained difference. | Row count and checksum comparison | database-owner | Yes |
| The cutover exceeds the agreed window with no clear path to completion. | Elapsed time against the window | delivery-lead | No |

## Decision window

The rollback decision is taken no later than the agreed window minus the measured rollback duration.

Past that point the rollback itself no longer fits inside the agreed window, and the
decision changes from "roll back" to "fix forward under incident management".

## Method

Return application configuration to the source, confirm write availability, then reconcile anything written to the target during the window.

## Preserve evidence first

Before rolling back, capture logs, metrics, failed test output, and replication state. Rolling back without evidence guarantees the same failure next attempt.

Rolling back without capturing evidence guarantees the next attempt fails the same way.

## Data reconciliation

Writes accepted by the target during the window must be identified, extracted, and replayed or formally written off with business-owner agreement. Rollback is not complete until this is settled.

Rollback is not complete when the application is serving again. It is complete when the
data question is settled and the business owner has agreed the outcome.

## After a rollback

1. Record the outcome as a validation report with a `no-go` result.
2. Raise corrective issues for every failure, each with an owner.
3. Hold a blameless review and update the plan before scheduling another attempt.
4. Never describe a rolled-back attempt as a success.
