# Issue-driven development

One issue, one bounded change. Never "build the repository" in a single issue — the result is
unreviewable, and unreviewable work is accepted on trust rather than inspection.

## What an issue must contain

| Section | Why |
| --- | --- |
| Context | Why this is needed; what goes wrong without it |
| Files in scope | An explicit list. Anything outside it is scope creep |
| Acceptance criteria | Checkable, not aspirational |
| Tests | Which ones to add, and what they assert |
| Commands | What must pass |
| Safety constraints | Boundaries this change must not weaken |
| Documentation impact | Which pages change |

The file list is the part that most often gets omitted and most often causes trouble. Without
it, "implement the plan" and "improve the module" are indistinguishable to a model.

## Shape of a change

A PR should be exactly one of these. If it is more, split it.

| Change | Files typically touched |
| --- | --- |
| A contract | `contracts/`, `models/`, `tests/contract/`, fixtures |
| A skill | `.github/skills/<name>/SKILL.md`, `tests/skills/` |
| An agent | `.github/agents/<name>.agent.md`, `tests/agents/` |
| A scenario | `scenarios/<nn>-<name>/`, `tests/scenarios/` |
| A policy | `playbooks/<name>/policies.md`, `tests/playbooks/` |
| Implementation | `src/`, `tests/` |

## Plan first

```text
Inspect .github/copilot-instructions.md, the active playbook, the relevant contracts, the
existing tests, and the current implementation. Produce a file-by-file plan for issue <n>.
Identify assumptions, security concerns, affected schemas, tests to add, and the commands
that must pass. Do not edit any file yet.
```

Review the plan before implementation. Specifically check that it touches only the files the
issue names, that it adds tests rather than only code, and that it has not decided to
"improve" something adjacent.

Material architectural decisions become ADRs before implementation, not after — an ADR
written afterwards documents what happened rather than why it was chosen.

## Then implement

```text
Implement the approved plan for issue <n>. Stay within the listed files. Add or update tests
before declaring completion. Run: make format && make lint && make typecheck && make test
&& make validate. Do not make production calls. Do not introduce secrets. Summarise changed
files, commands run, and any remaining gaps.
```

"Summarise remaining gaps" is worth keeping. A model that has taken a shortcut will usually
say so when asked directly, and will not volunteer it otherwise.

## Then review, with a different agent

```text
Review this pull request with the governance-reviewer agent. Check tool privilege, secrets,
untrusted-input handling, evidence provenance, playbook compliance, approval boundaries,
rollback behaviour, and test quality. Do not edit any file.
```

The agent that wrote the code is the worst reviewer of it, for the same reason the author of
a decision cannot approve it.

## Generated engagement issues

`dbmodernize generate-issues` produces definitions **to disk**. `--create` is refused by
design, because a dry run should never be able to surprise a repository with fifty new
issues.

Each generated issue carries: title, engagement and workload ids, problem statement, source
evidence, approved target, playbook version, dependencies, scope, out of scope, acceptance
criteria, validation commands, security considerations, rollback considerations, owner role,
labels, milestone, blocked-by links, and definition of done.

Review `issues.yaml`, then create them however your team prefers.

## Definition of done

- [ ] Scoped to one contract, skill, agent, scenario, or policy.
- [ ] Tests added that would fail without the change.
- [ ] `make gate` passes.
- [ ] No secret, customer datum, or real identifier.
- [ ] Safety boundaries intact.
- [ ] Documentation and `CHANGELOG.md` updated.
- [ ] No undated product or commercial claim.
- [ ] Reviewed by a different agent or person.
