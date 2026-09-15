# Documentation

Start with the [README](../README.md) if you have not read it. This index is for finding the
page you need once you know what you are doing.

## By question

| Your question | Page |
| --- | --- |
| How does this repository fit together? | [Architecture overview](architecture/overview.md) |
| How do the agents hand off to each other? | [Agent architecture](architecture/agent-architecture.md) |
| Why is a skill not being selected? | [Skill architecture](architecture/skill-architecture.md) |
| Where does an artifact come from? | [Artifact and evidence flow](architecture/artifact-flow.md) |
| What stops this doing something dangerous? | [Security architecture](architecture/security-architecture.md) |
| Why does FY27 care about database modernization? | [FY27 context](guidance/fy27-context.md) |
| How do I assess an estate? | [Discovery and assessment](guidance/discovery-and-assessment.md) |
| How is a target chosen? | [Target selection](guidance/target-selection.md) |
| How do I sequence the work? | [Migration waves](guidance/migration-waves.md) |
| What happens on the night? | [Cutover and rollback](guidance/cutover-and-rollback.md) |
| How do we know it worked? | [Validation](guidance/validation.md) |
| Can we put an assistant on this data? | [AI-ready data](guidance/ai-ready-data.md) |
| How do I run the tool day to day? | [Runbook](operations/runbook.md) |
| Something broke in an engagement | [Incident response](operations/incident-response.md) |
| How do I use Copilot here? | [Getting started with Copilot](copilot/getting-started.md) |
| Who decides what? | [Decision rights](governance/decision-rights.md) |
| How do I change a policy? | [Policy management](governance/policy-management.md) |
| What are the responsible-AI controls? | [Responsible AI](governance/responsible-ai.md) |
| What should I learn this year? | [FY27 field readiness](readiness/fy27-field-readiness.md) |

## By role

**Field architect.** [FY27 context](guidance/fy27-context.md) →
[Target selection](guidance/target-selection.md) →
[Decision rights](governance/decision-rights.md) → the [playbooks](../playbooks/README.md).

**Delivery lead.** [Migration waves](guidance/migration-waves.md) →
[Cutover and rollback](guidance/cutover-and-rollback.md) →
[Validation](guidance/validation.md) → [Runbook](operations/runbook.md).

**Contributor.** [CONTRIBUTING.md](../CONTRIBUTING.md) →
[Architecture overview](architecture/overview.md) →
[Issue-driven development](copilot/issue-driven-development.md) →
[Review checklist](copilot/review-checklist.md).

**Security reviewer.** [SECURITY.md](../SECURITY.md) →
[Security architecture](architecture/security-architecture.md) →
[Risk and approvals](governance/risk-and-approvals.md) →
[Responsible AI](governance/responsible-ai.md).

**Sponsor or customer-facing lead.** The README, then
[FY27 context](guidance/fy27-context.md), then a generated executive brief from a scenario.

## Conventions

- Perishable claims — support status, limits, preview state, pricing — carry a
  `verified_on` date. Repository validation enforces this for `docs/guidance/`.
- Diagrams are Mermaid, in the Markdown, updated in the same change as the implementation.
- Every command shown works; `dbmodernize validate-repo` checks the README against the real
  command surface.
- Links are relative and are checked by `scripts/check_links.py`.

## Decisions

Architectural decisions are recorded as ADRs under [architecture/](architecture/), using
[the template](../templates/architecture-decision-record.md). The two that shape everything
else are
[ADR-0001](architecture/adr-0001-deterministic-core.md) and
[ADR-0002](architecture/adr-0002-artifact-based-handoff.md).
