---
name: migration-plan-generation
description: Produce the phased task plan for one wave from approved decisions, the playbook, and the risk register, gating every environment-changing task behind an approval and a documented rollback.
---

# Migration plan generation

Turns a wave into an executable sequence. The structural property that matters: a task that
can change an environment cannot exist without an approval requirement and a rollback note.
The model refuses to construct one, so the safety property survives an author's bad day.

## Invoke when

- A wave exists and its detailed plan is needed.
- Evidence or a target decision changed and the plan must be regenerated.
- A reviewer asks which tasks touch an environment and how each would be undone.

## Do not invoke when

- Waves have not been planned — use `migration-wave-planning` instead.
- Only cutover mechanics are in question — defer to `cutover-and-rollback`.
- Acceptance thresholds are being defined — use `migration-validation` instead.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| The wave | `migration-wave-planning` | Yes |
| Target decisions for its workloads | `azure-target-recommendation` | Yes |
| Active playbook | `playbooks/` | Yes |
| Risk register | Assessment | Yes |
| Team roles | Delivery lead | Yes |

## Preconditions

1. Every workload in the wave has a target decision.
2. The playbook validates, so the policy ids recorded on tasks resolve.
3. A non-production environment is available, or provisioning it is the first build task.

## Procedure

1. **Prepare.** Landing zone readiness, source performance baseline, dependency
   confirmation. Nothing moves until these close.
2. **Build.** Provision non-production from infrastructure as code with a what-if first.
   Add schema and code conversion where the decision requires it. Add application
   remediation where the decision requires it.
3. **Migrate.** Seed non-production, establish replication, rehearse the cutover and
   *measure* it, then rehearse the rollback. The rehearsal is what converts a downtime
   claim from an assertion into a number.
4. **Validate.** Execute the validation plan, then review it with all five owner roles.
5. **Cutover.** Provision production after a what-if review, then execute. Both tasks
   require recorded approval from all five roles.
6. **Stabilize.** Hypercare with the rollback still available, then a separate decision
   about decommissioning — which this repository never performs.
7. Record the playbook path, version, and applied policy ids on the plan.

## Decision points

| Question | Choose | Because |
| --- | --- | --- |
| Task changes an environment | `approval_required` and a rollback note | Enforced by the model; a task without them will not build |
| Conversion required | Add a conversion task before seeding | Converted code must exist before data lands on it |
| Application change required | Add remediation in the build phase | The application must be ready before rehearsal |
| Sizing estimated | Baseline capture is a prepare task | A comparison needs something to compare against |
| Rollback not yet rehearsed | Keep it a migrate-phase task | An unrehearsed rollback is a hypothesis |
| Decommission requested early | Keep it after hypercare, as a decision | The source is the rollback path until it is not |

## Output contract

A plan validating against `contracts/migration-plan.schema.json`: at least one phase, at
least one validation task, a cutover plan naming all five approval roles, a rollback plan
with triggers and evidence preservation, and testable acceptance criteria.

Every environment-changing task carries `approval_required: true`, a `rollback_note`, and
a `dry_run_command` where one is technically possible.

## Validation

```bash
dbmodernize render-plan --engagement input/engagement.yaml --input input --out out --dry-run
dbmodernize validate-scenario scenarios
```

The model rejects a plan with no validation task, a task depending on an unknown task, and
a cutover missing any of the five roles.

## Failure and fallback

- **No non-production environment available.** Make provisioning one the first build task.
  Rehearsing in production is not a fallback.
- **Rehearsal cannot be scheduled before the window.** Escalate. Without a rehearsal the
  downtime class stays `short-planned` or `unknown`, and the cutover decision is being
  taken on an estimate.
- **A required approval role is unfilled.** Block the cutover phase. Four of five is not a
  cutover approval, and naming a deputy is a decision the sponsor makes, not the plan.

## Avoid

- Creating a mutating task without an approval gate and a rollback note.
- Putting decommissioning inside the cutover phase.
- Writing a dry-run command that is not actually read-only.
- Omitting the baseline capture because sizing "looks fine".
- Generating a plan for a wave containing an unresolved workload.

## Example

The plan contains eleven tasks. Six change an environment; each carries an approval
requirement, a rollback note, and — where possible — a what-if command to run first.

The rollback rehearsal is a task in its own right, with its own approval, because the one
thing worse than needing a rollback is needing one that has never been run.
