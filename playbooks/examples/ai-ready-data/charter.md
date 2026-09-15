# AI-ready data playbook — charter

version: 1.0.0

For an estate where the stated destination includes analytics, vector search, an assistant,
or an agent over operational data. The database modernization is the easy half. The hard
half is telling the customer honestly whether their data can carry the thing they want to
build on it.

## Scope

Database workloads intended to serve an intelligent scenario, and the data governance
questions that scenario depends on.

Explicitly in scope, because these are what actually decide the outcome:

- System of record per entity, and who owns it.
- Measured data quality: completeness, consistency, duplication, timeliness.
- Whether the access model still holds when data is reached by a new path.
- Whether deletion obligations propagate to derived copies, indexes, and embeddings.

## Outcomes

1. **The customer gets an honest readiness verdict**, including "not yet" with the specific
   gap named.
2. **Data ownership is settled before anything is built on it.** An attribute with two
   systems of record has no correct answer, and an assistant will confidently give one.
3. **The access model holds on every path.** A scenario that bypasses row-level controls is
   a data breach with a friendly interface.
4. **Deletion obligations survive.** Derived copies are where deletion obligations go to
   die, and that is a compliance exposure rather than a technical debt item.

## Principles

Everything in the default playbook, plus:

**Readiness is separate from migration.** A clean migration says nothing about whether the
data underneath is fit to answer questions. Conflating the two is the most common way this
kind of engagement disappoints.

**Poor data does not degrade gracefully.** A conventional report with bad data looks wrong.
An assistant with bad data sounds right. That asymmetry is why quality has to be measured
before, not discovered after.

**"Not yet" is the cheapest answer in the engagement.** Two weeks of ownership work now, or
an unanswerable support question and a loss of trust later.

**No generated artifact claims AI readiness.** The verdict is conditional by construction
and names its conditions.

## Stakeholders

As the default, plus:

| Role | Responsibility | Holds decision rights over |
| --- | --- | --- |
| Data owner | Owns an entity and its quality, as an ongoing duty | System of record, quality thresholds |
| Privacy officer | Owns deletion and purpose-limitation obligations | Whether a derived copy is permissible |

## Decision rights

As the default, with two additions:

- The readiness verdict is the data owner's and privacy officer's jointly. It is not an
  architecture decision.
- Proceeding despite a "not ready" verdict requires a named risk acceptor and a date.
