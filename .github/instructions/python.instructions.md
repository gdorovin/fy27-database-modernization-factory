---
applyTo: "src/**/*.py,scripts/**/*.py,tests/**/*.py"
---

# Python

## Typing

- Strict mypy. Every function has annotated parameters and a return type.
- `from __future__ import annotations` at the top of every module.
- Prefer `X | None` over `Optional[X]`.
- Annotate collections precisely: `list[Finding]`, not `list`.
- Never use `Any` to silence a type error. If a value is genuinely dynamic, say so in a
  comment and narrow it at the boundary.

## Models

- Pydantic v2 for anything that crosses a contract boundary.
- Every model inherits `StrictModel`, so an unknown field is an error rather than a silent
  no-op.
- Cross-field invariants live in `@model_validator(mode="after")` with a message that
  explains *why* the rule exists, not just that it was broken.
- Enums are `StrEnum`, with values matching the JSON Schema exactly.

## Functions

- Small and pure where possible. A function that reads files, decides, and writes is three
  functions.
- Reach only for what is passed in. A scoring rule that reads the filesystem is not a rule.
- Return `FindingSet` from validators rather than raising, so every problem is reported in
  one pass instead of one per run.

## Errors

- Raise a `DbModernizeError` subclass so the CLI maps it to the right exit code.
- Messages name the artifact and what to do next. `"Invalid input"` helps nobody.
- Never swallow an exception. If it is genuinely expected, catch it narrowly and record a
  finding.

## Determinism

- Sort before serializing. Iteration order is not a contract.
- Never call `datetime.now()` in a code path that produces an artifact; time comes from the
  engagement's `as_of`.
- No randomness, no `hash()`, no locale-dependent formatting.
- Round explicitly where a float reaches an artifact.

## I/O

- Everything goes through `dbmodernize.utils.io`, which enforces UTF-8 and LF. Windows
  defaults to cp1252 and CRLF, and either would make generated artifacts differ between
  contributors.
- `yaml.safe_load` only. Never `yaml.load`, never `pickle`, never `eval`.
- Refuse to overwrite an existing file without `force=True`.

## Logging

- `get_logger(__name__)` from `dbmodernize.utils.logging`. It installs the redacting filter,
  so a caller cannot forget to redact.
- Log at `debug` for flow, `info` for outcomes, `warning` for degraded behaviour.
- Never log a value that came from an import without redaction.

## Security

- Untrusted input never becomes a path without `resolve_within`.
- Untrusted input never becomes a shell command, under any circumstances.
- No network calls in the core path. If one seems necessary, that is a design discussion,
  not an import.
