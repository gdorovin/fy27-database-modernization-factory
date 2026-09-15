#!/usr/bin/env python
"""Print the changelog section for one version, for use as release notes."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = REPO_ROOT / "CHANGELOG.md"


def main(argv: list[str]) -> int:
    if not argv:
        print("usage: extract_changelog.py <version>", file=sys.stderr)
        return 2

    version = argv[0].lstrip("v")
    text = CHANGELOG.read_text(encoding="utf-8")

    pattern = re.compile(
        rf"^## \[{re.escape(version)}\].*?$(?P<body>.*?)(?=^## \[|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    if not match:
        print(f"No '## [{version}]' section in CHANGELOG.md", file=sys.stderr)
        return 1

    body = match.group("body").strip()
    # Strip the link-reference block that Keep a Changelog puts at the end of the file.
    body = re.sub(r"^\[[^\]]+\]:\s+http.*$", "", body, flags=re.MULTILINE).strip()
    print(body)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
