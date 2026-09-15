#!/usr/bin/env python
"""Render a validation report and exit non-zero on a no-go.

The exit code matters: a pipeline must not be able to walk past a no-go by accident.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dbmodernize.errors import DbModernizeError, ExitCode  # noqa: E402
from dbmodernize.pipeline import run_pipeline  # noqa: E402
from dbmodernize.utils.io import write_text  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engagement", type=Path, required=True)
    parser.add_argument("--input", dest="input_dir", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--playbook", type=Path, default=REPO_ROOT / "playbooks" / "default")
    parser.add_argument("--out", type=Path, default=Path("out"))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        result = run_pipeline(
            REPO_ROOT,
            args.engagement,
            args.input_dir,
            args.playbook,
            validation_report_path=args.report,
        )
    except DbModernizeError as error:
        print(f"error: {error}", file=sys.stderr)
        return int(error.exit_code)

    if result.validation_report is None:
        print(f"No validation report could be read from {args.report}", file=sys.stderr)
        return int(ExitCode.INPUT_NOT_FOUND)

    path = write_text(
        args.out / "validation-report.md",
        result.documents["validation-report.md"],
        force=args.force,
        dry_run=args.dry_run,
    )
    outcome = result.validation_report.outcome.value
    counts = result.validation_report.counts

    print(f"{'Would write' if args.dry_run else 'Wrote'} {path}")
    print(
        f"Outcome: {outcome}. "
        f"{counts['pass']} passed, {counts['fail']} failed, {counts['not-run']} not run."
    )

    if outcome == "no-go":
        print(
            "No-go. The documented rollback path applies, corrective issues are required, "
            "and this attempt is not a success.",
            file=sys.stderr,
        )
        return int(ExitCode.VALIDATION_FAILED)

    return int(ExitCode.OK)


if __name__ == "__main__":
    raise SystemExit(main())
