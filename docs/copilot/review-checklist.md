# Review checklist

For reviewing Copilot-assisted changes. Ordered by how often each catches something.

## Before reading the code

- [ ] Does the PR link an issue?
- [ ] Is it **one** change — one contract, skill, agent, scenario, or policy?
- [ ] Do the changed files match the issue's scope list?

Scope creep is the most common problem and the easiest to spot. A twelve-file diff on a
one-file issue does not need reading in detail; it needs splitting.

## The diff

- [ ] Every changed file is explicable from the issue.
- [ ] No unrelated refactoring, reformatting, or import reshuffling.
- [ ] No new dependency without a stated reason.
- [ ] No `# type: ignore`, `# noqa`, or `--no-verify` without an explanation.

## Tests

- [ ] New behaviour has a test that would **fail without the change**. Check this by reading
      the assertion, not by counting tests.
- [ ] Assertions check values, not merely absence of exceptions.

  ```python
  assert decision is not None                                    # weak
  assert decision.recommended_target is AzureTarget.SQL_MANAGED_INSTANCE  # strong
  ```

- [ ] A schema change ships both a passing and a failing fixture.
- [ ] A failing fixture fails for the **intended** reason — `expected-reasons.json` pins it.
- [ ] Snapshot changes were reviewed line by line, not regenerated to go green.
- [ ] Nothing in the default gate needs a subscription, database, model, or paid API.

The snapshot one is worth being difficult about. `--update` is one keystroke, and it makes
any failure disappear.

## Safety

- [ ] No credential, connection string, endpoint, tenant id, subscription id, or customer
      identifier.
- [ ] Fixtures are synthetic.
- [ ] No path that deploys, migrates, cuts over, or deletes.
- [ ] Environment-changing tasks still require approval and document rollback.
- [ ] No zero-downtime claim in any wording.
- [ ] No cross-engine compatibility claim without conversion evidence for that target.
- [ ] Imported content is still treated as data.
- [ ] Agent tool allowlists unchanged, or the change is justified.

## Evidence and provenance

- [ ] New recommendations cite `evidence_refs`.
- [ ] Gaps appear in `assumptions` with an owner and a validation step, not in prose.
- [ ] `confidence` reflects the evidence class rather than optimism.
- [ ] New artifacts record playbook path, version, and policy ids.
- [ ] Unknowns are recorded as unknown.

## Claims

- [ ] No new pricing, funding, eligibility, or preview claim.
- [ ] Any perishable claim carries `verified_on`.
- [ ] No cost or saving figure without a named human source.

## Documentation

- [ ] Affected `docs/` page updated.
- [ ] README updated if the command surface changed.
- [ ] `CHANGELOG.md` updated, saying what it means to a user.
- [ ] Diagrams still match the implementation.
- [ ] Every command shown actually works.

## Governance

For anything touching `contracts/`, `playbooks/`, `.github/agents/`, or a safety boundary:

- [ ] Two distinct owners per `CODEOWNERS`.
- [ ] Reviewed with the `governance-reviewer` agent.
- [ ] A breaking contract change ships an ADR.
- [ ] No new path to self-approval.

## Commands

```bash
make gate
```

Read the output. "CI is green" is a claim about a machine; reading the output is a claim
about the change.

## Things that are not reasons to approve

- It compiles.
- The tests pass. *(Do they test anything?)*
- CI is green. *(Did you read it?)*
- It looks like the existing code. *(Is the existing code right?)*
- The model said it was done.

## When you are unsure

Ask the author to explain the change in two sentences without referring to the diff. If they
cannot, neither can the next person to read it.
