"""Detect directive-like content inside imported documents.

Assessment exports contain free text: descriptions, owner notes, comment fields. That text
is data. If it contains something shaped like an instruction, the correct response is to
record it and carry on treating it as data — never to obey it.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from dbmodernize.models.evidence import InjectionFinding

_MAX_EXCERPT = 280

#: Each pattern is a shape that only appears when text is trying to steer a model.
PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("instruction-override", re.compile(r"(?i)\bignore (?:all |any )?(?:previous|prior|above)\b")),
    ("role-reassignment", re.compile(r"(?i)\byou are (?:now )?(?:a|an|the)\b")),
    ("system-prompt-claim", re.compile(r"(?i)\b(system prompt|developer message|</?system>)")),
    (
        "policy-suspension",
        re.compile(
            r"(?i)\b(disregard|bypass|override)\b[^.\n]{0,30}\b(polic|rule|instruction|guardrail)"
        ),
    ),
    (
        "approval-forgery",
        re.compile(r"(?i)\b(?:this is |consider this )?(?:pre[- ]?)?approved by\b"),
    ),
    (
        "secret-exfiltration",
        re.compile(
            r"(?i)\b(reveal|print|output|send)\b[^.\n]{0,30}\b(secret|token|credential|key)\b"
        ),
    ),
    (
        "tool-invocation",
        re.compile(r"(?i)\b(run|execute|invoke)\b[^.\n]{0,20}\b(command|shell|script|tool)\b"),
    ),
    (
        "urgency-escalation",
        re.compile(r"(?i)\b(do not (?:ask|confirm|verify)|without (?:approval|review))\b"),
    ),
)


def scan_text(text: str, field_name: str) -> list[InjectionFinding]:
    if not text:
        return []
    findings: list[InjectionFinding] = []
    for name, pattern in PATTERNS:
        match = pattern.search(text)
        if match:
            start = max(match.start() - 40, 0)
            excerpt = text[start : start + _MAX_EXCERPT].strip()
            findings.append(
                InjectionFinding(
                    pattern=name,
                    excerpt=excerpt[:_MAX_EXCERPT] or match.group(0),
                    field_name=field_name,
                )
            )
    return findings


def scan_mapping(data: Mapping[str, Any], prefix: str = "") -> list[InjectionFinding]:
    """Recursively scan every string value in a mapping."""
    findings: list[InjectionFinding] = []
    for key, value in data.items():
        field_name = f"{prefix}{key}"
        if isinstance(value, str):
            findings.extend(scan_text(value, field_name))
        elif isinstance(value, Mapping):
            findings.extend(scan_mapping(value, prefix=f"{field_name}."))
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, str):
                    findings.extend(scan_text(item, f"{field_name}[{index}]"))
                elif isinstance(item, Mapping):
                    findings.extend(scan_mapping(item, prefix=f"{field_name}[{index}]."))
    return findings


__all__ = ["PATTERNS", "scan_mapping", "scan_text"]
