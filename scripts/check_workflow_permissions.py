#!/usr/bin/env python
"""Every workflow declares least-privilege permissions and pins its actions.

An unpinned action is someone else's supply chain running with your token. A workflow with
no `permissions:` block inherits whatever the repository default is, which is exactly the
kind of implicit privilege that is fine until the day it is not.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"

#: A 40-character commit SHA. Tags move; SHAs do not.
PINNED = re.compile(r"^[\w.-]+/[\w.-]+(/[\w.-]+)*@[0-9a-f]{40}$")

#: Actions published by GitHub itself under a major tag are still required to be pinned;
#: this set exists only for local composite actions, which cannot be pinned by SHA.
LOCAL_ACTION = re.compile(r"^\./")

#: Write scopes any job may hold: they cannot alter repository content.
WRITE_ALLOWED_ANYWHERE = frozenset({"security-events", "pull-requests", "id-token", "attestations"})

#: Write scopes that alter repository content, allowed only where the file named here has a
#: documented reason. ``contents: write`` used to sit in the general allowlist, which meant
#: the single most dangerous scope was the one this script never questioned.
WRITE_ALLOWED_BY_FILE = frozenset(
    {
        # Publishing a GitHub release requires writing the release object.
        (".github/workflows/release.yml", "contents"),
    }
)


def uses_values(node: Any) -> list[str]:
    found: list[str] = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "uses" and isinstance(value, str):
                found.append(value)
            else:
                found.extend(uses_values(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(uses_values(item))
    return found


def main() -> int:
    problems: list[str] = []

    for path in sorted(WORKFLOWS.glob("*.yml")) + sorted(WORKFLOWS.glob("*.yaml")):
        relative = path.relative_to(REPO_ROOT).as_posix()
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            problems.append(f"{relative}: does not parse as a mapping")
            continue

        if "permissions" not in document:
            problems.append(
                f"{relative}: no top-level 'permissions:' block, so the workflow inherits "
                "the repository default"
            )

        for job_name, job in (document.get("jobs") or {}).items():
            if not isinstance(job, dict):
                continue
            permissions = job.get("permissions")
            if isinstance(permissions, dict):
                for scope, level in permissions.items():
                    if level != "write":
                        continue
                    if scope in WRITE_ALLOWED_ANYWHERE:
                        continue
                    if (relative, scope) in WRITE_ALLOWED_BY_FILE:
                        continue
                    problems.append(
                        f"{relative}: job '{job_name}' requests write on '{scope}'. "
                        "Justify it in a comment and add it to WRITE_ALLOWED_BY_FILE, "
                        "or narrow it."
                    )

        for action in uses_values(document):
            if LOCAL_ACTION.match(action):
                continue
            if not PINNED.match(action):
                problems.append(
                    f"{relative}: action '{action}' is not pinned to a 40-character commit "
                    "SHA. A tag can be moved by its owner."
                )

    if problems:
        print("Workflow privilege and pinning check failed:", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    print("Workflow privilege and pinning check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
