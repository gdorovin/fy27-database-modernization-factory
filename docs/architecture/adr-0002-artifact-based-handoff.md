# ADR-0002: Agents hand off through artifacts, not conversation

- **Status:** accepted
- **Date:** 2026-09-15
- **Deciders:** architect, delivery lead
- **Consulted:** security owner

## Context

Eight agents cooperate across an engagement lifecycle. Each needs the previous one's output.

The obvious approach is conversational: the assessor summarises its findings, the architect
reads the summary, and so on. Every agent framework makes this the path of least resistance.

The constraint that makes it wrong: a modernization engagement is audited. Someone will ask,
possibly a year later and possibly under supervision, how a particular workload came to be
assigned a particular target. Conversation history cannot answer that. It cannot be diffed,
cannot be reviewed by someone who was not present, is not version-controlled, and disappears
when the session ends — which is exactly when the question gets asked.

There is a second, quieter problem. A summary is a lossy copy of something that already
exists, and the lossiness is invisible. An assessor that reports "four workloads, one
blocked" has dropped the evidence ids, the confidence levels, and the specific finding — all
of which the architect needs and none of which it can now see is missing.

## Options considered

### Option A — conversational handoff

Natural, fast, well supported by every framework. Each agent summarises for the next.

Costs: unauditable, lossy, unreviewable, and lost at session end. Also silently
context-window-bound: the earliest evidence falls out first, and nothing announces it.

### Option B — artifact handoff, passing content

Each agent writes a schema-valid artifact and passes its content to the next.

Better: durable and reviewable. But passing content re-creates the context problem at scale,
and encourages agents to re-serialise rather than reference.

### Option C — artifact handoff, passing paths

Each agent writes a schema-valid artifact and passes the **path**. The next agent reads what
it needs.

### Option D — a shared database

Durable and queryable. But it adds infrastructure, breaks the offline guarantee, and makes
the state invisible to `git diff` — which is the review mechanism everyone already has.

## Decision

**Option C.** Agents write schema-valid artifacts to disk and hand off paths. A handoff
message names the artifact; it does not summarise it.

The deciding fact: a reviewer six months later needs to reconstruct a decision without
talking to anyone. Files in version control support that. Nothing else in the option set
does, at any price.

## Consequences

### Accepted

- Every intermediate step must have a schema. That is upfront work, and it constrains what
  an agent can express.
- Agents cannot pass nuance that has no field. Where nuance matters it becomes an
  `assumption` or an `open_question`, which is more work and more useful.
- More disk I/O, which is irrelevant at this scale.
- Agent definitions must specify exactly which artifacts they read and write.

### Gained

- Any decision is reconstructable from files alone.
- `git diff` shows exactly what a change to the pipeline did to every output — which is how
  the scenario snapshots work at all.
- Sessions are resumable. State survives a crash, a restart, or a different person picking
  it up.
- No context-window limit on the state of an engagement.
- Handoff can be manual where a client has no handoff support, because the artifacts are the
  interface.
- Each agent is independently testable against a fixture artifact.

### Revisit when

- Schema maintenance becomes the dominant cost of adding a capability.
- An artifact type is needed that genuinely resists schematisation.

## Compliance and security impact

Directly supports the governance model: `IAM-002`-style least privilege and the no-self-approval rule needs an
artifact with a recorded author, and an approval needs something to hash. Neither works over
conversation.

Also reduces disclosure risk: an artifact has a classification field and can be excluded
from a repository, whereas a conversation transcript has neither.

No exception required.

## Verification

```bash
python -m pytest tests/integration/test_pipeline_and_cli.py -q
python -m pytest tests/agents -q
```

The first asserts the traceability chain resolves end to end. The second asserts every agent
declares a handoff section naming artifacts rather than summaries.
