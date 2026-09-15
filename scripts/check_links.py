#!/usr/bin/env python
"""Check that relative Markdown links resolve.

External URLs are not fetched. A build that depends on someone else's uptime fails for
reasons unrelated to the change being reviewed, and people learn to ignore it.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")

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

#: Generated documents reference wave-numbered siblings that only exist in an engagement
#: output directory, not in the repository.
SKIP_DIRS = ("scenarios",)


def markdown_files() -> list[Path]:
    return sorted(
        path
        for path in REPO_ROOT.rglob("*.md")
        if not any(part in SKIP_PARTS for part in path.parts)
        and not any(part in SKIP_DIRS for part in path.relative_to(REPO_ROOT).parts[:1])
    )


def main() -> int:
    problems: list[str] = []

    for path in markdown_files():
        relative = path.relative_to(REPO_ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")

        for target in LINK.findall(text):
            parsed = urlparse(target)
            if parsed.scheme or target.startswith("#") or target.startswith("mailto:"):
                continue

            fragment_free = unquote(target.split("#", 1)[0])
            if not fragment_free:
                continue

            resolved = (path.parent / fragment_free).resolve()
            if not resolved.exists():
                problems.append(f"{relative}: link target does not exist: {target}")

    if problems:
        print("Link check failed:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        print(
            "\nIf a target does not exist yet, describe it in prose rather than linking to "
            "a hopeful path.",
            file=sys.stderr,
        )
        return 1

    print(f"Link check passed across {len(markdown_files())} Markdown files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
