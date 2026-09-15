---
name: cutover-and-rollback
description: Define the write freeze, replication drain, go and no-go decision, execution sequence, rollback triggers and decision window, data reconciliation, communications, and ownership for a wave.
---

# Cutover and rollback

The two documents that get read under pressure. They are separate files for that reason:
nobody should scroll past a task list at 03:00 to find the rollback trigger.

## Invoke when

- A wave is approaching its cutover window.
- Rollback triggers and their thresholds need agreeing.
- A previous cutover was messy and the sequence needs tightening.

## Do not invoke when

- The full task plan is needed — use `migration-plan-generation` instead.
- Acceptance thresholds are being defined — defer to `migration-validation`, which supplies
  the evidence the go decision uses.
- The question is who may approve — use `governance-compliance` instead.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| Migration plan for the wave | `migration-plan-generation` | Yes |
| Agreed window and business freeze | Business owner | Yes |
| Measured rehearsal duration | Cutover rehearsal | Yes, before the window |
| Measured rollback duration | Rollback rehearsal | Yes, before the window |
| Performance baseline | Prepare phase | Yes |
| Named approvers for all five roles | Delivery lead | Yes |
| On-call roster for the window | Operations owner | Yes |

## Preconditions

1. Both rehearsals have happened and produced numbers. Without them the window is being
   sized from an estimate.
2. All five approval roles have named individuals available during the window.
3. The rollback path is staffed for the whole window, not just the start.

## Procedure

1. Fix the freeze start relative to the window, and announce it.
2. Confirm the replication method and the lag threshold that must be reached and held.
3. Write go and no-go criteria as thresholds, not opinions. At 03:00, judgement is the
   first thing to degrade.
4. Hold the go / no-go review with all five roles present. Announce the decision
   explicitly, including a no-go. Silence is not consent.
5. Execute: freeze, drain, switch, smoke test, confirm writes.
6. Size the rollback decision window as *window minus measured rollback duration*. Past
   that point the decision changes from roll back to fix forward under incident management,
   and everyone should know which mode they are in.
7. Define data reconciliation for the rollback path: writes accepted by the target during
   the window must be identified, extracted, and replayed or formally written off with the
   business owner.
8. Write the communication plan: freeze, checkpoints, decision, outcome.
9. Record what evidence is captured before any rollback.

## Decision points

| Question | Choose | Because |
| --- | --- | --- |
| Replication lag not at zero | No-go | Lag at switch is data loss with extra steps |
| A blocking validation check failed | No-go | The threshold already decided this |
| A blocking check has not run | No-go | Not run is not a pass |
| An approval role is absent | No-go | Four of five is not a cutover approval |
| Window exceeded with no clear path | Roll back | The decision window exists precisely for this |
| Past the rollback decision window | Fix forward under incident management | The rollback no longer fits |
| Regression inside tolerance but felt slow | Go, and record the observation | Thresholds decided in daylight beat impressions at night |

## Output contract

Two documents per wave: `cutover-plan-<sequence>.md` and `rollback-plan-<sequence>.md`.

The cutover plan lists all five required approval roles as an explicit checklist, the
freeze, the replication method, the go and no-go criteria, the sequence, and the
communication plan.

The rollback plan lists triggers with verification methods, the decision window, the
method, evidence preservation, and the data reconciliation obligation. If the rollback has
not been rehearsed, the document says so at the top.

## Validation

```bash
dbmodernize render-plan --engagement input/engagement.yaml --input input --out out
dbmodernize validate-scenario scenarios/07-failed-validation-and-rollback
```

## Failure and fallback

- **Rollback not rehearsed and the date is fixed.** Escalate the trade to the sponsor with
  the exposure stated. Do not quietly proceed.
- **Rollback triggered.** Preserve evidence first, then execute, then reconcile data. The
  rollback is not complete when the application is serving again; it is complete when the
  data question is settled.
- **Data written to the target during the window cannot be extracted.** Stop and escalate.
  A write-off is a business decision with a named owner, never a technical convenience.

## Avoid

- Claiming zero downtime under any wording.
- Treating "no objection" as a go decision.
- Starting a cutover without the rollback staffed for the full window.
- Rolling back before capturing logs, metrics, and failed test output.
- Describing a rolled-back attempt as a partial success.

## Example

The rehearsal measured a 34-minute cutover and a 21-minute rollback inside a 90-minute
window. The rollback decision point is therefore at minute 69, and it is written down
before the night rather than argued about during it.

At minute 71 the correct action is no longer rollback, and knowing that in advance is the
difference between a controlled recovery and an improvised one.
