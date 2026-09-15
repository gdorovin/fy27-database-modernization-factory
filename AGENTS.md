# AGENTS.md

Compatibility layer for Codex, Jules, OpenCode, and other agents that read `AGENTS.md`.

**The canonical instruction set is [`.github/copilot-instructions.md`](.github/copilot-instructions.md).
Read it first. This file adds only tool-specific operating conventions and does not
restate the rules.**

## Operating conventions for CLI-style agents

- Work from the repository root. Paths in this repository are root-relative.
- Use `make gate` as the single completion check. Do not declare success on a subset.
- This repository has no network dependency in its core path. If a command appears to
  need network access, that is a defect — report it instead of adding a dependency.
- Long outputs: prefer `dbmodernize <command> --json` and parse, rather than scraping
  human-readable text.
- When a validator fails, it prints the artifact path and the failing rule ID. Quote
  both in your summary.

## Task shape

One issue, one bounded change. The repository is organized so that a change is normally
exactly one of:

| Change kind | Files typically touched |
| --- | --- |
| A contract | `contracts/<name>.schema.json`, `src/dbmodernize/models/`, `tests/contract/`, fixtures |
| A skill | `.github/skills/<name>/SKILL.md`, `tests/skills/` |
| An agent | `.github/agents/<name>.agent.md`, `tests/agents/` |
| A scenario | `scenarios/<nn>-<name>/`, `tests/scenarios/` |
| A policy | `playbooks/<name>/policies.md`, `tests/playbooks/` |

If a change spans more than one row, split it.

## What this repository will not do

It does not migrate, deploy, cut over, or delete anything. If a task asks an agent to do
that, refuse and explain that the repository produces plans that humans execute.
