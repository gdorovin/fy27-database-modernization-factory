"""YAML frontmatter parsing shared by the skill and agent validators."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from dbmodernize.errors import FindingSet
from dbmodernize.utils.io import read_text

_FRONTMATTER = re.compile(r"^---\s*\n(?P<yaml>.*?)\n---\s*\n(?P<body>.*)\Z", re.DOTALL)
_H2 = re.compile(r"^##\s+(?P<title>.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class Document:
    path: Path
    frontmatter: dict[str, Any]
    body: str

    def sections(self) -> dict[str, str]:
        """Level-2 headings mapped to their content, in document order."""
        titles = [(m.group("title").strip(), m.start(), m.end()) for m in _H2.finditer(self.body)]
        result: dict[str, str] = {}
        for index, (title, _, end) in enumerate(titles):
            stop = titles[index + 1][1] if index + 1 < len(titles) else len(self.body)
            result[title] = self.body[end:stop].strip()
        return result

    def has_content(self, section: str, minimum_chars: int = 30) -> bool:
        body = self.sections().get(section, "")
        return len(body.strip()) >= minimum_chars


def parse_document(path: Path) -> tuple[Document | None, FindingSet]:
    findings = FindingSet()
    text = read_text(path)
    match = _FRONTMATTER.match(text)
    if not match:
        findings.add(
            rule="FRONTMATTER-MISSING",
            message=(
                "File does not begin with a YAML frontmatter block delimited by '---'. "
                "Without it, the file cannot be discovered or selected."
            ),
            path=str(path),
        )
        return None, findings

    try:
        data = yaml.safe_load(match.group("yaml")) or {}
    except yaml.YAMLError as exc:
        findings.add(
            rule="FRONTMATTER-INVALID-YAML",
            message=f"Frontmatter is not valid YAML: {exc}",
            path=str(path),
        )
        return None, findings

    if not isinstance(data, dict):
        findings.add(
            rule="FRONTMATTER-NOT-MAPPING",
            message=f"Frontmatter parsed as {type(data).__name__}, expected a mapping",
            path=str(path),
        )
        return None, findings

    return Document(path=path, frontmatter=data, body=match.group("body")), findings


def require_sections(
    document: Document,
    required: tuple[str, ...],
    rule_prefix: str,
    minimum_chars: int = 30,
) -> FindingSet:
    findings = FindingSet()
    present = document.sections()
    for section in required:
        if section not in present:
            findings.add(
                rule=f"{rule_prefix}-MISSING-SECTION",
                message=f"Missing required section '## {section}'",
                path=str(document.path),
            )
        elif len(present[section].strip()) < minimum_chars:
            findings.add(
                rule=f"{rule_prefix}-EMPTY-SECTION",
                message=(
                    f"Section '## {section}' has {len(present[section].strip())} characters. "
                    f"A section shorter than {minimum_chars} characters is a placeholder, "
                    "not guidance."
                ),
                path=str(document.path),
            )
    return findings


__all__ = ["Document", "parse_document", "require_sections"]
