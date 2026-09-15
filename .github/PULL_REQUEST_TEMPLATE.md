# Pull request

Closes #

## What changed, and why

<!-- One paragraph. The "why" matters more than the "what"; the diff already shows the what. -->

## Scope

This pull request changes **one** of the following. If it changes more than one, split it.

- [ ] One contract
- [ ] One skill
- [ ] One agent
- [ ] One scenario
- [ ] One playbook policy
- [ ] Implementation within an approved plan
- [ ] Documentation only

## Commands run

<!-- Paste the actual output, not a claim that it passed. -->

```text
make gate
```

## Evidence and provenance

- [ ] Any new recommendation cites `evidence_refs`.
- [ ] Any gap filled to proceed is in an `assumptions` array with an owner and a validation
      step, not buried in prose.
- [ ] `confidence` reflects the evidence class rather than optimism.
- [ ] Any new artifact records the playbook path, version, and applied policy ids.

## Safety boundaries

- [ ] No secret, credential, connection string, endpoint, tenant id, subscription id, or
      customer identifier.
- [ ] All fixtures and examples are synthetic.
- [ ] No path that deploys, migrates, cuts over, or deletes anything.
- [ ] Any environment-changing task requires approval and documents a rollback.
- [ ] No zero-downtime claim. `near-zero-planned` appears only with a measured rehearsal.
- [ ] No cross-engine compatibility claim without conversion evidence for that target.
- [ ] No new product, pricing, support-status, or commercial claim — or, if one was
      necessary, it carries a `verified_on` date.

## Tests

- [ ] New or changed behaviour has a test that would fail without this change.
- [ ] Schema changes ship a passing **and** a failing fixture.
- [ ] Snapshot changes were reviewed line by line, not regenerated to silence a failure.
- [ ] Default CI still needs no Azure subscription, database, model, or paid API.

## Documentation

- [ ] Affected `docs/` page updated.
- [ ] README updated if the command surface changed.
- [ ] `CHANGELOG.md` updated.
- [ ] Diagrams still match the implementation.

## Reviewer notes

<!-- What should a reviewer look at hardest? Where are you least sure? -->

## Governance

Changes touching `contracts/`, `playbooks/`, `.github/agents/`, or a safety boundary need
two distinct owners per `CODEOWNERS`, and a review using the `governance-reviewer` agent.

- [ ] Governance review requested, or not applicable.
