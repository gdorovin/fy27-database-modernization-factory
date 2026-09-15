# FY27 field readiness

An appendix. Nothing here is a prerequisite for using this repository, and no certification
gates any feature. Keeping those separate is deliberate: software that requires a badge to
run is software nobody adopts.

## What actually helps

Ordered by how often it changes an outcome in practice, not by how it looks on a plan.

### 1. Reading an estate honestly

The single most valuable skill, and the least taught. It means noticing that an inventory of
two instances against a stated estate of twelve is the finding, not a starting point.

Practise: run Scenario 05 and read the assessment summary before the target decisions. The
interesting page is the blocking issues, not the workload table.

### 2. Knowing what each Azure target is actually for

Not the feature matrix — the question each target answers.

- Database scope: isolation, and no instance-scoped dependency.
- Instance scope: broad compatibility, instance-scoped capability in use.
- High scale: size or growth the evidence supports.
- Infrastructure: operating-system or engine control that is genuinely required.
- Arc: governance over something that is not moving yet.

Practise: read `scoring/targets.py` and reconstruct one recommendation by hand.

### 3. Heterogeneous migration realism

Understanding why "84% automatic" is the least interesting number in a conversion report,
and why an assessment against one target says nothing about another.

Practise: Scenario 04.

### 4. Cutover and rollback under pressure

Knowing that the rollback decision point is arithmetic — window minus measured rollback
duration — and that past it the correct action changes.

Practise: read a generated `rollback-plan-<n>.md` and ask what would be ambiguous at 03:00.

### 5. Saying "not yet"

To an AI ambition, a date, or a recommendation the evidence does not support. This is a
professional skill rather than a technical one, and it is the one that most often prevents a
bad outcome.

Practise: Scenario 06, and read what the executive brief says about what has not been
measured.

### 6. Engineering fluency

Git, pull requests, CI, code review. Increasingly the medium in which modernization work
actually happens, whoever is doing it.

### 7. AI assistance fluency

Prompting with scope, prohibition, and expected output. Reviewing generated work sceptically.
Knowing that "it compiles" is not a reason to accept.

See [prompt recipes](../copilot/prompt-recipes.md) and the
[review checklist](../copilot/review-checklist.md).

### 8. Data governance basics

System of record, ownership, classification, retention, deletion propagation. Unglamorous,
and decisive whenever an intelligent scenario is involved.

## Using this repository to learn

| To understand | Do |
| --- | --- |
| Why blocked workloads get no target | Scenario 01, then read the rationale |
| Why over-provisioning is a failure | Scenario 02 |
| Why extensions are not a detail | Scenario 03 |
| Why Oracle has no estate-wide answer | Scenario 04 |
| Why Arc is not progress | Scenario 05 |
| Why AI readiness is separate | Scenario 06 |
| What an honest failure report looks like | **Scenario 07** |

Scenario 07 is the one to read first if you only read one. It is what the repository is for.

## Certification

Role-aligned certification is worth planning against, and it is genuinely useful for
credibility with a customer. It is also not a proxy for the eight skills above, and treating
it as one produces certified people who still recommend a target before the dependencies are
known.

Plan it as career development, on its own timeline, separate from delivery capability.

## A note on the separation

This page is an appendix because tying readiness to product behaviour is a mistake that gets
made repeatedly. It produces documentation that reads like a training plan, software that
gates on a credential, and a repository that ages the moment a certification is renamed.

The tool works for whoever picks it up. That is the point.
