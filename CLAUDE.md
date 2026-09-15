# CLAUDE.md

Compatibility layer for Claude Code.

**The canonical instruction set is [`.github/copilot-instructions.md`](.github/copilot-instructions.md).
Read it first. This file adds only tool-specific operating conventions and does not
restate the rules.**

## Operating conventions for Claude Code

- Start by reading `.github/copilot-instructions.md`, then the contract or skill you are
  about to touch. Do not generate before inspecting.
- Prefer `make` targets over ad-hoc commands so behavior matches CI exactly.
- `.github/skills/*/SKILL.md` files are Agent Skills. Their `Invoke when` and
  `Do not invoke when` sections are authoritative for selection; honour them rather than
  improvising a procedure.
- `.github/agents/*.agent.md` files declare a `tools` allowlist. Respect it. A read-only
  agent that edits a file is a governance failure, not a convenience.

## Plan mode

Use plan mode for anything touching `contracts/`, `playbooks/`, or `.github/agents/`.
Those three areas define the governance surface, and a silent change there invalidates
artifacts elsewhere in the repository.

## Refusals

Refuse and explain, rather than attempting, when asked to:

- run a migration, cutover, or rollback against a real system,
- create live GitHub issues without the explicit confirmation flag,
- deploy Azure infrastructure,
- insert a credential, connection string, or real customer export,
- approve an artifact that the same session produced.
