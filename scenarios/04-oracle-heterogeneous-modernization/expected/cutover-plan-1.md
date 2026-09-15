# Cutover plan — Wave 1 - pilot

> Generated from repository artifacts. Every statement here traces to an evidence reference, an assumption, or a recommendation, and is labelled as such. This document is a proposal until a human approves it.

| | |
| --- | --- |
| Engagement | `eng-litware-manufacturing-fy27` |
| Wave | `wave-1-pilot` |
| Plan | `plan-wave-1-pilot` |
| As at | 2026-06-08 |
| Owner | delivery-lead |
| Execution window | An agreed low-traffic window, sized from the measured rehearsal. |
| Freeze starts | T-2h relative to the agreed window start |

## Required approvals

All of the following must have recorded an approval before the cutover begins. Four of
five is not a cutover approval.

- [ ] business-owner
- [ ] application-owner
- [ ] database-owner
- [ ] security-owner
- [ ] operations-owner

## Replication

Continuous replication drained to zero lag before the switch.

## Go / no-go criteria

The decision is explicit and is announced either way. "No objection" is not a go.

| Criterion | Verified by | Owner | Automated |
| --- | --- | --- | --- |
| No blocking validation check has failed and none is un-run. | Validation report for the wave | delivery-lead | Yes |
| Replication lag has reached zero and stayed there for the agreed period. | Replication monitoring output captured as evidence | database-owner | Yes |
| The rollback path is rehearsed, staffed, and available for the window. | Rehearsal record plus named on-call roster | operations-owner | No |
| All five owner roles have recorded an approval for this cutover. | Approval ledger for the migration plan | delivery-lead | Yes |

## Sequence

1. Announce the freeze and confirm the on-call roster is in place.
2. Apply the write freeze at T-2h relative to the agreed window start.
3. Drain replication to zero lag and hold for the agreed period.
4. Run the go / no-go review with all five owner roles present.
5. On go: switch the application, run smoke tests, and confirm write availability.
6. On no-go: stop, announce it, and follow `rollback-plan.md`.
7. Announce the outcome, including the time taken and any deviation from plan.

## Communication

- Notify affected application owners and the service desk at freeze start.
- Post status at each checkpoint inside the window.
- Announce the go / no-go decision explicitly, including a no-go.
- Confirm completion or rollback, with the reason, to all stakeholders.

## If anything goes wrong

Rollback triggers, method, decision window, and evidence preservation are in
`rollback-plan-1.md`. Read it before the window opens, not during it.

## What this document does not do

It does not execute anything. Every step above is performed by a named human with the
recorded approvals in hand.
