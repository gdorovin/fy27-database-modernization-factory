#!/usr/bin/env python
"""Remove build and cache artifacts. Cross-platform, so the Makefile works on Windows."""

from __future__ import annotations

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

DIRECTORIES = (
    "build",
    "dist",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "htmlcov",
    "out",
)

GLOB_DIRECTORIES = ("**/__pycache__", "*.egg-info", "src/*.egg-info")

FILES = (".coverage", "coverage.xml")


def main() -> int:
    removed = 0

    for name in DIRECTORIES:
        path = REPO_ROOT / name
        if path.is_dir():
            shutil.rmtree(path)
            removed += 1
            print(f"removed {name}/")

    for pattern in GLOB_DIRECTORIES:
        for path in REPO_ROOT.glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                removed += 1
                print(f"removed {path.relative_to(REPO_ROOT).as_posix()}/")

    for name in FILES:
        path = REPO_ROOT / name
        if path.is_file():
            path.unlink()
            removed += 1
            print(f"removed {name}")

    print(f"Clean complete. {removed} item(s) removed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
