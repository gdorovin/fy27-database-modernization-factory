# Working with skills

Architecture is in [skill architecture](../architecture/skill-architecture.md). This page is
how to use them and why one might not fire.

## The seventeen

| Phase | Skills |
| --- | --- |
| Intake | `engagement-intake` |
| Discovery | `estate-discovery`, `evidence-normalization` |
| Assessment | `sql-server-modernization`, `postgres-mysql-modernization`, `oracle-heterogeneous-migration`, `modernization-classification` |
| Decision | `azure-target-recommendation`, `business-case` |
| Delivery | `landing-zone-readiness`, `migration-wave-planning`, `migration-plan-generation`, `cutover-and-rollback`, `migration-validation` |
| Closing | `ai-data-readiness`, `governance-compliance`, `executive-brief` |

## Letting selection happen

Describe the task in the vocabulary of the problem, not the solution:

```text
The customer has PostgreSQL 11 with PostGIS and wants to know whether they can move to
the managed service.
```

This should reach `postgres-mysql-modernization`. If it reaches `sql-server-modernization`,
that is a selection failure worth reporting — cross-family confusion is the classic error and
the skills carry explicit redirections to prevent it.

## Naming one explicitly

When the boundary is genuinely ambiguous:

```text
Use the migration-validation skill to evaluate Scenario 07. A failed integration test and a
material performance regression must lead to a no-go result.
```

Three parts worth copying: the skill, the scope, and the expected outcome. Stating the
expected outcome lets you tell the difference between "the skill worked" and "the model
agreed with me".

## Why a skill might not fire

| Symptom | Likely cause | Check |
| --- | --- | --- |
| Nothing fires | The description does not match your vocabulary | Read the `Invoke when` section |
| The wrong one fires | Two descriptions overlap | `dbmodernize validate-skill .github/skills` warns at 60% |
| It fires but ignores the procedure | The body is too long, or the sections are vague | Look for placeholder sections |
| It fires on the wrong platform | A cross-family redirection is missing | Check `Do not invoke when` |

`dbmodernize validate-skill` reports description overlap, missing redirections, and
placeholder sections. Most selection problems are visible there before you notice them in
practice.

## "Do not invoke when" is the useful half

Every skill names the alternative, and validation warns if it does not:

> **Do not invoke when**
> - The source is PostgreSQL, MySQL, or MariaDB — use `postgres-mysql-modernization` instead.
> - The comparison itself is being run — defer to `azure-target-recommendation`.

Telling a model what not to do without saying what to do instead leaves it improvising, which
is the behaviour the skill existed to prevent.

## Reading the output

A skill's `Output contract` says what it produces and against which schema. If what came back
does not match, the skill did not complete — treat that as a failure rather than a partial
result, and check the `Failure and fallback` section for what should have happened.

## Which skills refuse things

| Skill | Refuses |
| --- | --- |
| `engagement-intake` | An outcome that names a product |
| `azure-target-recommendation` | A destination for a blocked workload |
| `oracle-heterogeneous-migration` | Any compatibility claim without conversion evidence |
| `business-case` | Generating a figure |
| `migration-validation` | Counting an un-run check as a pass |
| `ai-data-readiness` | Declaring readiness without measured quality |
| `governance-compliance` | Approving anything |

If one of these complies when it should refuse, that is a defect worth an issue.

## Adding one

Write the description first. If you cannot distinguish it from every existing skill in one
sentence, it is not a new skill — it is a section of an existing one.

Then `Do not invoke when`, naming alternatives. Then the other nine sections, with no
placeholders. Then a case in `tests/evals/datasets/skill-selection.yaml`, and an entry in
`EXPECTED_SKILLS`.
