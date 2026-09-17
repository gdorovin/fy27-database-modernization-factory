#!/usr/bin/env python
"""Pre-commit guard: no secrets, credentials, or real identifiers in tracked content.

Runs on the staged files pre-commit passes in, or across the repository when called with
no arguments. Deliberately stricter than the redaction helper is permissive: redaction can
afford a false positive, a commit hook cannot.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dbmodernize.utils.redaction import contains_secret_like  # noqa: E402
from dbmodernize.validators.repository import PATTERN_BEARING_FILES  # noqa: E402

TEXT_SUFFIXES = frozenset(
    {
        ".md",
        ".py",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".cfg",
        ".txt",
        ".bicep",
        ".bicepparam",  # the file most likely to hold a real subscription or resource id
        ".sh",
        ".ps1",
        ".csv",
        ".env",
        ".ini",
        ".xml",
        ".sql",
        ".j2",
    }
)

SKIP_PARTS = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        ".mypy_cache",
        ".ruff_cache",
        ".pytest_cache",
        "node_modules",
    }
)

#: Files that define or test the detection rules and must be able to name the patterns.
#: Shared with the repository validator so the two cannot drift apart.
ALLOWED_TO_MENTION = PATTERN_BEARING_FILES

#: Identifiers that look real. Placeholders must be obviously fake.
REAL_LOOKING = (
    (
        "guid",
        re.compile(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
            re.IGNORECASE,
        ),
    ),
    (
        "azure-endpoint",
        re.compile(
            r"(?i)\b[\w-]+\.("
            r"(database|blob|vault)\.(windows|azure)\.net"
            r"|(blob|file|queue|table|dfs)\.core\.windows\.net"
            r"|(postgres|mysql|mariadb)\.database\.azure\.com"
            r")\b"
        ),
    ),
    ("email", re.compile(r"(?i)\b[\w.+-]+@(?!example\.|contoso\.example)[\w-]+\.[a-z]{2,}\b")),
)

ALL_ZERO_GUID = "00000000-0000-0000-0000-000000000000"

#: Private DNS zone names are service-wide labels, not customer endpoints. A resource id
#: that ends in one names the zone type, never a real server.
PRIVATE_LINK_ZONE_PREFIX = "privatelink."


def candidate_files(argv: list[str]) -> list[Path]:
    if argv:
        return [Path(arg) for arg in argv if Path(arg).suffix.lower() in TEXT_SUFFIXES]
    return sorted(
        path
        for path in REPO_ROOT.rglob("*")
        if path.is_file()
        and path.suffix.lower() in TEXT_SUFFIXES
        and not any(part in SKIP_PARTS for part in path.parts)
    )


def main(argv: list[str]) -> int:
    problems: list[str] = []

    for path in candidate_files(argv):
        if not path.is_file():
            continue
        relative = path.resolve().relative_to(REPO_ROOT).as_posix()
        if relative in ALLOWED_TO_MENTION:
            continue

        text = path.read_text(encoding="utf-8", errors="replace")

        for name in contains_secret_like(text):
            problems.append(f"{relative}: matches secret pattern '{name}'")

        for name, pattern in REAL_LOOKING:
            for match in pattern.finditer(text):
                value = match.group(0)
                if name == "guid" and value.lower() == ALL_ZERO_GUID:
                    continue
                if name == "azure-endpoint" and value.lower().startswith(PRIVATE_LINK_ZONE_PREFIX):
                    continue
                problems.append(
                    f"{relative}: contains a real-looking {name} ({value!r}). "
                    "Use an obviously fake placeholder."
                )

    if problems:
        print("Secret and identifier scan failed:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(
            "\nNothing in this repository may contain a credential, endpoint, or customer "
            "identifier. See SECURITY.md.",
            file=sys.stderr,
        )
        return 1

    print("Secret and identifier scan passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
