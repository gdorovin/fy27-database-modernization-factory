"""Text helpers shared by validators.

A rule that forbids a phrase has to be able to name the phrase it forbids. Without
negation awareness, the sentence "never claim zero downtime" trips the very check that
sentence exists to describe.
"""

from __future__ import annotations

import re

NEGATION = re.compile(
    r"(?i)\b(never|not|no|must not|cannot|can't|avoid|forbid\w*|prohibit\w*|refus\w*|"
    r"reject\w*|instead of|rather than|absent|intentionally|without)\b"
)

#: Section titles whose contents are, by their nature, a list of things not to do.
PROHIBITION_HEADING = re.compile(
    r"(?i)^(avoid|constraints|safety|forbidden|prohibited|out of scope|"
    r"do not\b|don't\b|never\b|what this .*not|.*does not\b|.*is not\b)"
)

_HEADING = re.compile(r"^(#{1,6})\s+(?P<title>.+?)\s*$")


def is_negated(line: str) -> bool:
    """True when the line reads as a prohibition rather than an assertion."""
    return bool(NEGATION.search(line))


def offending_lines(text: str, pattern: re.Pattern[str]) -> list[tuple[int, str]]:
    """Lines matching ``pattern`` that are not framed as a prohibition."""
    hits: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if pattern.search(line) and not is_negated(line):
            hits.append((number, line.strip()))
    return hits


def assertions_in_markdown(markdown: str, pattern: re.Pattern[str]) -> list[tuple[int, str, str]]:
    """Lines that *assert* ``pattern``, with their line number and section title.

    Skips any section whose heading reads as a prohibition, and any individual line framed
    as one. What remains is prose that would read to a customer as a claim.
    """
    hits: list[tuple[int, str, str]] = []
    section = ""
    suppressed = False

    for number, line in enumerate(markdown.splitlines(), start=1):
        heading = _HEADING.match(line)
        if heading:
            section = heading.group("title")
            suppressed = bool(PROHIBITION_HEADING.match(section))
            continue
        if suppressed or not pattern.search(line) or is_negated(line):
            continue
        hits.append((number, section or "<preamble>", line.strip()))
    return hits


__all__ = [
    "NEGATION",
    "PROHIBITION_HEADING",
    "assertions_in_markdown",
    "is_negated",
    "offending_lines",
]
