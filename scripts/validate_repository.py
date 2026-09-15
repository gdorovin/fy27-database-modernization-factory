#!/usr/bin/env python
"""Repository structure and safety validation.

Thin wrapper so pre-commit and CI can call the same checks the CLI exposes.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dbmodernize.errors import ExitCode  # noqa: E402
from dbmodernize.validators.repository import validate_repository  # noqa: E402
from dbmodernize.validators.schema import check_schema_self_validity  # noqa: E402


def main() -> int:
    findings = validate_repository(REPO_ROOT)
    findings.extend(check_schema_self_validity(REPO_ROOT))

    for finding in findings:
        print(finding.render(), file=sys.stderr if finding.severity == "error" else sys.stdout)

    if findings.ok:
        warnings = f" ({len(findings.warnings)} warning(s))" if findings.warnings else ""
        print(f"Repository validation passed{warnings}.")
        return int(ExitCode.OK)

    print(f"Repository validation failed with {len(findings.errors)} error(s).", file=sys.stderr)
    return int(ExitCode.VALIDATION_FAILED)


if __name__ == "__main__":
    raise SystemExit(main())
