# ADR-0001: The core is deterministic and model-free

- **Status:** accepted
- **Date:** 2026-09-15
- **Deciders:** architect, security owner
- **Consulted:** delivery lead, field architect

## Context

The repository must turn estate evidence into target recommendations, waves, plans, and
issues. A language model could do this directly and would handle messy input far better than
any rule set.

The constraint that makes this non-obvious: a customer will challenge a recommendation
months later, often after money has been spent against it, and usually when the person who
made it has moved on. At that point the question is not "is this a good recommendation" but
"how was this reached, and does the reasoning still hold given what we now know".

A model-generated recommendation cannot answer that. It can produce a plausible explanation
after the fact, which is worse than no explanation, because it is indistinguishable from a
real one.

Evidence available at the time: none from this repository — the decision was taken before
implementation. The reasoning rests on assumption A-003 (rule-based scoring is sufficient for
target comparison), which the seven scenarios have since supported.

## Options considered

### Option A — model generates recommendations directly

Handles ambiguity well. Fast to build. Adapts to input nobody anticipated.

Costs: non-reproducible, so CI cannot assert behaviour; unauditable, so a challenge has no
answer; untestable, so safety properties become intentions; and it requires a model in the
merge gate, which makes the build flaky and teaches people to re-run until green.

### Option B — deterministic rules, no model in the core

Reproducible, auditable, testable. Every score reconstructable by hand from a published
table. CI can assert that identical inputs give identical outputs, which turns "the
behaviour changed" into a visible diff.

Costs: rules cannot read a PL/SQL package and judge that it will be difficult. Messy input
needs an adapter rather than tolerance. More code.

### Option C — deterministic core with model assistance at the edges

As B, plus skills and agents that guide a human or an assistant *through* the core. The model
contributes judgement where judgement is genuinely needed; the core holds what must not
drift.

### Option D — do nothing, use documents and templates

Zero enforcement. Every safety property becomes a guideline, and guidelines are followed
until the week they are inconvenient.

## Decision

**Option C.** The core is deterministic and has no model dependency. Skills and agents
provide judgement around it.

The deciding fact: three properties are unavailable in any model-generated design, and all
three are load-bearing.

1. **Reproducibility.** CI regenerates every scenario and fails on a diff. A behavioural
   change cannot land unnoticed.
2. **Auditability.** Every score comes from a published adjustment. A challenge has an
   answer that does not depend on anyone's recollection.
3. **Testability.** "A blocking failure forces no-go" is a unit test, not an intention.

If the deciding assumption is wrong — if rule-based comparison turns out to produce
recommendations a competent architect would reject — this decision should be revisited. The
signal would be scenarios where the rules pick a target the reviewer overrides.

## Consequences

### Accepted

- Rules cannot reason about code complexity, organisational politics, or anything requiring
  reading. Those stay with the human, guided by skills.
- New target platforms need scoring rules written by hand.
- Unanticipated input formats need an adapter, not tolerance.
- More code than a prompt.

### Gained

- The pipeline runs with no subscription, no database, no model, no network.
- CI is fast and never flaky.
- Any recommendation can be reconstructed from the evidence and the published table.
- Safety properties are enforced by types rather than by hoping.
- The tool is usable in an air-gapped or restricted environment.

### Revisit when

- Rule-based comparison produces recommendations reviewers routinely override.
- The number of targets makes hand-written rules unmaintainable.
- A model-based comparison can be made reproducible and auditable to the same standard.

## Compliance and security impact

Supports `COMP-002` (dated product claims) by keeping perishable facts in one reviewable
table with a `verified_on` date, rather than distributed through model weights where nobody
can find or date them.

No exception required.

## Verification

```bash
dbmodernize validate-scenario scenarios --update && git diff --exit-code
python -m pytest tests/unit/test_scoring.py -q
```

The first proves the pipeline is reproducible. The second proves the scoring adjustments are
the ones documented. `tests/integration` additionally asserts that the package imports no
cloud or database client library.
