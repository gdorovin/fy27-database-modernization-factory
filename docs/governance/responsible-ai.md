# Responsible AI

This repository uses AI assistance to produce guidance that influences decisions about
customer systems. The controls below exist because that combination — plausible output,
consequential decisions — is where assistance stops being harmless.

## Where the risk actually is

Not that a model will do something dramatic. Nothing here can deploy, migrate, or delete.

The risk is quieter: **a model fills a gap with something plausible, and the plausible thing
becomes a fact nobody can trace.** An unknown version becomes a supported one. An
unmeasured baseline becomes a saving. A conversion percentage becomes a compatibility
verdict.

Each of those is a reasonable-looking sentence that survives review, gets quoted in a board
pack, and is discovered to be unfounded at the worst possible moment.

## Controls

### Determinism where it matters

Target recommendations, wave plans, and validation outcomes come from published rules, not
from a model. Every score is reconstructable by hand. See
[ADR-0001](../architecture/adr-0001-deterministic-core.md).

A recommendation only a model can produce cannot be defended when challenged, and it will be
challenged.

### Unknowns stay unknown

Enforced structurally. Support status cannot be derived from an unknown version — the model
rejects it. Cost figures are not generated. Downtime claims require a measurement.

Gaps live in `assumptions` with an owner and a validation step, or in `open_questions`. Never
in prose, where they are invisible to review.

### Provenance on every statement

Six evidence classes, explicit on every record. A recommendation that cites no evidence fails
validation. `confidence` is `low`/`medium`/`high` rather than a fabricated percentage,
because a percentage implies a calibration nobody performed.

### Humans decide

No agent can approve. No agent can approve agent-authored work. The strongest statement
available to the system is "ready for human approval".

Three gates — architecture review, go/no-go, business acceptance — and none can be passed by
anything in this repository.

### Imported text is data

Assessment exports are untrusted. Directive-like content is recorded as an
`InjectionFinding` and raises a blocking security finding. It is never obeyed.

Eight patterns are detected, including approval forgery — text claiming a database is
"pre-approved". Acting on that would let an export author grant approvals, which is exactly
the kind of privilege escalation that looks like a data-quality issue until someone thinks
about it.

### Refusals explain themselves

A refusal names the boundary and offers the safe alternative. A refusal with no reason leaves
the user guessing whether the request was impossible, forbidden, or misunderstood — and
guessing usually ends with them working around the control.

`tests/evals/datasets/refusal-boundaries.yaml` contains twelve refusal cases and two
compliance cases. The compliance cases matter: a dataset of refusals alone would reward a
system that refuses everything.

### Evaluation is honest about its limits

Thirteen rubric dimensions, each wired to a deterministic check that runs in the merge gate,
each separately describing what a model-based evaluator should look for.

Model-based evaluation runs in a **separate, non-gating** workflow. Gating merges on a
non-deterministic score makes the build flaky and teaches people to re-run until green, which
is worse than not evaluating.

When it does run, the evaluator configuration must differ from the generation configuration.
A model grading its own output measures self-consistency, not quality.

## What this repository will not claim

- That an estate is AI-ready. The verdict is conditional and names its conditions.
- That a migration will have zero downtime.
- That cross-engine code is compatible without conversion evidence for that target.
- That a saving exists against a baseline nobody measured.
- That a product is supported, in preview, or priced a particular way, without a date.

Scenario 06 asserts the **absence** of AI-readiness language in generated output. It is an
unusual test to write, and it exists because the failure mode here is enthusiasm.

## Fairness and transparency

The scoring table is published, in code, in a single file. Any recommendation can be
recomputed by hand. The rejected alternatives are recorded with their reasons.

A customer who disagrees with a recommendation can see exactly which adjustment produced it
and argue with that specific number, rather than with an opinion.

## Human oversight

| Point | Who |
| --- | --- |
| Accepting a target recommendation | Architect with application owner |
| Accepting a business case | Business owner |
| Go / no-go | All five owner roles |
| Accepting a risk | The named accepting role, with a date |
| Accepting AI readiness | Data owner and privacy officer |

## Reporting a concern

If the tooling produced something misleading, open an issue with a synthetic reproduction.
If it produced something that influenced a real decision, say so — that changes the urgency
from "fix the code" to "check who acted on it".
