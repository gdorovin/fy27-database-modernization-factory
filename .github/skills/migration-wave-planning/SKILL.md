---
name: migration-wave-planning
description: Group workloads into dependency-aware waves ordered lowest risk first, select a genuine pilot, and set testable entry and exit criteria for each wave.
---

# Migration wave planning

Decides what moves together and in what order. Two mistakes dominate: splitting coupled
systems, and calling something a pilot that is too large or too critical to learn from.

## Invoke when

- Target decisions exist for the workloads in scope.
- A wave needs resequencing because evidence or a constraint changed.
- A pilot needs selecting.

## Do not invoke when

- Targets have not been decided — use `azure-target-recommendation` instead.
- The detailed task plan is needed — defer to `migration-plan-generation`, which consumes
  waves.
- The question is cutover mechanics — use `cutover-and-rollback` instead.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| Target decisions | `azure-target-recommendation` | Yes |
| Confirmed dependencies | Assessment | Yes |
| Criticality and environment per workload | Assessment | Yes |
| Business calendar and freeze periods | Business owner | Yes |
| Team capacity | Delivery lead | Yes |
| Landing zone readiness | `landing-zone-readiness` | Before entry, not before planning |

## Preconditions

1. Workloads with open blocking findings are excluded. They may hold an interim posture,
   but they are not scheduled.
2. Workloads whose disposition is retain, retire, or replace are excluded. A wave moves
   things.
3. Dependency confirmation status is known per workload.

## Procedure

1. Build dependency groups. Workloads that reference each other move together, because a
   cutover that moves half a coupled pair is worse than either whole option.
2. Rank each group by criticality and environment. Non-production and low criticality
   first.
3. Select the pilot: the smallest, lowest-ranked group. A pilot exists to find the problems
   cheaply, so a large or business-critical pilot is a contradiction.
4. Band the remainder — low risk, medium risk, business critical — and sequence them.
5. Make each wave depend on the one before it, so lessons flow forward instead of being
   rediscovered.
6. Write entry criteria: approved decisions, no open blockers, rehearsed rollback.
7. Write exit criteria: validation passed, business acceptance recorded, monitoring live
   and owned. For the pilot, add lessons captured and the plan updated.
8. Add prerequisites: landing zone readiness, a non-production environment, a performance
   baseline where sizing is estimated.

## Decision points

| Question | Choose | Because |
| --- | --- | --- |
| Two workloads reference each other | Same wave | A half-moved pair fails in both directions |
| Everything is coupled | One wave, and say so | Hiding the coupling does not remove it |
| Pilot candidate is business critical | Find another, or say no pilot is available | A critical pilot cannot fail safely |
| Business freeze overlaps a wave | Move the wave | The freeze is a constraint, not a preference |
| Capacity insufficient | Fewer waves in parallel, not shorter validation | Validation is the last line of defence |
| Workload is retained | Exclude from waves | Counting it as scheduled overstates progress |

## Output contract

A wave plan where waves have unique sequences, no workload appears twice, no wave depends
on a later wave, the pilot is sequence 1 and small, every wave has at least one testable
exit criterion, and `deferred_workload_ids` lists everything not scheduled.

The model enforces all of this, so a plan that violates it will not serialize.

## Validation

```bash
dbmodernize plan-waves --engagement input/engagement.yaml --input input --out out
dbmodernize validate-scenario scenarios
```

## Failure and fallback

- **No small, low-risk group exists.** Say that no true pilot is available and raise it as
  a risk. Do not relabel a critical workload as a pilot.
- **Dependencies unconfirmed.** Those workloads stay out of waves. Scheduling them would
  schedule an unknown blast radius.
- **Sponsor wants everything in one wave.** Present what a single wave means for rollback:
  one decision, one window, one chance. Then let them decide with that in front of them.

## Avoid

- Splitting a confirmed dependency pair across waves.
- Putting the most valuable workload first because it is the most visible.
- Writing exit criteria that cannot be checked.
- Scheduling a workload with an open blocking finding.
- Treating a retained or Arc-governed workload as a scheduled wave member.

## Example

Four workloads. Two are coupled and business critical; one is a test copy; one has unknown
consumers.

The pilot is the test copy alone. The coupled pair forms the second wave, entered only
after the pilot's exit criteria are met. The workload with unknown consumers is deferred
entirely — it appears in `deferred_workload_ids` and in an issue, not in a wave.
