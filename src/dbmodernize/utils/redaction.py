"""Redaction of secret-like values before they reach a log, a report, or a fixture.

This is defence in depth, not a guarantee. The primary control is never importing real
credentials in the first place.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

MASK = "***REDACTED***"

#: Ordered so that the most specific pattern wins.
_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "connection-string-secret",
        re.compile(
            r"(?i)\b((?:password|pwd|accountkey|sharedaccesskey|secret|api[_-]?key|token)"
            r"\s*=\s*)([^;\s\"']+)",
        ),
    ),
    (
        "json-secret-field",
        re.compile(
            r"(?i)(\"(?:password|pwd|secret|client_secret|api_key|access_token|"
            r"connection_string|sas_token)\"\s*:\s*\")([^\"]*)(\")",
        ),
    ),
    ("bearer", re.compile(r"(?i)\b(bearer\s+)([A-Za-z0-9._\-]{16,})")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\b")),
    ("azure-sas", re.compile(r"(?i)\b(sig=)([A-Za-z0-9%+/=]{16,})")),
    (
        "private-key-block",
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S),
    ),
)

#: Keys whose values are masked wholesale regardless of content.
_SENSITIVE_KEYS = frozenset(
    {
        "password",
        "pwd",
        "secret",
        "client_secret",
        "api_key",
        "apikey",
        "access_token",
        "refresh_token",
        "connection_string",
        "connectionstring",
        "sas_token",
        "account_key",
        "private_key",
        "credential",
    }
)

#: Detection is stricter than redaction. A connection-string assignment has no spaces
#: around the equals sign and a value that is not a bare lowercase identifier, which is
#: what separates ``Password=Str0ng!Pass;`` from ``password = value``.
_CONNECTION_STRING_LITERAL = re.compile(
    r"(?i)\b(?:password|pwd|accountkey|sharedaccesskey|client_secret|api[_-]?key)"
    r"=(?=[^;\s\"']*[A-Z0-9!@#$%^&*_+\-])[^;\s\"']{8,}"
)

_DETECTION_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("connection-string-secret", _CONNECTION_STRING_LITERAL),
    *(
        (name, pattern)
        for name, pattern in _PATTERNS
        if name in {"json-secret-field", "bearer", "jwt", "azure-sas", "private-key-block"}
    ),
)


def redact(text: str) -> str:
    """Mask secret-like substrings in free text."""
    if not text:
        return text
    result = text
    for name, pattern in _PATTERNS:
        if name in {"jwt", "private-key-block"}:
            result = pattern.sub(MASK, result)
        elif name == "json-secret-field":
            result = pattern.sub(rf"\1{MASK}\3", result)
        else:
            result = pattern.sub(rf"\1{MASK}", result)
    return result


def redact_mapping(data: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively mask sensitive keys and secret-like values in a mapping."""
    out: dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in _SENSITIVE_KEYS:
            out[key] = MASK
        elif isinstance(value, Mapping):
            out[key] = redact_mapping(value)
        elif isinstance(value, list):
            out[key] = [
                redact_mapping(item)
                if isinstance(item, Mapping)
                else (redact(item) if isinstance(item, str) else item)
                for item in value
            ]
        elif isinstance(value, str):
            out[key] = redact(value)
        else:
            out[key] = value
    return out


def contains_secret_like(text: str) -> list[str]:
    """Return the names of detection patterns that matched.

    Used by the pre-commit guard and the repository scan, so it is deliberately stricter
    than :func:`redact`. Redaction can afford a false positive; a build gate cannot, and
    ``token = token.replace(...)`` is ordinary Python, not a leaked credential.
    """
    return [name for name, pattern in _DETECTION_PATTERNS if pattern.search(text)]
