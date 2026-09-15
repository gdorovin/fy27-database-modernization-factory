"""Error types and exit codes.

Exit codes are part of the CLI contract and are asserted in tests. Changing one is a
breaking change.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum


class ExitCode(IntEnum):
    """Process exit codes for the ``dbmodernize`` CLI."""

    OK = 0
    VALIDATION_FAILED = 1
    USAGE_ERROR = 2
    INPUT_NOT_FOUND = 3
    OUTPUT_EXISTS = 4
    POLICY_VIOLATION = 5
    SAFETY_REFUSAL = 6
    INTERNAL_ERROR = 70


@dataclass(frozen=True, slots=True)
class Finding:
    """A single validation result.

    ``rule`` is a stable identifier so that tests and reviewers can refer to a specific
    check rather than to a message string.
    """

    rule: str
    message: str
    path: str
    severity: str = "error"
    hint: str | None = None

    def render(self) -> str:
        location = self.path or "<repository>"
        base = f"[{self.severity}] {self.rule} {location}: {self.message}"
        return f"{base}\n    hint: {self.hint}" if self.hint else base

    def as_dict(self) -> dict[str, str]:
        out = {
            "rule": self.rule,
            "message": self.message,
            "path": self.path,
            "severity": self.severity,
        }
        if self.hint:
            out["hint"] = self.hint
        return out


@dataclass(slots=True)
class FindingSet:
    """An ordered, deduplicated collection of findings."""

    findings: list[Finding] = field(default_factory=list)

    def add(
        self,
        rule: str,
        message: str,
        path: str = "",
        severity: str = "error",
        hint: str | None = None,
    ) -> None:
        candidate = Finding(rule=rule, message=message, path=path, severity=severity, hint=hint)
        if candidate not in self.findings:
            self.findings.append(candidate)

    def extend(self, other: FindingSet) -> None:
        for finding in other.findings:
            if finding not in self.findings:
                self.findings.append(finding)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [f for f in self.findings if f.severity == "warning"]

    @property
    def ok(self) -> bool:
        return not self.errors

    def __len__(self) -> int:
        return len(self.findings)

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self.findings)

    def as_dicts(self) -> list[dict[str, str]]:
        return [f.as_dict() for f in self.findings]


class DbModernizeError(Exception):
    """Base class for errors that map onto a specific exit code."""

    exit_code: ExitCode = ExitCode.INTERNAL_ERROR


class UsageError(DbModernizeError):
    exit_code = ExitCode.USAGE_ERROR


class InputNotFoundError(DbModernizeError):
    exit_code = ExitCode.INPUT_NOT_FOUND


class OutputExistsError(DbModernizeError):
    exit_code = ExitCode.OUTPUT_EXISTS


class PolicyViolationError(DbModernizeError):
    exit_code = ExitCode.POLICY_VIOLATION


class SafetyRefusalError(DbModernizeError):
    """Raised when a request crosses a documented safety boundary.

    The message is shown to the user verbatim, so it must explain *why* the action was
    refused and what the safe alternative is.
    """

    exit_code = ExitCode.SAFETY_REFUSAL


class ValidationFailedError(DbModernizeError):
    exit_code = ExitCode.VALIDATION_FAILED

    def __init__(self, message: str, findings: FindingSet | None = None) -> None:
        super().__init__(message)
        self.findings = findings or FindingSet()
