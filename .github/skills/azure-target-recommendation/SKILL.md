---
name: azure-target-recommendation
description: Compare viable Azure destinations for one workload on compatibility, operational control, scale, availability, security, residency, application coupling, and cost inputs, and record the rejected alternatives. Use after assessment.
---

# Azure target recommendation

Produces a per-workload destination with its reasoning and its rejected alternatives. The
rejected options are the valuable part: they are what survives review.

## Invoke when

- A workload has been assessed and is free of blocking findings.
- An existing recommendation is challenged and the comparison needs re-running.
- New evidence changes an input, such as a measured size or a confirmed dependency.

## Do not invoke when

- The workload has an open blocking finding — use `estate-discovery` instead to close it.
  Only a non-moving interim posture is available until it is closed.
- The source engine family differs from the target family — defer to
  `oracle-heterogeneous-migration`, which requires conversion evidence first.
- The question is sequencing rather than destination — use `migration-wave-planning`.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| Assessed workload with findings | `estate-discovery` | Yes |
| Instance features and extensions in use | Evidence | Yes |
| Sizing, and whether it was measured | Evidence | Yes |
| RPO, RTO, and planned-downtime budget | Business owner | Yes |
| Data residency requirement | Security owner | Where one exists |
| Playbook approved target list | Active playbook | Yes |
| Cost inputs | Customer or account team | No; never invented |

## Preconditions

1. `workload.is_recommendation_ready` is true, or only a non-moving posture is on offer.
2. The active playbook has been validated.
3. Any prohibited target is known, so it can be rejected with a citation rather than
   silently omitted.

## Procedure

1. Enumerate every candidate for the source platform. A comparison that starts with one
   option is a preference wearing a decision's clothes.
2. Remove nothing silently. A target prohibited by the playbook is *rejected with a
   citation*, so the reader can see it was considered.
3. Block, rather than score down, any target that cannot satisfy a hard constraint —
   operating-system dependency, data residency, an instance-scoped feature the target does
   not offer.
4. Score the remainder against the published adjustments in
   `src/dbmodernize/scoring/targets.py`. Every number must be reconstructable by hand.
5. Select the highest scorer. Mark every other option `rejected` or `blocked` with the
   reason and, where relevant, the score gap.
6. Record compatibility, operational, security, performance, residency, and application
   impact notes.
7. Record the downtime approach. Without a rehearsal, the class is `short-planned` or
   `unknown`. Never stronger.
8. Attach cost inputs only if a human supplied them, with the source named.

## Decision points

| Question | Choose | Because |
| --- | --- | --- |
| Instance-scoped feature in use | Block database-scoped targets | The feature is not available at that scope |
| Operating-system dependency in use | Block every managed target | No managed service offers that access |
| Size and growth both modest | Reject the high-scale tier | Capability nobody asked for is still cost and complexity |
| Sizing estimated, not measured | Recommend, but forbid a capacity commitment | An estimate cannot carry a commitment |
| Residency requirement present | Block, do not penalise | A hard constraint is not a scoring input |
| Evidence complete and nothing blocking | Recommend, status `recommended` | Approval is a separate, human step |

## Output contract

One artifact per workload validating against `contracts/target-decision.schema.json`, with
at least two considered options, exactly one `recommended`, at least one `rejected` or
`blocked`, a rationale, and a `downtime_approach` carrying a named method and a basis.

Status is `recommended`. It becomes `approved` only when a separate approval artifact
exists, authored by a different principal.

## Validation

```bash
dbmodernize recommend-targets --engagement input/engagement.yaml --input input --out out
dbmodernize validate-scenario scenarios
```

The model rejects a decision with a single option, a decision with no rejected
alternative, and a `near-zero-planned` downtime class with no measured rehearsal.

## Failure and fallback

- **Every option blocked.** Produce no destination. Record why each is blocked and
  escalate; the estate is telling you a constraint has to move first.
- **Two options score within a few points.** Do not split the difference. Record both as
  viable, name the evidence that would separate them, and take it to architecture review.
- **Playbook prohibits the only viable target.** Stop. A policy exception with compensating
  controls is a governance decision, not a scoring adjustment.

## Avoid

- Recommending a target because it is the current campaign.
- Applying one destination across an estate. Two databases on one instance can legitimately
  differ.
- Claiming zero downtime under any wording.
- Inventing a cost, a saving, or a consumption figure.
- Asserting current service limits or support status without a dated reference.

## Example

A workload uses scheduled jobs and cross-database queries. Database-scoped targets are
**blocked** — not scored low — because the features are unavailable at that scope. The
instance-scoped target scores 95; infrastructure scores 37 because it would retain
patching responsibility for no reason the evidence supports.

The recommendation is the instance-scoped target, and the reader can see exactly why the
other four were not chosen.
