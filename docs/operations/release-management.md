# Release management

## Versioning

Semantic versioning against the **behaviour of the toolkit**, not the wording of the
guidance.

| Change | Bump |
| --- | --- |
| A breaking contract change | Major |
| A CLI exit code changes meaning | Major |
| An artifact field is removed or repurposed | Major |
| A new command, adapter, skill, or scenario | Minor |
| A scoring adjustment changes a recommendation | Minor, and call it out |
| A new optional field | Minor |
| A bug fix with no behavioural change | Patch |
| Documentation only | Patch |

A scoring change deserves attention even though it is only a minor bump: it changes what the
tool recommends, and someone may have a decision in flight that it would now contradict.

`SCHEMA_VERSION` in `dbmodernize/__init__.py` moves independently, so a stored artifact can
be checked against the contract that produced it.

## Releasing

1. `make gate` locally.
2. Update `CHANGELOG.md` with a `## [x.y.z]` section.
3. Bump `__version__` and `pyproject.toml`.
4. PR, reviewed per `CODEOWNERS`.
5. Tag `vx.y.z` on `main`.

The release workflow then re-runs the full gate, checks the tag matches the package version,
checks the changelog has a matching section, builds, verifies the wheel installs and the CLI
runs, attests provenance, and creates the release.

It uses no long-lived credential. Provenance attestation uses OIDC.

## The changelog is not optional

`CHANGELOG.md` is updated in the same PR as the behaviour change, not batched at release
time. Batched changelogs are written by someone reading commit messages a fortnight later,
and they read like it.

Entries say what changed and why it matters to someone using the tool. "Refactored scoring"
tells a reader nothing; "Hyperscale is now rejected where neither size nor growth justifies
it" tells them whether to re-check a decision.

## Breaking a contract

1. ADR explaining the necessity — a breaking change invalidates stored artifacts.
2. Bump the major `schema_version`.
3. Update the Pydantic model in the same commit.
4. Update every fixture and regenerate scenario expectations.
5. Note the migration path in the changelog.
6. Architect and security review per `CODEOWNERS`.

## What a release does not do

No publication to a package index, no deployment, no customer notification. Consumers pin a
tag and update deliberately.

## Supported versions

`main` is supported. Security fixes are not backported to tags — with a repository this
small, upgrading is cheaper than maintaining branches, and pretending otherwise creates an
obligation nobody has staffed.
