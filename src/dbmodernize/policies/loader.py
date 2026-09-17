"""Parse a playbook directory into a :class:`Playbook`.

A playbook is three Markdown files so architects can read and review it as prose, while
the tables inside it stay machine-checkable. Content that does not fit the tables is kept
verbatim in ``extended`` rather than being dropped.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from dbmodernize.errors import FindingSet, InputNotFoundError
from dbmodernize.models.approval import PolicyException
from dbmodernize.models.base import PlaybookRef
from dbmodernize.policies.models import (
    Directive,
    Playbook,
    Policy,
    PolicyCategory,
    TargetPolicy,
)
from dbmodernize.utils.io import read_text

CANONICAL_FILES = ("charter.md", "targets.md", "policies.md")

_VERSION = re.compile(r"^\s*version:\s*(?P<version>[\w.\-]+)\s*$", re.IGNORECASE | re.MULTILINE)
_HEADING = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<title>.+?)\s*$")
_SEPARATOR = re.compile(r"^\s*\|?[\s:\-|]+\|?\s*$")

REQUIRED_CHARTER_SECTIONS = ("Scope", "Outcomes", "Principles", "Stakeholders", "Decision rights")


def split_sections(markdown: str) -> dict[str, str]:
    """Split on level-2 headings. Content before the first ``##`` is keyed ``_preamble``."""
    sections: dict[str, str] = {}
    current = "_preamble"
    buffer: list[str] = []
    for line in markdown.splitlines():
        match = _HEADING.match(line)
        if match and len(match.group("hashes")) == 2:
            sections[current] = "\n".join(buffer).strip()
            current = match.group("title").strip()
            buffer = []
        else:
            buffer.append(line)
    sections[current] = "\n".join(buffer).strip()
    return {k: v for k, v in sections.items() if v or k != "_preamble"}


def parse_table(markdown: str, malformed: list[str] | None = None) -> list[dict[str, str]]:
    """Parse the first Markdown pipe table found in ``markdown``.

    Lines inside a fenced code block are never table rows, however many pipes they carry:
    a worked example in a fence must not become a live policy. A row whose cell count does
    not match the header is appended to ``malformed`` (when given) instead of being skipped
    in silence, because a mistyped policy row that quietly stops being enforced is worse
    than one that fails validation.
    """
    lines = [line.strip() for line in markdown.splitlines()]
    header: list[str] | None = None
    rows: list[dict[str, str]] = []
    in_fence = False

    for line in lines:
        if line.startswith("```") or line.startswith("~~~"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if not line.startswith("|"):
            if header is not None and rows:
                break
            continue
        if _SEPARATOR.match(line) and header is not None:
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if header is None:
            header = [cell.lower().replace(" ", "_") for cell in cells]
            continue
        if len(cells) != len(header):
            if malformed is not None:
                malformed.append(
                    f"row has {len(cells)} cell(s) but the header has {len(header)}: {line}"
                )
            continue
        rows.append(dict(zip(header, cells, strict=True)))
    return rows


def _parse_policies(text: str, findings: FindingSet, source: str) -> list[Policy]:
    policies: list[Policy] = []
    sections = split_sections(text)
    body = sections.get("Policies")
    if body is None:
        findings.add(
            rule="PLAYBOOK-MISSING-SECTION",
            message="policies.md has no '## Policies' section",
            path=source,
        )
        return policies

    malformed: list[str] = []
    for row in parse_table(body, malformed):
        try:
            policies.append(
                Policy(
                    id=row.get("id", ""),
                    category=PolicyCategory(row.get("category", "")),
                    subject=row.get("subject", ""),
                    directive=Directive(row.get("directive", "")),
                    requirement=row.get("requirement", ""),
                    applies_to=row.get("applies_to") or "all",
                )
            )
        except (ValidationError, ValueError) as exc:
            findings.add(
                rule="PLAYBOOK-POLICY-INVALID",
                message=f"Policy row {row.get('id', '<no id>')!r} is invalid: {exc}",
                path=source,
            )
    for problem in malformed:
        findings.add(
            rule="PLAYBOOK-ROW-MALFORMED",
            message=f"Policy table {problem}",
            path=source,
            hint="A row the parser cannot read is a policy that is not enforced.",
        )
    return policies


def _parse_exceptions(text: str, findings: FindingSet, source: str) -> list[PolicyException]:
    exceptions: list[PolicyException] = []
    body = split_sections(text).get("Exceptions")
    if not body:
        return exceptions

    malformed: list[str] = []
    rows = parse_table(body, malformed)
    for problem in malformed:
        findings.add(
            rule="PLAYBOOK-ROW-MALFORMED",
            message=f"Exception table {problem}",
            path=source,
            hint=(
                "A row the parser cannot read is an exception that is neither granted nor refused."
            ),
        )
    for row in rows:
        payload: dict[str, Any] = {
            "id": row.get("id", ""),
            "policy_id": row.get("policy_id", ""),
            "scope": row.get("scope", ""),
            "justification": row.get("justification", ""),
            "owner_role": row.get("owner_role", ""),
            "approver_role": row.get("approver_role", ""),
            "approver_principal": row.get("approver_principal", ""),
            "compensating_controls": [
                item.strip()
                for item in row.get("compensating_controls", "").split(";")
                if item.strip()
            ],
            "granted_on": row.get("granted_on", ""),
            "expires_on": row.get("expires_on", ""),
            "review_on": row.get("review_on", ""),
        }
        try:
            exceptions.append(PolicyException.model_validate(payload))
        except ValidationError as exc:
            findings.add(
                rule="PLAYBOOK-EXCEPTION-INVALID",
                message=(
                    f"Exception {row.get('id', '<no id>')!r} is invalid: {exc}. "
                    "Every exception needs scope, justification, owner, approver, "
                    "compensating controls, an expiry date, and a review date."
                ),
                path=source,
            )
    return exceptions


def _parse_targets(text: str, findings: FindingSet, source: str) -> list[TargetPolicy]:
    targets: list[TargetPolicy] = []
    sections = split_sections(text)
    for heading in ("Approved targets", "Prohibited targets"):
        body = sections.get(heading)
        if body is None:
            continue
        malformed: list[str] = []
        rows = parse_table(body, malformed)
        for problem in malformed:
            findings.add(
                rule="PLAYBOOK-ROW-MALFORMED",
                message=f"Target table under '{heading}' {problem}",
                path=source,
                hint="An unreadable target row is a target treated as prohibited by accident.",
            )
        for row in rows:
            status = row.get("status") or (
                "prohibited" if heading == "Prohibited targets" else "approved"
            )
            try:
                targets.append(
                    TargetPolicy(
                        target=row.get("target", ""),  # type: ignore[arg-type]
                        status=status,
                        conditions=row.get("conditions") or row.get("reason") or "",
                    )
                )
            except (ValidationError, ValueError) as exc:
                findings.add(
                    rule="PLAYBOOK-TARGET-INVALID",
                    message=f"Target row {row.get('target', '<no target>')!r} is invalid: {exc}",
                    path=source,
                )
    if not targets:
        findings.add(
            rule="PLAYBOOK-MISSING-SECTION",
            message="targets.md declares no targets under '## Approved targets'",
            path=source,
        )
    return targets


def _extended_content(sections: dict[str, str], known: set[str], prefix: str) -> dict[str, str]:
    return {
        f"{prefix}:{name}": body
        for name, body in sections.items()
        if name not in known and name != "_preamble" and body.strip()
    }


def load_playbook(directory: Path) -> tuple[Playbook | None, FindingSet]:
    """Load and structurally parse a playbook. Semantic checks live in the validator."""
    findings = FindingSet()
    if not directory.is_dir():
        raise InputNotFoundError(f"Playbook directory not found: {directory}")

    for filename in CANONICAL_FILES:
        if not (directory / filename).is_file():
            findings.add(
                rule="PLAYBOOK-MISSING-FILE",
                message=f"{filename} is missing. A playbook is exactly these three files.",
                path=str(directory),
            )
    if not findings.ok:
        return None, findings

    charter_text = read_text(directory / "charter.md")
    targets_text = read_text(directory / "targets.md")
    policies_text = read_text(directory / "policies.md")

    version_match = _VERSION.search(charter_text)
    if not version_match:
        findings.add(
            rule="PLAYBOOK-NO-VERSION",
            message=(
                "charter.md does not declare a version. Generated plans record the playbook "
                "version, so an unversioned playbook breaks traceability."
            ),
            path=str(directory / "charter.md"),
            hint="Add a line such as 'version: 1.0.0' near the top of charter.md.",
        )
    version = version_match.group("version") if version_match else "unknown"

    charter_sections = split_sections(charter_text)
    policies = _parse_policies(policies_text, findings, str(directory / "policies.md"))
    exceptions = _parse_exceptions(policies_text, findings, str(directory / "policies.md"))
    targets = _parse_targets(targets_text, findings, str(directory / "targets.md"))

    extended: dict[str, str] = {}
    extended |= _extended_content(charter_sections, set(REQUIRED_CHARTER_SECTIONS), "charter")
    extended |= _extended_content(
        split_sections(policies_text), {"Policies", "Exceptions"}, "policies"
    )
    extended |= _extended_content(
        split_sections(targets_text), {"Approved targets", "Prohibited targets"}, "targets"
    )

    playbook = Playbook(
        name=directory.name,
        version=version,
        path=directory.as_posix(),
        charter_sections=charter_sections,
        policies=policies,
        targets=targets,
        exceptions=exceptions,
        extended=extended,
    )
    return playbook, findings


def playbook_reference(playbook: Playbook, repo_root: Path | None = None) -> PlaybookRef:
    """Pin the governance contract in a form that survives leaving this machine.

    ``Playbook.path`` is absolute because the loader reads files with it. The reference
    embedded in artifacts must not be: an absolute path makes every generated document
    depend on one person's home directory, so the same evidence produces different output
    on a colleague's laptop and in CI.
    """
    path = Path(playbook.path)
    root = (repo_root or Path.cwd()).resolve()
    try:
        relative = path.resolve().relative_to(root)
    except ValueError:
        # A playbook outside the repository has no portable path. Its name is the most
        # that can honestly be recorded, and it is still enough to identify.
        relative = Path(playbook.name)
    return PlaybookRef(
        path=relative.as_posix(),
        version=playbook.version,
        policy_ids=[policy.id for policy in playbook.policies],
    )


def today() -> date:
    """Indirection so tests can pin 'now' without patching the stdlib."""
    return date.today()


__all__ = [
    "CANONICAL_FILES",
    "REQUIRED_CHARTER_SECTIONS",
    "load_playbook",
    "parse_table",
    "split_sections",
    "today",
]
