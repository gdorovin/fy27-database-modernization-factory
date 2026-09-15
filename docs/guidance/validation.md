# Validation

> **verified_on: 2026-09-15.** The check categories reflect what is commonly verifiable.
> Service-specific capabilities change; confirm the method for each check against current
> documentation.

## Three rules

Everything else on this page is detail. These three decide outcomes:

1. **A blocking check that fails forces `no-go`.** Not negotiable.
2. **A blocking check that has not run forbids `go`.** Not run is not a pass.
3. **`go` cannot rest on generated tests alone.** They are supporting evidence.

The Pydantic model enforces all three. A report claiming `go` with a blocking failure will
not serialize, so this survives a tired team at 04:00 as well as a fresh one at 10:00.

## Tolerances are agreed in advance

A check without a tolerance cannot distinguish pass from fail; "pass" becomes an opinion.

A tolerance agreed *after* seeing the result is a negotiation. It usually ends with the
threshold moving to wherever the observation landed, which is the same as having no
threshold — except that it now looks rigorous.

Where a check is genuinely a judgement call, it says so and names the owner who makes it.

## Coverage

Every generated plan covers, per wave:

| Group | Checks |
| --- | --- |
| Inventory and configuration | Workloads accounted for; target matches the approved design |
| Schema and data | Objects reconcile; row counts and checksums; types, precision, collation; referential integrity |
| Programmability | Stored procedures and functions behave identically |
| Application | Connectivity, functional, regression, integration |
| Performance | Latency and throughput against baseline; concurrency and locking |
| Availability | Failover; backup and restore; measured RPO and RTO |
| Security | Configuration, identity, network isolation, encryption, auditing, posture |
| Operations | Monitoring and alerting; runbooks; cost and sizing observation |
| Business | Owner acceptance |

Conversion adds a behaviour comparison and a business validation by named users. Compliance
scope adds control evidence. Extensions add a presence-and-version check.

## Generated tests

Mark them `generated_test: true`, and keep them non-blocking.

They are the most tempting number in a validation report: large, green, and produced
automatically. Four hundred and twelve auto-generated comparisons passing tells you the
conversion tool is internally consistent. It does not tell you the application behaves the
same way, because the generated cases were derived from the same source the conversion was.

Scenario 07 exists partly to hold this line: it contains a passing generated suite alongside
two blocking failures, and the outcome is `no-go`.

## Baselines

Captured before migration, as a prepare-phase task. Without one, "no regression" is an
assertion.

The baseline should cover what the business actually notices. For a billing platform that is
the overnight run, not average query latency — a 3% improvement in mean latency is no comfort
if the batch finishes after the business day.

## Recording results

Every completed check records an **observed value**. The model rejects a `pass` or `fail`
with no observation, which closes the most common shortcut: marking a check green because it
looked fine.

Where a check did not finish, record `not-run` with the reason. Partial reconciliation — 22
of 38 tables — is `not-run`, not a partial pass.

## Outcomes

| Outcome | Requires |
| --- | --- |
| `go` | All blocking checks passed; business and application owners accepted; not resting on generated tests |
| `conditional-go` | Non-blocking issues remain, each with a condition and an owner |
| `no-go` | Any blocking failure, or a blocking check that has not run |

A `no-go` must list corrective issue ids. A failure with no follow-up work is not a result.

## Running it

```bash
dbmodernize render-report --engagement input/engagement.yaml --input input \
  --report out/validation-report.json --out out
```

Exits non-zero on a `no-go`, so a pipeline cannot walk past one by accident.

## When the result is unwelcome

Report the evidence unchanged and escalate.

The cheapest moment to discover a regression is before the cutover. The most expensive is
after everyone has been told it went well — at which point the regression is competing with
a public statement, and the statement usually wins for a few weeks.
