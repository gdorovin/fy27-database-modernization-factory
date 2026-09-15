#!/usr/bin/env python
"""Validate a playbook. Thin wrapper over the CLI so CI and hooks share one code path."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dbmodernize.errors import ExitCode  # noqa: E402
from dbmodernize.validators.playbook import validate_playbook  # noqa: E402


def main(argv: list[str]) -> int:
    target = Path(argv[0]) if argv else REPO_ROOT / "playbooks" / "default"
    as_of = date.fromisoformat(argv[1]) if len(argv) > 1 else None

    playbook, findings = validate_playbook(target, as_of=as_of)
    for finding in findings:
        print(finding.render(), file=sys.stderr if finding.severity == "error" else sys.stdout)

    if not findings.ok:
        print(f"Playbook {target} failed with {len(findings.errors)} error(s).", file=sys.stderr)
        return int(ExitCode.VALIDATION_FAILED)

    assert playbook is not None
    print(
        f"Playbook {playbook.name} v{playbook.version} passed: "
        f"{len(playbook.policies)} policies, {len(playbook.targets)} target entries, "
        f"{len(playbook.exceptions)} exception(s)."
    )
    return int(ExitCode.OK)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
