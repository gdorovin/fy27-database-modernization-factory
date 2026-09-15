# Regulated enterprise playbook — charter

version: 1.0.0

Derived from the default playbook, tightened for an estate under external regulatory
supervision. The differences are deliberate and few: a playbook that changes everything is
a fork, and a fork stops receiving improvements.

## Scope

Every database workload in a regulated scope, and every artifact produced about one.

Additional in scope compared with the default:

- Evidence retention and audit trail for supervisory review.
- Segregation of duties between the party proposing and the party approving.
- Data residency as a hard, non-tradeable constraint.

## Outcomes

1. **The audit trail survives independent review.** A supervisor should be able to
   reconstruct any decision from the artifacts alone, without interviewing anyone.
2. **No unreviewed change reaches production.**
3. **Residency and control requirements hold for every workload**, including those that do
   not move.
4. **Security posture improves, measurably, against a recorded baseline.**

## Principles

Everything in the default playbook, plus:

**Residency is a constraint, not a score.** A target that cannot satisfy a residency
requirement is blocked. It is never weighed against convenience.

**Infrastructure targets need a reason.** Choosing infrastructure transfers patching,
availability, and hardening back to the customer. In a supervised estate that transfer must
be justified, not defaulted to.

**Evidence outlives the engagement.** Artifacts are written for someone who was not there
and who is asking two years later.

## Stakeholders

As the default, plus:

| Role | Responsibility | Holds decision rights over |
| --- | --- | --- |
| Compliance officer | Owns the supervisory relationship | Evidence sufficiency, residency interpretation |
| Internal audit | Independent assurance | Whether the trail is reconstructable |

## Decision rights

As the default, with two changes:

- A policy exception additionally requires the compliance officer.
- Any residency interpretation is the compliance officer's decision, not the architect's.
