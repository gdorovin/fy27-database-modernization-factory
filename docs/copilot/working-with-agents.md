# Working with agents

Architecture is in [agent architecture](../architecture/agent-architecture.md). This page is
how to actually use them.

## Pick by what you need done

| You want to | Agent | It will refuse to |
| --- | --- | --- |
| Know where the engagement stands | `engagement-orchestrator` | Decide anything technical |
| Assess an estate | `estate-assessor` | Resolve a conflict, or declare dependencies complete |
| Compare Azure targets | `target-architect` | Approve its own recommendation |
| Build a business case | `value-advisor` | Generate a figure |
| Plan waves and issues | `migration-planner` | Execute anything |
| Write code | `implementation-engineer` | Change production, or deviate from the plan |
| Validate an outcome | `validation-engineer` | Soften a failure |
| Review before approval | `governance-reviewer` | Approve, or fix a finding |

The refusal column is the more useful half of this table. Knowing what an agent will not do
tells you when you have picked the wrong one.

## Handoffs

Pass paths, not summaries:

```text
Assessment complete. The estate assessor wrote:
  out/evidence.json
  out/workloads.json
  out/risks.json
Three workloads are recommendation-ready; one has a blocking dependency finding.

Use the target-architect agent to compare targets for the ready workloads.
```

The reason is in [ADR-0002](../architecture/adr-0002-artifact-based-handoff.md): a summary
is lossy in ways that are invisible, and conversation history cannot be reviewed by someone
who was not there.

## Without handoff support

Not every client shows handoff buttons. Run the sequence manually — the artifacts are the
interface, so nothing depends on the host's features:

```bash
dbmodernize assess --engagement input/engagement.yaml --input input --out out
# then, with the target-architect agent selected, point it at out/workloads.json
```

## Escalation, and why it looks unhelpful

Every agent escalates rather than improvising. A missing input is named, not synthesised. A
conflict is surfaced, not resolved. Another agent's failing output is returned with the rule
quoted, not repaired.

This reads as unhelpful the first time. It is the property that makes the output trustworthy:
an agent that quietly fills a gap to keep things moving produces a result nobody can trace,
and the gap surfaces later as a surprise rather than a question.

## Boundaries you will meet

**"I cannot recommend a target for this workload."** It has a blocking finding. The agent
will offer a governed interim posture and name the evidence needed.

**"I cannot approve this."** No agent can. The governance reviewer can say "ready for human
approval", which is the strongest statement available.

**"That would change a production environment."** Refused without an approval artifact naming
all five owner roles.

**"I would need to generate a figure."** The value advisor will not. Give it a source, or
accept an empty cell with an owner.

## Reviewing agent output

Use a different agent than the one that produced it:

```text
Review this pull request with the governance-reviewer agent. Check tool privilege, secrets,
untrusted-input handling, evidence provenance, playbook compliance, approval boundaries,
rollback behaviour, and test quality. Do not edit any file. Return blocking findings,
non-blocking findings, and the evidence for each.
```

## Extending the set

Decide what the agent may **not** do first — that determines the tool list, and the tool list
is the only part the validator can enforce. Then write the eight required sections, register
it in the tests, and wire it into the orchestrator's handoff table.

If it overlaps an existing agent, that is a design problem. Two agents that could handle the
same step make routing unpredictable, and the symptom is a workflow that behaves differently
depending on who ran it.
