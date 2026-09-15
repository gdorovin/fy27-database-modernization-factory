"""Playbook parsing and governance rules.

The conflict and expiry checks are the ones that matter: a playbook that quietly contains
two contradictory rules produces decisions nobody can defend, and an exception that lapses
into permanence is how a temporary deviation becomes the architecture.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from dbmodernize.models.base import AzureTarget
from dbmodernize.policies.loader import load_playbook, parse_table, split_sections
from dbmodernize.policies.models import Directive, PolicyCategory
from dbmodernize.validators.playbook import REQUIRED_CATEGORIES, validate_playbook

AS_OF = date(2026, 3, 2)

POLICY_HEADER = (
    "| ID | Category | Subject | Directive | Requirement | Applies to |\n"
    "| --- | --- | --- | --- | --- | --- |\n"
)

EXCEPTION_HEADER = (
    "| ID | Policy ID | Scope | Justification | Owner role | Approver role | "
    "Approver principal | Compensating controls | Granted on | Expires on | Review on |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n"
)


def _minimal_policy_rows() -> str:
    """One policy per required category, so coverage checks pass by default."""
    rows = []
    subjects = {
        PolicyCategory.SECURITY: "network.public-endpoint",
        PolicyCategory.IDENTITY: "auth.method",
        PolicyCategory.NETWORKING: "network.private-endpoint",
        PolicyCategory.DATA: "data.classification",
        PolicyCategory.OBSERVABILITY: "monitoring.alerting",
        PolicyCategory.AVAILABILITY: "availability.rpo-rto",
        PolicyCategory.VALIDATION: "validation.blocking-checks",
    }
    for index, (category, subject) in enumerate(sorted(subjects.items()), start=1):
        rows.append(
            policy_row(
                f"TST-{index:03d}",
                category.value,
                subject,
                "required",
                f"A requirement for {category.value}.",
            )
        )
    return "\n".join(rows)


def policy_row(
    policy_id: str,
    category: str,
    subject: str,
    directive: str,
    requirement: str = "A requirement.",
    applies_to: str = "all",
) -> str:
    """Build one Markdown policy row, so no source line has to carry a whole table row."""
    return f"| {policy_id} | {category} | {subject} | {directive} | {requirement} | {applies_to} |"


def write_playbook(
    directory: Path,
    *,
    extra_policies: str = "",
    exceptions: str = "",
    version: str = "1.0.0",
    targets: str = "| azure-sql-database | approved | Fits database scope. |",
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)

    (directory / "charter.md").write_text(
        f"# Charter\n\nversion: {version}\n\n"
        "## Scope\n\nEverything in the fixture.\n\n"
        "## Outcomes\n\nNothing reaches production unreviewed.\n\n"
        "## Principles\n\nEvidence before recommendation.\n\n"
        "## Stakeholders\n\nThe usual five owner roles.\n\n"
        "## Decision rights\n\nHumans decide.\n",
        encoding="utf-8",
    )
    (directory / "targets.md").write_text(
        "# Targets\n\n## Approved targets\n\n"
        "| Target | Status | Conditions |\n| --- | --- | --- |\n"
        f"{targets}\n",
        encoding="utf-8",
    )
    body = "# Policies\n\n## Policies\n\n" + POLICY_HEADER + _minimal_policy_rows() + "\n"
    if extra_policies:
        body += extra_policies + "\n"
    if exceptions:
        body += "\n## Exceptions\n\n" + EXCEPTION_HEADER + exceptions + "\n"
    (directory / "policies.md").write_text(body, encoding="utf-8")
    return directory


class TestDefaultPlaybook:
    def test_it_validates(self, repo_root: Path) -> None:
        playbook, findings = validate_playbook(repo_root / "playbooks" / "default", as_of=AS_OF)
        assert playbook is not None
        assert findings.ok, "\n".join(f.render() for f in findings.errors)

    def test_it_covers_every_required_category(self, repo_root: Path) -> None:
        playbook, _ = validate_playbook(repo_root / "playbooks" / "default", as_of=AS_OF)
        assert playbook is not None
        present = {policy.category for policy in playbook.policies}
        assert present >= REQUIRED_CATEGORIES

    def test_policy_ids_are_unique(self, repo_root: Path) -> None:
        playbook, _ = validate_playbook(repo_root / "playbooks" / "default", as_of=AS_OF)
        assert playbook is not None
        ids = [policy.id for policy in playbook.policies]
        assert len(ids) == len(set(ids))

    def test_at_least_one_target_is_recommendable(self, repo_root: Path) -> None:
        playbook, _ = validate_playbook(repo_root / "playbooks" / "default", as_of=AS_OF)
        assert playbook is not None
        assert playbook.allowed_targets()

    def test_retaining_and_retiring_are_legitimate_outcomes(self, repo_root: Path) -> None:
        """A playbook that can only say 'migrate' is a sales script."""
        playbook, _ = validate_playbook(repo_root / "playbooks" / "default", as_of=AS_OF)
        assert playbook is not None
        allowed = set(playbook.allowed_targets())
        assert AzureTarget.RETAIN in allowed
        assert AzureTarget.RETIRE in allowed


class TestExamplePlaybooks:
    def test_every_example_validates(self, repo_root: Path) -> None:
        examples = sorted(d for d in (repo_root / "playbooks" / "examples").iterdir() if d.is_dir())
        assert examples, "no example playbooks found"

        for directory in examples:
            playbook, findings = validate_playbook(directory, as_of=AS_OF)
            assert playbook is not None, f"{directory.name} failed to load"
            assert findings.ok, f"{directory.name}: " + "\n".join(
                f.render() for f in findings.errors
            )


class TestConflictDetection:
    def test_contradictory_directives_fail(self, tmp_path: Path) -> None:
        """The repository refuses to choose between two rules nobody has reconciled."""
        directory = write_playbook(
            tmp_path / "conflicting",
            extra_policies="\n".join(
                [
                    policy_row("CNF-001", "security", "network.public-endpoint", "prohibited"),
                    policy_row("CNF-002", "security", "network.public-endpoint", "required"),
                ]
            ),
        )
        _, findings = validate_playbook(directory, as_of=AS_OF)
        assert any(f.rule == "PLAYBOOK-CONFLICT" for f in findings.errors)

    def test_opposing_soft_directives_are_a_warning(self, tmp_path: Path) -> None:
        directory = write_playbook(
            tmp_path / "soft",
            extra_policies="\n".join(
                [
                    policy_row("SFT-001", "cost", "cost.observation", "recommended"),
                    policy_row("SFT-002", "cost", "cost.observation", "discouraged"),
                ]
            ),
        )
        _, findings = validate_playbook(directory, as_of=AS_OF)
        assert findings.ok
        assert any(f.rule == "PLAYBOOK-CONFLICT-SOFT" for f in findings.warnings)

    def test_same_subject_in_different_scopes_is_not_a_conflict(self, tmp_path: Path) -> None:
        """Production and development can legitimately differ."""
        directory = write_playbook(
            tmp_path / "scoped",
            extra_policies="\n".join(
                [
                    policy_row(
                        "SCP-001",
                        "security",
                        "network.public-endpoint",
                        "prohibited",
                        applies_to="production",
                    ),
                    policy_row(
                        "SCP-002",
                        "security",
                        "network.public-endpoint",
                        "required",
                        applies_to="development",
                    ),
                ]
            ),
        )
        _, findings = validate_playbook(directory, as_of=AS_OF)
        assert not any(f.rule == "PLAYBOOK-CONFLICT" for f in findings.errors)

    def test_duplicate_policy_ids_fail(self, tmp_path: Path) -> None:
        """Artifacts cite policy ids; a duplicate makes a citation ambiguous."""
        directory = write_playbook(
            tmp_path / "duplicate",
            extra_policies="\n".join(
                [
                    policy_row("DUP-001", "security", "data.encryption-at-rest", "required"),
                    policy_row("DUP-001", "data", "data.classification", "required"),
                ]
            ),
        )
        _, findings = validate_playbook(directory, as_of=AS_OF)
        assert any(f.rule == "PLAYBOOK-DUPLICATE-POLICY" for f in findings.errors)


class TestExceptions:
    def _row(self, **overrides: str) -> str:
        fields = {
            "id": "EX-001",
            "policy_id": "TST-001",
            "scope": "One legacy tool",
            "justification": "The vendor has no supported alternative",
            "owner": "database-owner",
            "approver_role": "security-owner",
            "approver": "security-owner-a",
            "controls": "Rotated every 30 days; access restricted",
            "granted": "2026-01-15",
            "expires": "2026-06-30",
            "review": "2026-04-30",
        }
        fields.update(overrides)
        return (
            f"| {fields['id']} | {fields['policy_id']} | {fields['scope']} | "
            f"{fields['justification']} | {fields['owner']} | {fields['approver_role']} | "
            f"{fields['approver']} | {fields['controls']} | {fields['granted']} | "
            f"{fields['expires']} | {fields['review']} |"
        )

    def test_a_valid_exception_is_accepted(self, tmp_path: Path) -> None:
        directory = write_playbook(tmp_path / "ok", exceptions=self._row())
        playbook, findings = validate_playbook(directory, as_of=AS_OF)
        assert playbook is not None
        assert findings.ok, "\n".join(f.render() for f in findings.errors)
        assert len(playbook.exceptions) == 1

    def test_an_expired_exception_fails(self, tmp_path: Path) -> None:
        """An expired exception must not lapse quietly into permanence."""
        directory = write_playbook(tmp_path / "expired", exceptions=self._row())
        _, findings = validate_playbook(directory, as_of=date(2026, 7, 1))
        assert any(f.rule == "PLAYBOOK-EXCEPTION-EXPIRED" for f in findings.errors)

    def test_an_exception_without_compensating_controls_fails(self, tmp_path: Path) -> None:
        directory = write_playbook(tmp_path / "nocontrols", exceptions=self._row(controls=""))
        _, findings = validate_playbook(directory, as_of=AS_OF)
        assert any(f.rule == "PLAYBOOK-EXCEPTION-INVALID" for f in findings.errors)

    def test_an_exception_for_an_unknown_policy_fails(self, tmp_path: Path) -> None:
        directory = write_playbook(tmp_path / "unknown", exceptions=self._row(policy_id="ZZZ-999"))
        _, findings = validate_playbook(directory, as_of=AS_OF)
        assert any(f.rule == "PLAYBOOK-EXCEPTION-UNKNOWN-POLICY" for f in findings.errors)

    def test_requester_cannot_approve_their_own_exception(self, tmp_path: Path) -> None:
        directory = write_playbook(
            tmp_path / "self", exceptions=self._row(approver_role="database-owner")
        )
        _, findings = validate_playbook(directory, as_of=AS_OF)
        assert any(f.rule == "PLAYBOOK-EXCEPTION-INVALID" for f in findings.errors)


class TestStructuralRequirements:
    def test_missing_file_fails(self, tmp_path: Path) -> None:
        directory = write_playbook(tmp_path / "incomplete")
        (directory / "targets.md").unlink()
        _, findings = validate_playbook(directory, as_of=AS_OF)
        assert any(f.rule == "PLAYBOOK-MISSING-FILE" for f in findings.errors)

    def test_missing_version_fails(self, tmp_path: Path) -> None:
        """Generated plans record the playbook version; without one, traceability breaks."""
        directory = write_playbook(tmp_path / "unversioned")
        (directory / "charter.md").write_text(
            "# Charter\n\n## Scope\n\nx\n\n## Outcomes\n\nx\n\n## Principles\n\nx\n\n"
            "## Stakeholders\n\nx\n\n## Decision rights\n\nx\n",
            encoding="utf-8",
        )
        _, findings = validate_playbook(directory, as_of=AS_OF)
        assert any(f.rule == "PLAYBOOK-NO-VERSION" for f in findings.errors)

    def test_missing_charter_section_fails(self, tmp_path: Path) -> None:
        directory = write_playbook(tmp_path / "thin")
        (directory / "charter.md").write_text(
            "# Charter\n\nversion: 1.0.0\n\n## Scope\n\nOnly scope.\n", encoding="utf-8"
        )
        _, findings = validate_playbook(directory, as_of=AS_OF)
        assert any(f.rule == "PLAYBOOK-CHARTER-SECTION" for f in findings.errors)

    def test_category_gap_fails(self, tmp_path: Path) -> None:
        """Silence on a governance category is not a decision."""
        directory = tmp_path / "gap"
        write_playbook(directory)
        (directory / "policies.md").write_text(
            "# Policies\n\n## Policies\n\n"
            + POLICY_HEADER
            + policy_row("ONE-001", "security", "network.public-endpoint", "prohibited")
            + "\n",
            encoding="utf-8",
        )
        _, findings = validate_playbook(directory, as_of=AS_OF)
        assert any(f.rule == "PLAYBOOK-CATEGORY-GAP" for f in findings.errors)

    def test_all_targets_prohibited_fails(self, tmp_path: Path) -> None:
        directory = write_playbook(
            tmp_path / "noneallowed",
            targets="| azure-sql-database | prohibited | Not permitted here. |",
        )
        _, findings = validate_playbook(directory, as_of=AS_OF)
        assert any(f.rule == "PLAYBOOK-NO-ALLOWED-TARGET" for f in findings.errors)

    def test_unmapped_content_is_retained_with_a_warning(self, tmp_path: Path) -> None:
        """Nothing is dropped, but enforcement over it is best-effort and says so."""
        directory = write_playbook(tmp_path / "extended")
        with (directory / "policies.md").open("a", encoding="utf-8") as handle:
            handle.write("\n## Notes\n\nSome prose the schema does not model.\n")

        playbook, findings = validate_playbook(directory, as_of=AS_OF)
        assert playbook is not None
        assert findings.ok
        assert any(f.rule == "PLAYBOOK-EXTENDED" for f in findings.warnings)
        assert any("Notes" in key for key in playbook.extended)


class TestParsing:
    def test_sections_split_on_level_two_headings(self) -> None:
        sections = split_sections("preamble\n\n## One\n\nalpha\n\n## Two\n\nbeta\n")
        assert sections["One"] == "alpha"
        assert sections["Two"] == "beta"

    def test_table_parsing_ignores_the_separator_row(self) -> None:
        rows = parse_table("| A | B |\n| --- | --- |\n| 1 | 2 |\n")
        assert rows == [{"a": "1", "b": "2"}]

    def test_table_parsing_skips_malformed_rows(self) -> None:
        rows = parse_table("| A | B |\n| --- | --- |\n| 1 |\n| 3 | 4 |\n")
        assert rows == [{"a": "3", "b": "4"}]

    def test_load_returns_none_when_files_are_missing(self, tmp_path: Path) -> None:
        directory = tmp_path / "empty"
        directory.mkdir()
        playbook, findings = load_playbook(directory)
        assert playbook is None
        assert not findings.ok


@pytest.mark.parametrize("directive", list(Directive))
def test_every_directive_is_representable(directive: Directive) -> None:
    assert directive.value in {"required", "prohibited", "recommended", "discouraged"}
