# Governance

How decisions are made, who makes them, and what evidence a decision must carry.

## Principle

The repository generates **proposals**. Humans make **decisions**. Nothing in this
codebase can turn a proposal into an approved decision on its own, and no agent may
approve its own output.

## Decision rights

Full table in [`docs/governance/decision-rights.md`](docs/governance/decision-rights.md).
Summary:

| Decision | Proposed by | Decided by | Cannot be decided by |
| --- | --- | --- | --- |
| Engagement scope and outcomes | Engagement Orchestrator | Customer sponsor + engagement lead | Any agent |
| Workload classification | Estate Assessor | Data platform architect | The agent that proposed it |
| Azure target per workload | Target Architect | Architecture review (architect + app owner) | Target Architect |
| Business case acceptance | Value Advisor | Customer sponsor | Any agent |
| Wave composition and sequence | Migration Planner | Delivery lead + application owners | Any agent |
| Policy exception | Requester | Security + architect owners named in `CODEOWNERS` | The requester |
| Go / no-go for cutover | Validation Engineer (evidence) | Business, application, database, security, and operations owners — all five | Any agent |
| Rollback trigger | Validation Engineer | Delivery lead, per the documented trigger thresholds | Any agent |
| Playbook change | Any contributor | Architect owner + security owner | A single reviewer |

## Repository controls

- `CODEOWNERS` assigns ownership by area; governance areas require two distinct owners.
- The default branch is protected. No direct pushes; no self-merge of governance files.
- Required status checks: lint, format check, types, unit, contract, repository, skill,
  agent, playbook, and scenario tests.
- Releases are tagged and traceable to commits; release notes reference merged issues.
- Conventional Commits, enforced by review.
- `CHANGELOG.md` is updated in the same PR as the behavior change.
- Material architectural changes require an ADR under `docs/architecture/` using
  `templates/architecture-decision-record.md`.
- Playbook files are never edited directly on the default branch.

## Agent governance

Every agent and skill has:

- a named owner recorded in `CODEOWNERS`,
- a version and change history through Git,
- an explicit tool allowlist, validated in CI,
- a documented escalation path,
- an off switch: set `enabled: false` in the frontmatter, and the validator will treat it
  as disabled rather than deleting history.

Runtime expectations, for when this repository is wired into an agent runtime:

- A correlation ID flows through every step of an engagement and appears in every
  artifact.
- Long-running workflows checkpoint to artifacts on disk, not to conversation memory.
- Operations are idempotent; re-running a step must not duplicate artifacts.
- Retries are bounded and have explicit stop conditions.
- No agent may approve, and no agent may escalate its own tool set.

## Approval mechanics

An approval is an artifact conforming to `contracts/approval.schema.json`. It records the
approved artifact ID and content hash, the approving role, the principal, a timestamp,
the decision, and conditions. Validation fails when:

- the approver equals the artifact author or generating agent,
- the recorded content hash does not match the artifact,
- a cutover approval is missing any of the five required roles,
- an approval references an artifact whose status cannot legally transition.

## Status lifecycle

```
draft -> evidence-complete -> recommended -> reviewed -> approved
      -> implementation-ready -> validating -> accepted
                                            -> rejected
any    -> superseded
```

Transitions not in this graph fail validation. `recommended -> approved` additionally
requires a valid approval artifact.

## Policy exceptions

An exception requires scope, justification, owner, approver, compensating controls,
expiry date, and review date. Exceptions without an expiry are rejected. Expired
exceptions fail validation rather than lapsing quietly.

## Conflicts

Where two evidence sources, two policies, or two stakeholders disagree, the repository
records the conflict and blocks progression. It does not choose. Resolution is a human
decision and is captured as an ADR or an approval artifact.
