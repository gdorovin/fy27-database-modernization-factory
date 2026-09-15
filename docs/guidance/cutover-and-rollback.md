# Cutover and rollback

> **verified_on: 2026-09-15.** Replication mechanisms and their characteristics change.
> Nothing here asserts a specific product capability; confirm the method against current
> documentation when you choose one.

## Two documents, deliberately separate

`cutover-plan-<n>.md` and `rollback-plan-<n>.md` are separate files because they are read
under different conditions. Nobody should be scrolling past a task list at 03:00 to find the
rollback trigger.

Both are rendered per wave.

## Before the window

Four things must be true, and the first two produce numbers rather than opinions:

1. **The cutover has been rehearsed**, and the rehearsal produced a duration.
2. **The rollback has been rehearsed**, and that produced a duration too.
3. **All five approval roles have named individuals available** for the whole window.
4. **The rollback is staffed** for the whole window, not just the start.

Without the two measurements, the window is sized from an estimate and the rollback decision
point is a guess.

## The decision point

This is the most useful number in the plan, and it is arithmetic:

```text
rollback decision point = window length − measured rollback duration
```

A 90-minute window with a measured 21-minute rollback gives a decision point at minute 69.
Past that, the correct action is no longer "roll back" — it is "fix forward under incident
management", because the rollback no longer fits.

Knowing which mode you are in, in advance, is the difference between a controlled recovery
and an improvised one. Writing it down before the night is the only way that happens.

## Go and no-go

Thresholds, not judgement. At 03:00, judgement is the first thing to degrade.

| Criterion | Verified by |
| --- | --- |
| No blocking validation check failed, and none is un-run | The validation report |
| Replication lag reached zero and held | Monitoring output, captured |
| Rollback rehearsed, staffed, and available | Rehearsal record plus named roster |
| All five owner roles have approved | The approval ledger |

The decision is **announced**, either way. "No objection" is not a go. Silence in a
conference bridge at 02:00 means people are tired, not that they agree.

## Sequence

1. Announce the freeze; confirm the on-call roster.
2. Apply the write freeze.
3. Drain replication to zero lag and hold for the agreed period.
4. Run the go / no-go review with all five roles present.
5. **Go:** switch the application, run smoke tests, confirm write availability.
6. **No-go:** stop, announce it, follow the rollback plan.
7. Announce the outcome, including elapsed time and any deviation.

## Rollback triggers

Any one of these is sufficient. Each is a threshold with a verification method:

- Performance regresses beyond the agreed tolerance against baseline.
- Any blocking application integration test fails.
- Data reconciliation is incomplete or shows an unexplained difference.
- The window is exceeded with no clear path to completion.

## Rolling back

**Preserve evidence first.** Logs, metrics, failed test output, replication state. Rolling
back without capturing evidence guarantees the next attempt fails the same way, and the
second failure is always more expensive than the first — politically as well as technically.

**Then execute.** Return application configuration to the source, confirm write availability.

**Then reconcile.** Writes accepted by the target during the window must be identified,
extracted, and either replayed or formally written off with the business owner.

Rollback is not complete when the application is serving again. It is complete when the data
question is settled. The gap between those two moments is where quiet data loss lives.

## Afterwards

1. Record a validation report with a `no-go` outcome.
2. Raise a corrective issue per failure, each with an owner.
3. Hold a blameless review; update the plan before scheduling another attempt.
4. **Never describe a rolled-back attempt as a success.**

That last one is enforced. Scenario 07 asserts that the generated report contains no success
language, because "completed successfully with some issues" is precisely how a rolled-back
migration enters a status report and stops being examined.

## Language

No zero-downtime claim, in any wording. The model rejects it, and the repository validator
scans every Markdown file for it.

`near-zero-planned` requires a measured rehearsal. Until then the honest answer is
`short-planned`, with the method named.
