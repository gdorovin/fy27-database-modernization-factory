---
name: migration-validation
description: Define and evaluate the technical and business acceptance checks a go or no-go decision rests on, with tolerances, recorded observations, and outcome rules that a failure cannot be argued past.
---

# Migration validation

Produces the evidence a go decision rests on. Three rules do most of the work, and all three
exist because each has been ignored somewhere and cost someone a weekend.

## Invoke when

- A wave needs its validation plan.
- Validation has run and the results need recording and judging.
- A go or no-go decision is being taken.
- A failed attempt needs an accurate record.

## Do not invoke when

- Platform readiness is the question — use `landing-zone-readiness` instead.
- Cutover mechanics are the question — defer to `cutover-and-rollback`.
- The estate has not been migrated yet and the question is design — use
  `azure-target-recommendation` instead.

## Required inputs

| Input | Source | Required |
| --- | --- | --- |
| Migration plan and its wave | `migration-plan-generation` | Yes |
| Source performance baseline | Prepare phase | Yes |
| Agreed tolerances | Business and database owners | Yes |
| Application test suites | Application owner | Yes |
| Confirmed dependency list | Assessment | Yes |
| Compliance control requirements | Security owner | Where applicable |

## Preconditions

1. A baseline exists. Without one, "no regression" is an opinion.
2. Tolerances are agreed in advance. A tolerance agreed after the result is a negotiation.
3. Every check names a verification method specific enough for someone else to repeat.

## Procedure

1. Generate the plan for the wave. It covers inventory, configuration, schema, data
   reconciliation, types, referential integrity, programmability, connectivity, functional,
   regression, integration, performance, concurrency, availability, backup and restore, RPO
   and RTO, security configuration, identity, network isolation, encryption, auditing,
   posture, cost and sizing, monitoring, runbooks, and business acceptance.
2. Add conversion-behaviour checks where code was converted, including business validation
   by named users.
3. Add compliance control evidence checks for regulated workloads.
4. Execute every check and record the observed value against its tolerance.
5. Apply the outcome rules:
   - a blocking check that **fails** forces `no-go`,
   - a blocking check that **has not run** forbids `go`,
   - `go` also requires business and application owner acceptance,
   - `go` cannot rest on generated tests alone.
6. On `no-go`, create a corrective issue per failure, each with an owner.

## Decision points

| Result | Outcome | Note |
| --- | --- | --- |
| All blocking checks pass, acceptance recorded | `go` | The only path to go |
| Any blocking check fails | `no-go` | Not negotiable; the threshold already decided |
| A blocking check has not run | `conditional-go` or `no-go` | Partial evidence is not evidence |
| Non-blocking check fails | `conditional-go` with a condition | Record the condition and its owner |
| Only generated tests passed | Not `go` | Generated tests are supporting evidence |
| Regression within tolerance | Pass, and record the number | The number matters later |

## Output contract

A validation report validating against `contracts/validation-report.schema.json`. Every
completed check records an observed value. Generated tests carry `generated_test: true`.
The outcome follows the rules above, and the model enforces that — a report claiming `go`
with a blocking failure will not serialize.

A `no-go` report must list corrective issue ids. A failure with no follow-up work is not a
result.

## Validation

```bash
dbmodernize render-report --engagement input/engagement.yaml --input input --report input/validation-report.json --out out
dbmodernize validate-scenario scenarios/07-failed-validation-and-rollback
```

`render-report` exits non-zero on a no-go, so a pipeline cannot proceed past one by
accident.

## Failure and fallback

- **A check cannot be run in time.** Record `not-run` with a reason. Never record a
  convenient pass; that is the failure this whole skill exists to prevent.
- **Reconciliation is partial.** Partial reconciliation is `not-run`, not a partial pass.
- **Tolerance disputed after the result.** Record both the agreed tolerance and the
  observation, and escalate. Changing the threshold to fit the result is not a decision.
- **Business acceptance not reached.** `go` is unavailable. Say so plainly.

## Avoid

- Counting a check that did not run as a pass.
- Letting a generated test suite carry a verdict.
- Describing a rolled-back attempt as a success, a partial success, or "successfully
  completed with issues".
- Recording a result without the observed value.
- Softening a no-go into "go with conditions" when a blocking check failed.

## Example

Nine checks. Six pass, two blocking checks fail, one blocking check did not finish. A
generated suite of 412 comparisons passed cleanly.

The outcome is `no-go`. The generated suite appears in the report marked as a generated
test and explicitly described as supporting evidence only. Three corrective issues are
created with owners, and the report says at the top that nothing in it should be read as a
partial success.
