"""Structural validation of Agent Skills.

A skill is a reusable operating procedure. The checks here exist because the two ways
skills fail in practice are: a body that is a wall of prose with no decision points, and
a description so vague that the model cannot tell two skills apart.
"""

from __future__ import annotations

import re
from pathlib import Path

from dbmodernize.errors import FindingSet
from dbmodernize.utils.text import assertions_in_markdown
from dbmodernize.validators.frontmatter import Document, parse_document, require_sections

REQUIRED_SECTIONS: tuple[str, ...] = (
    "Invoke when",
    "Do not invoke when",
    "Required inputs",
    "Preconditions",
    "Procedure",
    "Decision points",
    "Output contract",
    "Validation",
    "Failure and fallback",
    "Avoid",
    "Example",
)

_NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
_MAX_DESCRIPTION = 500
_MIN_DESCRIPTION = 60

#: Words that make a description useless for selection because every skill could claim them.
_VAGUE_TERMS = frozenset(
    {"helps", "various", "general", "stuff", "things", "etc", "and more", "any task"}
)

#: Text that would make a skill unsafe if a model followed it literally. Checked per line
#: and skipped where the line is framed as a prohibition, so a skill can name what it bans.
_UNSAFE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("zero-downtime-claim", re.compile(r"(?i)\bzero[\s-]downtime\b")),
    ("auto-approve", re.compile(r"(?i)\bauto(?:matically)?[\s-]approve")),
    (
        "direct-production-change",
        re.compile(r"(?i)\b(?:apply|deploy|run)\b[^.\n]{0,40}\bto production\b"),
    ),
)

#: Checked without negation awareness: there is no legitimate reason to write one down.
_ABSOLUTE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("credential-literal", re.compile(r"(?i)\b(password|client_secret|api_key)\s*=\s*\S+")),
)


def validate_skill(skill_dir: Path) -> FindingSet:
    """Validate one skill directory."""
    findings = FindingSet()
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.is_file():
        findings.add(
            rule="SKILL-MISSING-FILE",
            message="Directory contains no SKILL.md",
            path=str(skill_dir),
        )
        return findings

    document, parse_findings = parse_document(skill_file)
    findings.extend(parse_findings)
    if document is None:
        return findings

    name = str(document.frontmatter.get("name", "")).strip()
    description = str(document.frontmatter.get("description", "")).strip()

    if not name:
        findings.add(
            rule="SKILL-NO-NAME", message="Frontmatter has no 'name'", path=str(skill_file)
        )
    else:
        if not _NAME_PATTERN.match(name):
            findings.add(
                rule="SKILL-NAME-FORMAT",
                message=f"Name {name!r} must be lowercase and hyphen-separated",
                path=str(skill_file),
            )
        if name != skill_dir.name:
            findings.add(
                rule="SKILL-NAME-MISMATCH",
                message=(f"Frontmatter name {name!r} does not match directory {skill_dir.name!r}"),
                path=str(skill_file),
            )

    findings.extend(_check_description(description, skill_file))
    findings.extend(require_sections(document, REQUIRED_SECTIONS, "SKILL"))
    findings.extend(_check_invoke_contract(document.sections(), skill_file))
    findings.extend(_check_unsafe_language(document, skill_file))

    if document.frontmatter.get("enabled") is False:
        findings.add(
            rule="SKILL-DISABLED",
            message="Skill is disabled via frontmatter and will not be selected",
            path=str(skill_file),
            severity="warning",
        )
    return findings


def _check_description(description: str, path: Path) -> FindingSet:
    findings = FindingSet()
    if not description:
        findings.add(
            rule="SKILL-NO-DESCRIPTION",
            message="Frontmatter has no 'description'; the skill cannot be selected",
            path=str(path),
        )
        return findings
    if len(description) > _MAX_DESCRIPTION:
        findings.add(
            rule="SKILL-DESCRIPTION-LONG",
            message=(
                f"Description is {len(description)} characters. Keep it under "
                f"{_MAX_DESCRIPTION}; selection reads the description, not the body."
            ),
            path=str(path),
        )
    if len(description) < _MIN_DESCRIPTION:
        findings.add(
            rule="SKILL-DESCRIPTION-SHORT",
            message=(
                f"Description is {len(description)} characters and is unlikely to "
                "distinguish this skill from its neighbours."
            ),
            path=str(path),
        )
    lowered = description.lower()
    vague = sorted(term for term in _VAGUE_TERMS if term in lowered)
    if vague:
        findings.add(
            rule="SKILL-DESCRIPTION-VAGUE",
            message=f"Description contains non-distinguishing terms: {', '.join(vague)}",
            path=str(path),
            severity="warning",
        )
    return findings


def _check_invoke_contract(sections: dict[str, str], path: Path) -> FindingSet:
    """'Do not invoke when' must actually redirect, otherwise it is decoration."""
    findings = FindingSet()
    body = sections.get("Do not invoke when", "")
    if body and not re.search(r"(?i)\buse\b.*\binstead\b|\bdefer to\b|\bhand(?: |-)off to\b", body):
        findings.add(
            rule="SKILL-NO-REDIRECT",
            message=(
                "'Do not invoke when' does not name an alternative. Telling a model what "
                "not to do without saying what to do instead leaves it improvising."
            ),
            path=str(path),
            severity="warning",
        )
    return findings


def _check_unsafe_language(document: Document, path: Path) -> FindingSet:
    """Flag unsafe guidance the skill asserts, not unsafe guidance it forbids."""
    findings = FindingSet()

    for name, pattern in _UNSAFE_PATTERNS:
        for line_number, section, line in assertions_in_markdown(document.body, pattern):
            findings.add(
                rule=f"SKILL-UNSAFE-{name.upper()}",
                message=(
                    f"Line {line_number} under '{section}' asserts unsafe guidance "
                    f"({name}): {line!r}. See the safety boundaries in "
                    ".github/copilot-instructions.md."
                ),
                path=str(path),
            )

    for name, pattern in _ABSOLUTE_PATTERNS:
        match = pattern.search(document.body)
        if match:
            findings.add(
                rule=f"SKILL-UNSAFE-{name.upper()}",
                message=f"Skill body contains {name}: {match.group(0)!r}",
                path=str(path),
            )
    return findings


def validate_skills_tree(skills_root: Path) -> FindingSet:
    """Validate every skill and check that descriptions stay distinguishable."""
    findings = FindingSet()
    if not skills_root.is_dir():
        findings.add(
            rule="SKILL-ROOT-MISSING",
            message=f"Skills directory not found: {skills_root}",
            path=str(skills_root),
        )
        return findings

    directories = sorted(d for d in skills_root.iterdir() if d.is_dir())
    if not directories:
        findings.add(
            rule="SKILL-ROOT-EMPTY",
            message=f"No skills found under {skills_root}",
            path=str(skills_root),
        )

    descriptions: dict[str, set[str]] = {}
    for directory in directories:
        findings.extend(validate_skill(directory))
        document, _ = parse_document(directory / "SKILL.md")
        if document:
            text = str(document.frontmatter.get("description", "")).lower()
            descriptions[directory.name] = set(re.findall(r"[a-z]{4,}", text))

    findings.extend(_check_overlap(descriptions, skills_root))
    return findings


def _check_overlap(descriptions: dict[str, set[str]], root: Path) -> FindingSet:
    """Two skills that could plausibly answer the same request is a design bug."""
    findings = FindingSet()
    names = sorted(descriptions)
    for i, left in enumerate(names):
        for right in names[i + 1 :]:
            a, b = descriptions[left], descriptions[right]
            if not a or not b:
                continue
            jaccard = len(a & b) / len(a | b)
            if jaccard >= 0.6:
                findings.add(
                    rule="SKILL-DESCRIPTION-OVERLAP",
                    message=(
                        f"Descriptions for {left!r} and {right!r} overlap at "
                        f"{jaccard:.0%}. Selection between them will be unreliable."
                    ),
                    path=str(root),
                    severity="warning",
                )
    return findings


__all__ = ["REQUIRED_SECTIONS", "validate_skill", "validate_skills_tree"]
