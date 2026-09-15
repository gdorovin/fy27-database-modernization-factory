"""Agent Skills: structure, selection boundaries, and safety language."""

from __future__ import annotations

from pathlib import Path

import pytest

from dbmodernize.validators.frontmatter import parse_document
from dbmodernize.validators.skill import REQUIRED_SECTIONS, validate_skill, validate_skills_tree

#: Every skill the pipeline expects to exist. A missing one is a gap in the lifecycle.
EXPECTED_SKILLS = frozenset(
    {
        "engagement-intake",
        "estate-discovery",
        "evidence-normalization",
        "modernization-classification",
        "azure-target-recommendation",
        "sql-server-modernization",
        "postgres-mysql-modernization",
        "oracle-heterogeneous-migration",
        "landing-zone-readiness",
        "business-case",
        "migration-wave-planning",
        "migration-plan-generation",
        "cutover-and-rollback",
        "migration-validation",
        "ai-data-readiness",
        "governance-compliance",
        "executive-brief",
    }
)


def skills_root(repo_root: Path) -> Path:
    return repo_root / ".github" / "skills"


def skill_dirs(repo_root: Path) -> list[Path]:
    return sorted(d for d in skills_root(repo_root).iterdir() if d.is_dir())


def test_all_skills_validate(repo_root: Path) -> None:
    findings = validate_skills_tree(skills_root(repo_root))
    assert findings.ok, "\n".join(f.render() for f in findings.errors)


def test_expected_skills_are_present(repo_root: Path) -> None:
    present = {d.name for d in skill_dirs(repo_root)}
    assert present >= EXPECTED_SKILLS, f"Missing skills: {sorted(EXPECTED_SKILLS - present)}"


def test_no_catch_all_skill(repo_root: Path) -> None:
    """A skill that could answer anything will be selected for everything."""
    banned = {"general", "helper", "misc", "utility", "common", "fabric-anything"}
    names = {d.name for d in skill_dirs(repo_root)}
    assert not (names & banned), f"Catch-all skill present: {sorted(names & banned)}"


class TestSkillStructure:
    def test_every_skill_has_all_required_sections(self, repo_root: Path) -> None:
        for directory in skill_dirs(repo_root):
            document, _ = parse_document(directory / "SKILL.md")
            assert document is not None
            missing = set(REQUIRED_SECTIONS) - set(document.sections())
            assert not missing, f"{directory.name} missing: {sorted(missing)}"

    def test_frontmatter_name_matches_directory(self, repo_root: Path) -> None:
        for directory in skill_dirs(repo_root):
            document, _ = parse_document(directory / "SKILL.md")
            assert document is not None
            assert document.frontmatter.get("name") == directory.name

    def test_do_not_invoke_always_names_an_alternative(self, repo_root: Path) -> None:
        """Telling a model what not to do without saying what to do leaves it improvising."""
        for directory in skill_dirs(repo_root):
            document, _ = parse_document(directory / "SKILL.md")
            assert document is not None
            body = document.sections()["Do not invoke when"].lower()
            assert "instead" in body or "defer to" in body, (
                f"{directory.name}: 'Do not invoke when' names no alternative"
            )

    def test_invoke_and_do_not_invoke_do_not_contradict(self, repo_root: Path) -> None:
        """A skill that claims a case in both sections cannot be selected reliably."""
        for directory in skill_dirs(repo_root):
            document, _ = parse_document(directory / "SKILL.md")
            assert document is not None
            sections = document.sections()
            invoke = _bullet_set(sections["Invoke when"])
            do_not = _bullet_set(sections["Do not invoke when"])
            overlap = invoke & do_not
            assert not overlap, f"{directory.name}: identical bullet in both sections"


def _bullet_set(body: str) -> set[str]:
    return {
        line.lstrip("- ").strip().lower()
        for line in body.splitlines()
        if line.strip().startswith("- ")
    }


class TestSelectionBoundaries:
    """Every skill must be distinguishable from every other by description alone."""

    def test_descriptions_are_unique(self, repo_root: Path) -> None:
        seen: dict[str, str] = {}
        for directory in skill_dirs(repo_root):
            document, _ = parse_document(directory / "SKILL.md")
            assert document is not None
            description = str(document.frontmatter["description"]).strip()
            assert description not in seen, (
                f"{directory.name} and {seen[description]} share a description"
            )
            seen[description] = directory.name

    def test_platform_skills_redirect_to_each_other(self, repo_root: Path) -> None:
        """The three platform skills are the easiest pair to confuse; they must cross-refer."""
        expected = {
            "sql-server-modernization": [
                "postgres-mysql-modernization",
                "oracle-heterogeneous-migration",
            ],
            "postgres-mysql-modernization": [
                "sql-server-modernization",
                "oracle-heterogeneous-migration",
            ],
            "oracle-heterogeneous-migration": [
                "sql-server-modernization",
                "postgres-mysql-modernization",
            ],
        }
        for name, others in expected.items():
            body = (skills_root(repo_root) / name / "SKILL.md").read_text(encoding="utf-8")
            for other in others:
                assert other in body, f"{name} does not redirect to {other}"


class TestSkillValidatorItself:
    """The validator must be able to fail, or it proves nothing about the skills."""

    def _write(self, directory: Path, frontmatter: str, body: str) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "SKILL.md").write_text(
            f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8"
        )
        return directory

    def test_missing_frontmatter_fails(self, tmp_path: Path) -> None:
        directory = tmp_path / "example-skill"
        directory.mkdir()
        (directory / "SKILL.md").write_text("# No frontmatter here\n", encoding="utf-8")
        findings = validate_skill(directory)
        assert any(f.rule == "FRONTMATTER-MISSING" for f in findings.errors)

    def test_name_mismatch_fails(self, tmp_path: Path) -> None:
        directory = self._write(
            tmp_path / "example-skill",
            "name: something-else\ndescription: " + "x" * 80,
            "## Invoke when\n\n" + "x" * 40,
        )
        findings = validate_skill(directory)
        assert any(f.rule == "SKILL-NAME-MISMATCH" for f in findings.errors)

    def test_placeholder_section_fails(self, tmp_path: Path) -> None:
        directory = self._write(
            tmp_path / "example-skill",
            "name: example-skill\ndescription: " + "A distinctive description. " * 4,
            "\n".join(f"## {section}\n\nTBD\n" for section in REQUIRED_SECTIONS),
        )
        findings = validate_skill(directory)
        assert any(f.rule == "SKILL-EMPTY-SECTION" for f in findings.errors)

    def test_unsafe_guidance_fails(self, tmp_path: Path) -> None:
        directory = self._write(
            tmp_path / "example-skill",
            "name: example-skill\ndescription: " + "A distinctive description. " * 4,
            "## Procedure\n\nDeliver the migration with zero downtime for the customer. "
            + "x" * 40,
        )
        findings = validate_skill(directory)
        assert any("ZERO-DOWNTIME" in f.rule for f in findings.errors)


@pytest.mark.parametrize(
    ("request_text", "expected_skill"),
    [
        ("We are starting a new engagement and need to capture outcomes", "engagement-intake"),
        ("Map this CSV export onto the evidence contract", "evidence-normalization"),
        ("Which Azure target fits this workload", "azure-target-recommendation"),
        ("We have an Oracle estate under licensing pressure", "oracle-heterogeneous-migration"),
        ("Our PostgreSQL version is unsupported", "postgres-mysql-modernization"),
        ("Group these workloads into waves", "migration-wave-planning"),
        ("Define the rollback triggers for the window", "cutover-and-rollback"),
        ("Is this estate ready for an assistant over customer data", "ai-data-readiness"),
        ("Audit the approval trail before sign-off", "governance-compliance"),
    ],
)
def test_request_wording_appears_in_the_intended_skill(
    repo_root: Path, request_text: str, expected_skill: str
) -> None:
    """A weak proxy for selection: the vocabulary of the request should live in the skill.

    It cannot prove a model will choose correctly, but it does catch a skill whose text has
    drifted away from the requests it is supposed to serve.
    """
    body = (skills_root(repo_root) / expected_skill / "SKILL.md").read_text(encoding="utf-8")
    words = [word for word in request_text.lower().split() if len(word) > 4]
    matched = sum(1 for word in words if word in body.lower())
    assert matched >= max(1, len(words) // 2), (
        f"{expected_skill} matches only {matched} of {len(words)} distinctive words "
        f"from {request_text!r}"
    )
