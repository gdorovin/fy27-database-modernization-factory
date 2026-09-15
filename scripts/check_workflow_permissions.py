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
                    if level == "write" and scope not in {
                        "security-events",
                        "pull-requests",
                        "contents",
                        "id-token",
                        "attestations",
                    }:
                        problems.append(
                            f"{relative}: job '{job_name}' requests write on '{scope}'. "
                            "Justify it in a comment or narrow it."
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
