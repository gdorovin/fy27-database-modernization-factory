"""Repository-level structure and safety validation.

These checks encode the promises made in the README and `SECURITY.md`. They run in CI, in
pre-commit, and from `dbmodernize validate-repo`, so a promise cannot quietly stop being
true.
"""

from __future__ import annotations

import re
from pathlib import Path

from dbmodernize.errors import FindingSet
from dbmodernize.utils.redaction import contains_secret_like
from dbmodernize.utils.text import assertions_in_markdown

REQUIRED_PATHS: tuple[str, ...] = (
    "README.md",
    "AGENTS.md",
    "CLAUDE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "GOVERNANCE.md",
    "CODE_OF_CONDUCT.md",
    "CHANGELOG.md",
    "LICENSE",
    "Makefile",
    "pyproject.toml",
    ".github/copilot-instructions.md",
    ".github/CODEOWNERS",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE",
    ".github/instructions",
    ".github/agents",
    ".github/skills",
    ".github/workflows",
    "contracts",
    "playbooks/default",
    "templates",
    "src/dbmodernize",
    "scripts",
    "scenarios",
    "tests",
    "docs",
    "infra",
)

#: Directories whose contents are generated or vendored and are not scanned for prose rules.
_SKIP_DIRS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
        "node_modules",
        "htmlcov",
        "build",
        "dist",
    }
)

_TEXT_SUFFIXES = frozenset(
    {".md", ".py", ".json", ".yaml", ".yml", ".toml", ".cfg", ".txt", ".bicep", ".sh", ".ps1"}
)

_ZERO_DOWNTIME = re.compile(r"(?i)\b(zero[\s-]downtime|no downtime)\b")

#: Claims that age. A file making one must also state when it was last verified.
_DATED_CLAIM_TERMS = (
    "currently supported",
    "generally available",
    "in preview",
    "public preview",
    "private preview",
    "pricing",
    "list price",
    "funding",
    "eligibility",
    "service limit",
    "quota is",
)
_VERIFIED_ON = re.compile(r"(?i)verified[_ ]on")

#: Obviously-fake values that are safe to use as placeholders.
_ALLOWED_PLACEHOLDERS = (
    "00000000-0000-0000-0000-000000000000",
    "contoso.example",
    "REPLACE-ME",
    "REDACTED",
)

#: Files that implement or test the detection rules, and so must be able to contain the
#: very patterns they detect. Keeping this list short and explicit is the point: a broad
#: exclusion would quietly disable the check. Imported by scripts/check_no_secrets.py so
#: the two cannot drift apart.
PATTERN_BEARING_FILES = frozenset(
    {
        "src/dbmodernize/utils/redaction.py",
        "src/dbmodernize/evidence/injection.py",
        "scripts/check_no_secrets.py",
        "tests/security/test_untrusted_input.py",
        "tests/repository/test_repository.py",
    }
)


def _iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in _TEXT_SUFFIXES:
            files.append(path)
    return sorted(files)


def validate_repository(root: Path) -> FindingSet:
    findings = FindingSet()
    findings.extend(check_structure(root))
    findings.extend(check_no_empty_directories(root))
    findings.extend(check_no_secrets(root))
    findings.extend(check_no_restricted_fixtures(root))
    findings.extend(check_downtime_language(root))
    findings.extend(check_dated_claims(root))
    findings.extend(check_readme_commands(root))
    return findings


def check_structure(root: Path) -> FindingSet:
    findings = FindingSet()
    for relative in REQUIRED_PATHS:
        if not (root / relative).exists():
            findings.add(
                rule="REPO-MISSING-PATH",
                message=f"Required path is missing: {relative}",
                path=relative,
            )
    return findings


def check_no_empty_directories(root: Path) -> FindingSet:
    """Every committed directory must contain something meaningful.

    A directory holding only an unexplained `.gitkeep` tells a reader nothing and makes
    the tree look more complete than it is.
    """
    findings = FindingSet()
    for directory in sorted(root.rglob("*")):
        if not directory.is_dir():
            continue
        if any(part in _SKIP_DIRS for part in directory.parts):
            continue
        entries = [p for p in directory.iterdir() if p.name != ".DS_Store"]
        if not entries:
            findings.add(
                rule="REPO-EMPTY-DIR",
                message="Directory is empty; remove it or add content that explains its use",
                path=str(directory.relative_to(root).as_posix()),
            )
            continue
        if len(entries) == 1 and entries[0].name in {".gitkeep", ".keep"}:
            text = entries[0].read_text(encoding="utf-8", errors="replace").strip()
            if len(text) < 20:
                findings.add(
                    rule="REPO-BARE-KEEPFILE",
                    message=(
                        "Directory contains only a keep file with no explanation. "
                        "State what will live here and why the directory exists now."
                    ),
                    path=str(directory.relative_to(root).as_posix()),
                )
    return findings


def check_no_secrets(root: Path) -> FindingSet:
    findings = FindingSet()
    for path in _iter_text_files(root):
        relative = path.relative_to(root).as_posix()
        if relative in PATTERN_BEARING_FILES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(placeholder in text for placeholder in _ALLOWED_PLACEHOLDERS) and len(text) < 200:
            continue
        matched = contains_secret_like(text)
        if matched:
            findings.add(
                rule="REPO-SECRET-LIKE",
                message=(
                    f"Content matches secret patterns ({', '.join(matched)}). "
                    "Replace with an obviously fake placeholder."
                ),
                path=relative,
            )
    return findings


def check_no_restricted_fixtures(root: Path) -> FindingSet:
    """Nothing classified above `internal` may be committed."""
    findings = FindingSet()
    pattern = re.compile(
        r'"classification"\s*:\s*"(confidential|restricted)"|'
        r"classification:\s*(confidential|restricted)"
    )
    for path in _iter_text_files(root):
        if path.suffix.lower() not in {".json", ".yaml", ".yml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if pattern.search(text):
            findings.add(
                rule="REPO-CLASSIFICATION",
                message=(
                    "File declares a classification above 'internal'. Evidence at that "
                    "level belongs in approved customer-side storage, referenced by "
                    "manifest only."
                ),
                path=str(path.relative_to(root).as_posix()),
            )
    return findings


def check_downtime_language(root: Path) -> FindingSet:
    """A zero-downtime claim is allowed only where it is being forbidden.

    Only Markdown is scanned. Prose is what a customer reads; source code that implements
    the rule and configuration that tests it must be able to name the phrase.
    """
    findings = FindingSet()
    for path in _iter_text_files(root):
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for line_number, section, line in assertions_in_markdown(text, _ZERO_DOWNTIME):
            findings.add(
                rule="REPO-ZERO-DOWNTIME",
                message=(
                    f"Line {line_number} under '{section}' claims zero downtime without "
                    f"qualification: {line!r}. Use 'near-zero planned downtime' with a "
                    "method-specific basis."
                ),
                path=str(path.relative_to(root).as_posix()),
            )
    return findings


def check_dated_claims(root: Path) -> FindingSet:
    """Guidance that states a perishable fact must record when it was verified."""
    findings = FindingSet()
    scanned = [
        p for p in _iter_text_files(root) if p.suffix == ".md" and "docs/guidance" in p.as_posix()
    ]
    for path in scanned:
        text = path.read_text(encoding="utf-8", errors="replace")
        lowered = text.lower()
        hits = sorted({term for term in _DATED_CLAIM_TERMS if term in lowered})
        if hits and not _VERIFIED_ON.search(text):
            findings.add(
                rule="REPO-UNDATED-CLAIM",
                message=(
                    f"Contains perishable claims ({', '.join(hits)}) but no 'verified_on' "
                    "date. Product status, limits, and commercial terms change; readers "
                    "need to know how stale this is."
                ),
                path=str(path.relative_to(root).as_posix()),
            )
    return findings


def check_readme_commands(root: Path) -> FindingSet:
    """Every `dbmodernize <command>` shown in the README must actually exist.

    Only code spans and fenced blocks are inspected. Prose such as "the dbmodernize CLI"
    is not a command reference and must not be treated as one.
    """
    findings = FindingSet()
    readme = root / "README.md"
    if not readme.is_file():
        return findings

    from dbmodernize.cli import command_names

    known = command_names()
    text = readme.read_text(encoding="utf-8")
    snippets = _code_spans(text)
    referenced: set[str] = set()
    for snippet in snippets:
        referenced.update(re.findall(r"\bdbmodernize\s+([a-z][a-z\-]+)", snippet))

    for command in sorted(referenced - known - {"help"}):
        findings.add(
            rule="REPO-README-UNKNOWN-COMMAND",
            message=(
                f"README shows 'dbmodernize {command}' in a code span, but that is not a "
                "registered command."
            ),
            path="README.md",
        )
    return findings


def _code_spans(markdown: str) -> list[str]:
    """Return fenced code blocks and inline code spans."""
    fenced = re.findall(r"```[a-zA-Z]*\n(.*?)```", markdown, re.DOTALL)
    inline = re.findall(r"`([^`\n]+)`", markdown)
    return fenced + inline


__all__ = [
    "PATTERN_BEARING_FILES",
    "REQUIRED_PATHS",
    "check_dated_claims",
    "check_downtime_language",
    "check_no_empty_directories",
    "check_no_restricted_fixtures",
    "check_no_secrets",
    "check_readme_commands",
    "check_structure",
    "validate_repository",
]
