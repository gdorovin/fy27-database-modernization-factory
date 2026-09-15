---
name: landing-zone-readiness
description: Check subscription, identity, network, private connectivity, name resolution, policy, logging, security, backup, disaster recovery, and operational ownership before any workload is scheduled into a wave.
---

# Landing zone readiness

The gate that stops a migration discovering its platform problems during a cutover window.
Most of these checks are cheap now and expensive at 03:00.

## Invoke when

- Before a wave's entry criteria can be met.
- A new subscription or region enters scope.
- A security or compliance finding touches the target platform.
- An earlier wave hit a platform issue that later waves would repeat.

## Do not invoke when

- The question is which target to use — use `azure-target-recommendation` instead.
- The question is whether the playbook itself is coherent — defer to
  `governance-compliance`.
- The question is post-migration verification — use `migration-validation` instead.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| Target subscription and region | Architect | Yes |
| Identity model for applications and administrators | Security owner | Yes |
| Network topology and the path from applications | Network owner | Yes |
| Name resolution design | Network owner | Yes |
| Policy assignments in scope | Security owner | Yes |
| Log destination and retention | Operations owner | Yes |
| Backup and disaster-recovery design | Operations owner | Yes |
| Named operational owner | Delivery lead | Yes |

## Preconditions

1. The playbook is validated, so the policies being checked against are coherent.
2. The target for the wave is known, since requirements differ by target.
3. Someone is accountable for each area. An unowned area fails this check by definition.

## Procedure

1. **Subscription.** Confirm the subscription exists, has an owner, and has capacity for
   the wave. Check quota before the wave, not during it.
2. **Identity.** Confirm applications can authenticate with a managed or directory
   identity. Where a shared login is unavoidable, confirm an approved exception with
   compensating controls exists — not a plan to get one.
3. **Network.** Confirm private connectivity exists between the application tier and the
   target, and that the route has been tested rather than drawn.
4. **Name resolution.** Confirm private name resolution works from the application hosts.
   This is the single most common cutover-night surprise.
5. **Policy.** Confirm the assignments in scope, and that nothing in the planned
   configuration would be denied on deployment.
6. **Logging.** Confirm the destination, retention, and that a test event arrives.
7. **Security.** Confirm posture reporting covers the target scope and record the current
   baseline, so a new finding after migration is attributable.
8. **Backup and recovery.** Confirm the design, and that a restore has been performed into
   an isolated environment.
9. **Ownership.** Name the operational owner and the on-call route. "The platform team"
   is not a name.

## Decision points

| Finding | Effect |
| --- | --- |
| Private connectivity absent | Wave entry blocked |
| Name resolution untested | Wave entry blocked; this fails at the worst moment |
| No managed identity path | Requires an approved exception before entry |
| Policy would deny the deployment | Fix the configuration or obtain an exception first |
| Log destination unconfirmed | Blocking; auditing evidence must land somewhere |
| No named operational owner | Blocking; an unowned system has no incident response |
| Quota insufficient | Blocking; resolve before the window, not inside it |

## Output contract

A readiness result per area — pass, fail, or not applicable — each with evidence and an
owner. Failures become wave prerequisites and, where they carry real exposure, risks in the
register.

## Validation

```bash
dbmodernize validate-playbook playbooks/default
az deployment group what-if --template-file infra/bicep/main.bicep --parameters infra/bicep/main.bicepparam
```

The what-if is a read-only preview. It is never followed by an apply from this repository.

## Failure and fallback

- **Access to inspect the target is unavailable.** Record every area as unverified and
  block wave entry. Unverified is not a pass.
- **An area fails and the date will not move.** Escalate the trade explicitly: the options
  are fix it, obtain a time-boxed exception with compensating controls, or move the date.
  Proceeding quietly is not among them.
- **Ownership disputed.** Record it as a blocking risk owned by the delivery lead.

## Avoid

- Accepting a network diagram as evidence that a route works.
- Treating a policy assignment as compliance without checking the planned configuration
  against it.
- Signing off a backup design with no restore test behind it.
- Deploying anything from this repository. What-if only; a human applies.

## Example

Private connectivity is configured and the diagram is correct. Name resolution from the
application subnet has never been tested.

Wave entry is blocked. The cost now is one afternoon. The cost during a cutover window is
the window, the rollback, and the confidence of everyone who agreed to the plan.
