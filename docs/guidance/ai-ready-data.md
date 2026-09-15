# AI-ready data

> **verified_on: 2026-09-15.** Deliberately names no product, service, or capability.
> Those change quickly, and none of them is what decides whether this works.

## The asymmetry that matters

A conventional report built on poor data **looks** wrong. Someone notices the total does not
add up, and investigates.

An assistant built on poor data **sounds** right. It answers fluently, with the same
confidence it has when it is correct, and nobody investigates because there is nothing to
notice.

That asymmetry is why data quality has to be measured before, not discovered after. It is
also why the cheapest answer in the whole engagement is often "not yet".

## Readiness is not migration

A clean migration says nothing about whether the data underneath can carry an intelligent
scenario. Conflating the two is the most common way these engagements disappoint: the
technical work succeeds, the demo works, and the thing quietly stops being used.

Assess them separately. Migration readiness is about the database. This is about the data.

## Seven dimensions

**Ownership.** Every entity in scope has exactly one named system of record, with a named
owner. An attribute with two systems of record has no correct answer — and an assistant will
confidently give one of them.

**Quality.** Completeness, consistency, duplication, timeliness. Measured, with numbers
recorded. Not "we think it's pretty good".

**Semantics.** Field names and coded values that mean what a reader would assume. A column
called `status` with eleven undocumented values is a correctness problem the moment anything
reasons over it.

**Security.** The access model must hold on the new path. A scenario that reaches data
around row-level controls is a data breach with a friendly interface.

**Retention and deletion.** Deletion obligations must propagate to every derived copy,
index, cache, and embedding. Derived copies are where deletion obligations go to die, and
the gap is discovered by a regulator rather than a test.

**Performance and concurrency.** Either the operational system has measured headroom for the
additional read pattern, or a separate serving path exists. Decide this explicitly; it is
not a consequence of the target.

**Operational access.** A supported path to the data that does not create yet another
uncontrolled copy.

## Verdicts

| Verdict | Means |
| --- | --- |
| Ready | All seven satisfied; scope the scenario |
| Ready with conditions | Gaps exist, each with an owner and a date |
| **Not ready** | A specific dimension fails; name it |

"Not ready" is a result, not a failure to deliver one. Two weeks of ownership work now costs
less than an unanswerable support question later, after an assistant has been giving one of
two addresses to customers for a month.

## Derived copies

An index, cache, or embedding built from source data **inherits the obligations** — retention,
deletion, purpose limitation — and **does not inherit the permissions**.

That sentence is the single most expensive misunderstanding in this space. The source
enforces row-level access; the derived copy usually does not, and the scenario built on it
reads the derived copy.

## What the repository will not say

No generated artifact asserts that an estate is AI-ready. The verdict is conditional by
construction, and it names its conditions.

Scenario 06 enforces this by asserting the **absence** of AI-readiness language, product
names, and capability claims in every generated document. It is an unusual kind of test, and
it exists because the failure mode here is enthusiasm rather than error.

## When the customer wants a date

Give them the gaps and the owners.

A date built on unmeasured data quality produces a demo in six weeks and a stalled programme
in six months. A date built on a closed ownership register produces something that survives
contact with real questions.

## Timing

Assess readiness **after** the platform is stable. Attaching an intelligent scenario to an
estate mid-migration adds a variable nobody can isolate when something misbehaves — and
something always misbehaves.

The cadence in the FY27 context page puts it at T+90 for exactly this reason.
