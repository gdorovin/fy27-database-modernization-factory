#!/usr/bin/env python
"""Validate Agent Skills. Thin wrapper over the CLI so CI and hooks share one code path."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dbmodernize.errors import ExitCode  # noqa: E402
from dbmodernize.validators.skill import validate_skill, validate_skills_tree  # noqa: E402


def main(argv: list[str]) -> int:
    target = Path(argv[0]) if argv else REPO_ROOT / ".github" / "skills"

    findings = (
        validate_skill(target) if (target / "SKILL.md").is_file() else validate_skills_tree(target)
    )

    for finding in findings:
        print(finding.render(), file=sys.stderr if finding.severity == "error" else sys.stdout)

    if not findings.ok:
        print(f"Skill validation failed with {len(findings.errors)} error(s).", file=sys.stderr)
        return int(ExitCode.VALIDATION_FAILED)

    warnings = f" ({len(findings.warnings)} warning(s))" if findings.warnings else ""
    print(f"Skill validation passed{warnings}.")
    return int(ExitCode.OK)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
