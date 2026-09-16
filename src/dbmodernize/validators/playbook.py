"""Semantic validation of a playbook: duplicates, conflicts, coverage, expiry."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from pathlib import Path

from dbmodernize.errors import FindingSet
from dbmodernize.policies.loader import REQUIRED_CHARTER_SECTIONS, load_playbook, today
from dbmodernize.policies.models import (
    HARD_CONFLICTS,
    SOFT_CONFLICTS,
    Directive,
    Playbook,
    PolicyCategory,
)

#: Longest exception this repository will accept without complaint, measured from the grant
#: date to the expiry date. Deliberately clock-free: the question "is this exception too
#: long?" has the same answer today and in five years, so it must not depend on when it is
#: asked. `policies.md` names 90 days as the ceiling for a real exception.
MAX_EXCEPTION_DAYS = 90

#: Categories a playbook must speak to. Silence on any of these is a governance gap.
REQUIRED_CATEGORIES = frozenset(
    {
        PolicyCategory.SECURITY,
        PolicyCategory.IDENTITY,
        PolicyCategory.NETWORKING,
        PolicyCategory.DATA,
        PolicyCategory.OBSERVABILITY,
        PolicyCategory.AVAILABILITY,
        PolicyCategory.VALIDATION,
    }
)


def validate_playbook(
    directory: Path, as_of: date | None = None
) -> tuple[Playbook | None, FindingSet]:
    playbook, findings = load_playbook(directory)
    if playbook is None:
        return None, findings

    as_of = as_of or today()
    findings.extend(_check_duplicate_ids(playbook, directory))
    findings.extend(_check_conflicts(playbook, directory))
    findings.extend(_check_charter(playbook, directory))
    findings.extend(_check_category_coverage(playbook, directory))
    findings.extend(_check_targets(playbook, directory))
    findings.extend(_check_exceptions(playbook, directory, as_of))
    findings.extend(_warn_extended(playbook, directory))
    return playbook, findings


def _check_duplicate_ids(playbook: Playbook, directory: Path) -> FindingSet:
    findings = FindingSet()
    seen: dict[str, int] = defaultdict(int)
    for policy in playbook.policies:
        seen[policy.id] += 1
    for policy_id, count in sorted(seen.items()):
        if count > 1:
            findings.add(
                rule="PLAYBOOK-DUPLICATE-POLICY",
                message=(
                    f"Policy id {policy_id} appears {count} times. Artifacts cite policy ids, "
                    "so a duplicate makes a citation ambiguous."
                ),
                path=str(directory / "policies.md"),
            )
    return findings


def _check_conflicts(playbook: Playbook, directory: Path) -> FindingSet:
    """Two policies over the same subject and scope that contradict each other."""
    findings = FindingSet()
    grouped: dict[tuple[str, str], list[tuple[str, Directive]]] = defaultdict(list)
    for policy in playbook.policies:
        grouped[policy.scope_key].append((policy.id, policy.directive))

    for (subject, scope), entries in sorted(grouped.items()):
        directives = {directive for _, directive in entries}
        ids = ", ".join(sorted(policy_id for policy_id, _ in entries))
        for pair in HARD_CONFLICTS:
            if pair <= directives:
                findings.add(
                    rule="PLAYBOOK-CONFLICT",
                    message=(
                        f"Policies {ids} give contradictory directives for subject "
                        f"{subject!r} in scope {scope!r}: "
                        + " and ".join(sorted(d.value for d in pair))
                        + ". Resolve the conflict; the repository will not choose."
                    ),
                    path=str(directory / "policies.md"),
                )
        for pair in SOFT_CONFLICTS:
            if pair <= directives:
                findings.add(
                    rule="PLAYBOOK-CONFLICT-SOFT",
                    message=(
                        f"Policies {ids} pull in opposite directions for subject {subject!r} "
                        f"in scope {scope!r}: " + " and ".join(sorted(d.value for d in pair)) + "."
                    ),
                    path=str(directory / "policies.md"),
                    severity="warning",
                )
    return findings


def _check_charter(playbook: Playbook, directory: Path) -> FindingSet:
    findings = FindingSet()
    for section in REQUIRED_CHARTER_SECTIONS:
        if section not in playbook.charter_sections:
            findings.add(
                rule="PLAYBOOK-CHARTER-SECTION",
                message=f"charter.md is missing the '## {section}' section",
                path=str(directory / "charter.md"),
            )
    return findings


def _check_category_coverage(playbook: Playbook, directory: Path) -> FindingSet:
    findings = FindingSet()
    present = {policy.category for policy in playbook.policies}
    for category in sorted(REQUIRED_CATEGORIES - present):
        findings.add(
            rule="PLAYBOOK-CATEGORY-GAP",
            message=(
                f"No policy covers the {category.value!r} category. Silence is not a "
                "decision; state the position even if it is 'no additional requirement'."
            ),
            path=str(directory / "policies.md"),
        )
    return findings


def _check_targets(playbook: Playbook, directory: Path) -> FindingSet:
    findings = FindingSet()
    seen: set[str] = set()
    for entry in playbook.targets:
        if entry.target.value in seen:
            findings.add(
                rule="PLAYBOOK-DUPLICATE-TARGET",
                message=f"Target {entry.target.value} is listed more than once",
                path=str(directory / "targets.md"),
            )
        seen.add(entry.target.value)

    if not playbook.allowed_targets():
        findings.add(
            rule="PLAYBOOK-NO-ALLOWED-TARGET",
            message="Every target is prohibited, so no recommendation can ever be made",
            path=str(directory / "targets.md"),
        )
    return findings


def _check_exceptions(playbook: Playbook, directory: Path, as_of: date) -> FindingSet:
    findings = FindingSet()
    known_policy_ids = {policy.id for policy in playbook.policies}
    seen: set[str] = set()

    for exception in playbook.exceptions:
        if exception.id in seen:
            findings.add(
                rule="PLAYBOOK-DUPLICATE-EXCEPTION",
                message=f"Exception id {exception.id} appears more than once",
                path=str(directory / "policies.md"),
            )
        seen.add(exception.id)

        if exception.policy_id not in known_policy_ids:
            findings.add(
                rule="PLAYBOOK-EXCEPTION-UNKNOWN-POLICY",
                message=(
                    f"Exception {exception.id} excepts {exception.policy_id}, which is not "
                    "a policy in this playbook."
                ),
                path=str(directory / "policies.md"),
            )
        if exception.is_expired(as_of):
            findings.add(
                rule="PLAYBOOK-EXCEPTION-EXPIRED",
                message=(
                    f"Exception {exception.id} expired on {exception.expires_on.isoformat()}. "
                    "Renew it with fresh justification or remove it; an expired exception "
                    "must not lapse quietly into permanence."
                ),
                path=str(directory / "policies.md"),
            )

        granted = (exception.expires_on - exception.granted_on).days
        if granted > MAX_EXCEPTION_DAYS:
            findings.add(
                rule="PLAYBOOK-EXCEPTION-HORIZON",
                message=(
                    f"Exception {exception.id} runs for {granted} days, above the "
                    f"{MAX_EXCEPTION_DAYS}-day ceiling. An exception long enough to outlive "
                    "the people who agreed to it is a policy change wearing an exception's "
                    "clothes; change the policy or shorten the exception."
                ),
                path=str(directory / "policies.md"),
                severity="warning",
            )
    return findings


def _warn_extended(playbook: Playbook, directory: Path) -> FindingSet:
    findings = FindingSet()
    for key in sorted(playbook.extended):
        findings.add(
            rule="PLAYBOOK-EXTENDED",
            message=(
                f"Section {key!r} is outside the playbook schema. It is retained verbatim, "
                "but enforcement over it is best-effort only."
            ),
            path=str(directory),
            severity="warning",
        )
    return findings


__all__ = ["REQUIRED_CATEGORIES", "validate_playbook"]
