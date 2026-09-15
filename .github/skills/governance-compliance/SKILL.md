---
name: governance-compliance
description: Check artifacts against the active playbook, verify approval completeness and separation of duties, audit policy exceptions and their expiry, and confirm evidence provenance is intact.
---

# Governance and compliance

Checks that the trail holds. Not whether the architecture is good — whether the reasoning
can be reconstructed and the approvals are real.

## Invoke when

- A plan is about to be presented for human approval.
- A pull request touches contracts, playbooks, agents, or safety boundaries.
- An approval trail needs auditing.
- A policy exception is being requested, renewed, or has expired.

## Do not invoke when

- Platform configuration is the question — use `landing-zone-readiness` instead.
- Technical validation results are the question — defer to `migration-validation`.
- A target is being chosen — use `azure-target-recommendation` instead.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| The artifacts under review | The engagement | Yes |
| Active playbook and its version | `playbooks/` | Yes |
| Approval ledger | The engagement | Yes |
| Policy exceptions with expiry dates | Playbook | Where any exist |
| Evidence bundle | `estate-discovery` | Yes |

## Preconditions

1. The playbook validates. Checking artifacts against an incoherent playbook produces
   incoherent findings.
2. Artifact authorship is recorded, so self-approval is detectable by inspection.
3. The reviewer is not the author of what is being reviewed.

## Procedure

1. **Playbook pin.** Confirm each artifact records the playbook path, version, and the
   policy ids applied. Without that pin, nobody can reconstruct which rules produced the
   decision.
2. **Provenance.** Confirm every recommendation cites evidence, every assumption sits in
   the `assumptions` array with an owner, and confidence is not inflated beyond the
   evidence class.
3. **Approvals.** For any artifact claiming an approved status, confirm an approval
   artifact exists, its content hash still matches, and the approver differs from the
   author. An agent may never approve agent-authored work.
4. **Cutover approvals.** Confirm all five owner roles. Count them; do not assume.
5. **Exceptions.** Confirm every exception carries scope, justification, owner, approver,
   compensating controls, expiry, and review date. Confirm none has expired. An expired
   exception is a live finding, not a formality.
6. **Separation of duties.** Confirm the proposing party did not approve, and that read-only
   agents hold no editing tools.
7. **Conflicts.** Confirm unresolved evidence conflicts have blocked progression rather
   than being quietly resolved.
8. **Safety.** Confirm no artifact claims zero downtime, no undated product claim has
   appeared, and no secret or customer datum has entered the repository.
9. Mark the plan ready for human approval, or list what blocks it. Never approve it.

## Decision points

| Finding | Severity |
| --- | --- |
| Artifact approved with no approval artifact | Blocking |
| Approval hash no longer matches | Blocking; the artifact changed after approval |
| Author approved their own artifact | Blocking |
| Cutover missing any of the five roles | Blocking |
| Exception expired | Blocking |
| Exception missing compensating controls | Blocking |
| Recommendation with no evidence reference | Blocking |
| Undated perishable product claim | Blocking |
| Assumption stated in prose rather than the array | Non-blocking, fix it |
| Extended playbook content outside the schema | Non-blocking, note that enforcement is best-effort |

## Output contract

Blocking findings, non-blocking findings, and the evidence for each — each naming the
artifact and the rule. Plus one explicit statement: ready for human approval, or not, with
what would change that.

This skill has the authority to say "ready for human approval". It never performs the
approval itself.

## Validation

```bash
dbmodernize validate-repo
dbmodernize validate-playbook playbooks/default
dbmodernize validate-agent .github/agents
dbmodernize validate-skill .github/skills
```

## Failure and fallback

- **Approval ledger unavailable.** Treat every approval claim as unverified and block.
- **Playbook fails validation.** Stop. Fix the playbook first; findings against a broken
  playbook are noise.
- **Reviewer authored some of the artifacts.** Hand those to a second reviewer. Reviewing
  your own work is how the separation-of-duties rule fails in practice.

## Avoid

- Approving anything. This skill checks; humans decide.
- Accepting a plan because it is thorough. Thorough and compliant are different properties.
- Letting an expired exception pass as a formality.
- Treating a warning as a blocker, or a blocker as a warning.
- Reviewing against a playbook version different from the one the artifact pinned.

## Example

A target decision reports status `approved`. An approval artifact exists, but the content
hash no longer matches the artifact.

That is a blocking finding. Someone edited the decision after it was approved, which means
what was approved and what is now recorded are not the same document. The approval is
invalid until re-granted against the current content.
