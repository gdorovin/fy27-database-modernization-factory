#!/usr/bin/env python
"""Generate GitHub issue definitions to disk.

Definitions only. This script never contacts the GitHub API, and the CLI refuses
``--create`` by design, so a dry run cannot surprise a repository with fifty new issues.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from dbmodernize.errors import DbModernizeError, ExitCode  # noqa: E402
from dbmodernize.issue_generation.generator import generate_issues  # noqa: E402
from dbmodernize.pipeline import run_pipeline  # noqa: E402
from dbmodernize.utils.io import write_yaml  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engagement", type=Path, required=True)
    parser.add_argument("--input", dest="input_dir", type=Path, required=True)
    parser.add_argument("--playbook", type=Path, default=REPO_ROOT / "playbooks" / "default")
    parser.add_argument("--out", type=Path, default=Path("out"))
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        result = run_pipeline(REPO_ROOT, args.engagement, args.input_dir, args.playbook)
        issues = generate_issues(
            result.engagement,
            result.inventory,
            result.decisions,
            result.waves,
            result.playbook_ref,
        )
        path = write_yaml(
            args.out / "issues.yaml",
            issues.model_dump(mode="json"),
            force=args.force,
            dry_run=args.dry_run,
        )
    except DbModernizeError as error:
        print(f"error: {error}", file=sys.stderr)
        return int(error.exit_code)

    verb = "Would write" if args.dry_run else "Wrote"
    print(f"{verb} {path}: {len(issues.issues)} issue definition(s).")
    print("Review them before creating anything. This script creates no live issues.")
    return int(ExitCode.OK)


if __name__ == "__main__":
    raise SystemExit(main())
