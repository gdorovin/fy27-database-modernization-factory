#!/usr/bin/env python
"""Run scenarios against their committed expectations.

Pass ``--update`` to regenerate expectations, then review every line of the diff.
Regenerating to make a failure disappear defeats the purpose of the snapshot, and the
scenario acceptance criteria exist to catch exactly that.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dbmodernize.errors import ExitCode  # noqa: E402
from dbmodernize.validators.scenario import (  # noqa: E402
    validate_scenario,
    validate_scenarios_tree,
)


def main(argv: list[str]) -> int:
    update = "--update" in argv
    positional = [arg for arg in argv if not arg.startswith("-")]
    target = Path(positional[0]) if positional else REPO_ROOT / "scenarios"

    findings = (
        validate_scenario(REPO_ROOT, target, update=update)
        if (target / "scenario.yaml").is_file()
        else validate_scenarios_tree(REPO_ROOT, target, update=update)
    )

    for finding in findings:
        print(finding.render(), file=sys.stderr if finding.severity == "error" else sys.stdout)

    if not findings.ok:
        print(f"Scenario validation failed with {len(findings.errors)} error(s).", file=sys.stderr)
        return int(ExitCode.VALIDATION_FAILED)

    print("Scenario validation passed.")
    return int(ExitCode.OK)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
