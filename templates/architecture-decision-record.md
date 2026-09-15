# ADR-<NNNN>: <short decision title>

- **Status:** proposed | accepted | superseded by ADR-<NNNN>
- **Date:** <YYYY-MM-DD>
- **Deciders:** <roles, not names>
- **Consulted:** <roles>
- **Supersedes:** <ADR id, or none>

## Context

What forced a decision. Include the constraint that makes this non-obvious — if there is
no tension, there is no decision to record.

State the evidence available at the time and its class (`observed`, `user-provided`,
`derived`, `assumption`). An ADR written from assumptions should say so plainly; it will
be read later by someone deciding whether the reasoning still holds.

## Options considered

### Option A — <name>

- What it is.
- Why it might be right.
- What it costs, in effort, risk, or optionality.

### Option B — <name>

As above.

### Option C — do nothing

Always consider it explicitly. "Retain" is a legitimate outcome, and writing down why it
was rejected is more useful than pretending it was never on the table.

## Decision

The option chosen, in one sentence.

Then the reasoning: the specific fact that made this option better than the others. If
the deciding fact is an assumption, say which one, and name what would have to be true
for the decision to flip.

## Consequences

### Accepted

- What gets harder, slower, or more expensive because of this.

### Gained

- What becomes possible or cheaper.

### Revisit when

- The condition that should trigger a re-read of this ADR.

## Compliance and security impact

Which playbook policies apply, and whether any exception is required. An exception needs
scope, justification, owner, approver, compensating controls, expiry, and review date.

## Verification

How anyone can check this decision was implemented as written — a command, a test, or a
named artifact.
