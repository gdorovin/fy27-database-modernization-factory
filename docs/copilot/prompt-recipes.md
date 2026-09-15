# Prompt recipes

Tested phrasings. The pattern that makes them work: **scope, prohibition, expected output.**
Omit the prohibition and a model will occasionally do something reasonable-looking and wrong.

## Orientation

```text
Read .github/copilot-instructions.md and docs/architecture/overview.md.
Summarise what this repository does, what it refuses to do, and where the safety
properties are enforced. Do not edit anything.
```

If the summary does not mention that it produces plans rather than executing them, the
instructions are not landing.

## Planning a change

```text
Inspect the repository instructions, the active playbook, the relevant contracts, the
existing tests, and the current implementation. Produce a file-by-file plan for issue <n>.
Identify assumptions, security concerns, affected schemas, tests to add, and the commands
that must pass. Do not edit any file yet.
```

## Implementing

```text
Implement the approved plan for issue <n>. Stay within the listed files. Add or update tests
before declaring completion. Run: make format && make lint && make typecheck && make test &&
make validate. Do not make production calls. Do not introduce secrets. Summarise changed
files, commands run, and any remaining gaps.
```

## Governance review

```text
Review this pull request using the governance-reviewer agent. Check tool privilege, secrets,
untrusted-input handling, evidence provenance, playbook compliance, approval boundaries,
rollback behaviour, and test quality. Do not edit any file. Return blocking findings,
non-blocking findings, and the evidence for each.
```

## Reviewing a generated plan

```text
Review the generated migration plan and validation report. Confirm that every recommendation
links to evidence, every risk has an owner, every environment-changing task requires
approval and documents rollback, and every rollback criterion is testable rather than a
judgement call. List anything that would be ambiguous at 03:00.
```

That last sentence is the useful one. It reliably surfaces criteria that read fine in
daylight and become arguments under pressure.

## Target comparison

```text
Use the azure-target-recommendation skill to evaluate the normalized workloads in
scenarios/01-sql2016-to-managed-instance. Do not modify the approved playbook. Produce a
target decision artifact and list every unresolved evidence gap.
```

## Validating a failure

```text
Use the migration-validation skill to evaluate Scenario 07. A failed integration test and a
material performance regression must lead to a no-go result. Confirm the report contains no
success language and that the un-run reconciliation is not counted as a pass.
```

## Adding an adapter

```text
Add an adapter for <format> in src/dbmodernize/adapters/. Subclass EvidenceAdapter, build
records through self._record so injection scanning applies, and override supports() to
discriminate on document shape. Add a synthetic fixture and a unit test asserting the
evidence class and source_ref. Do not change any existing adapter.
```

## Adding a scenario

```text
Create scenario <nn>-<name>. Write the README first, stating which mistake the scenario
prevents. Create synthetic input only. Write at least five acceptance criteria including one
negative. Generate expectations with --update and summarise what they contain. Do not modify
any other scenario.
```

## Explaining a decision to a customer

```text
Read out/target-decisions.json. For workload <id>, explain in plain language why the
recommended target was chosen and why each alternative was not, citing the evidence. Do not
introduce any fact absent from the artifact.
```

## Anti-recipes

These reliably produce bad output:

```text
Build the whole repository.
```
Unreviewable. One issue, one bounded change.

```text
Fix the failing test.
```
Invites deleting it. Say what the correct behaviour is.

```text
Make the scenario pass.
```
Invites regenerating the snapshot. Say what the output should be and why.

```text
Estimate the saving.
```
Refused, correctly. Supply a source or accept an empty cell.

```text
Just make it work.
```
"Just" is doing a lot of load-bearing work in that sentence.

## The general pattern

| Part | Example |
| --- | --- |
| Scope | "in `scenarios/01-.../`", "within the listed files" |
| Prohibition | "do not modify the playbook", "do not edit any file" |
| Expected output | "produce a target decision artifact and list unresolved gaps" |

All three, every time. The prohibition is the one people drop, and it is the one that
prevents the model from helpfully improving something you did not ask it to touch.
