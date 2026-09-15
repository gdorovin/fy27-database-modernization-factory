# Contributing

Thank you for improving the FY27 Database Modernization Factory. Read
[`.github/copilot-instructions.md`](.github/copilot-instructions.md) first — it is the
canonical rule set, and this file only covers process.

## Setup

```bash
git clone <this-repo>
cd fy27-database-modernization-factory
make install-dev
pre-commit install
make gate
```

A Dev Container is provided. Open the folder in VS Code and choose
**Reopen in Container**; `scripts/bootstrap.sh` runs automatically.

## Change shape

Prefer pull requests that implement **one** contract, **one** skill, **one** agent, or
**one** scenario, with tests and documentation, and that are easy to revert. Avoid
unrelated refactoring; it makes review and rollback harder and hides the real change.

Every PR links to an issue. Issues carry context, in-scope files, acceptance criteria,
tests, commands, safety constraints, and documentation impact.

## Commit convention

Conventional Commits.

```
feat(contracts): add supersedes link to target-decision
fix(scoring): treat unknown edition as a blocker rather than a penalty
docs(guidance): date the Hyperscale claim and add verified_on
test(scenarios): cover the rollback path in scenario 07
chore(ci): pin actions to commit SHAs
```

Scopes in use: `contracts`, `models`, `policies`, `scoring`, `renderers`, `evidence`,
`adapters`, `issues`, `cli`, `skills`, `agents`, `playbooks`, `scenarios`, `docs`,
`ci`, `infra`, `tests`.

## Adding a contract

1. Write `contracts/<name>.schema.json`. Include `title`, `description`, `$id`,
   `examples`, and `additionalProperties: false` on every object.
2. Add the matching Pydantic model in `src/dbmodernize/models/`.
3. Add fixtures: at least one valid under `tests/fixtures/valid/<name>/` and one
   invalid under `tests/fixtures/invalid/<name>/`. Invalid fixtures are named after the
   rule they violate.
4. Contract tests pick fixtures up automatically by directory convention.

Schema changes must be backward compatible within a major `schema_version`. A breaking
change bumps the major version and adds an ADR.

## Adding a skill

1. Create `.github/skills/<lowercase-hyphenated-name>/SKILL.md`.
2. Frontmatter requires `name` (matching the directory) and `description`.
3. The body requires all eleven sections. `dbmodernize validate-skill` enforces this.
4. Add invoke / do-not-invoke fixtures to `tests/skills/` so selection is tested, not
   assumed.
5. Keep the description short and semantically distinct. Two skills that could plausibly
   answer the same request is a design bug.

## Adding an agent

1. Create `.github/agents/<name>.agent.md` with frontmatter `name`, `description`,
   `tools`, and `target`.
2. Grant the least-privileged tool set that still lets the agent do its job.
3. Declare objective, inputs, outputs, permitted decisions, decisions needing human
   approval, and escalation behavior.
4. Read-only agents must not list editing tools. `dbmodernize validate-agent` enforces
   this against the role table in `docs/governance/decision-rights.md`.

## Adding a scenario

Scenarios are executable fixtures. Each has `input/` and `expected/`, and every expected
artifact is committed so regressions appear in the diff. Run
`dbmodernize validate-scenario scenarios/<nn>-<name>` before pushing.

If you change a renderer, regenerate expectations with
`dbmodernize validate-scenario scenarios --update` and review every line of the diff.
Never regenerate to make a failure disappear.

## Playbook changes

`playbooks/*/charter.md`, `targets.md`, and `policies.md` are the governance contract.
They require architect and security review per `CODEOWNERS`, a scenario test, and a
change note in `CHANGELOG.md`. Direct pushes to `main` are blocked.

## Review expectations

Do not approve a change because it compiles. Check the diff scope, run the commands, read
the assertions, confirm documentation matches implementation, and confirm that no secret,
customer datum, or undated product claim slipped in.

For anything touching governance, evidence handling, or safety boundaries, request a
review from a second agent or person using the `governance-reviewer` agent.
