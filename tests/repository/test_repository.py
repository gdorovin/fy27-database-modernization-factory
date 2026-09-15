"""Repository structure and safety rules.

These assert that the promises made in the README and SECURITY.md are still true, so a
promise cannot quietly stop being kept.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from dbmodernize.cli import command_names
from dbmodernize.validators.repository import (
    REQUIRED_PATHS,
    check_dated_claims,
    check_downtime_language,
    check_no_empty_directories,
    check_no_restricted_fixtures,
    check_no_secrets,
    check_readme_commands,
    check_structure,
    validate_repository,
)
from dbmodernize.validators.schema import check_schema_self_validity


def test_repository_passes_every_check(repo_root: Path) -> None:
    findings = validate_repository(repo_root)
    findings.extend(check_schema_self_validity(repo_root))
    assert findings.ok, "\n".join(f.render() for f in findings.errors)


@pytest.mark.parametrize("relative", REQUIRED_PATHS)
def test_required_path_exists(repo_root: Path, relative: str) -> None:
    assert (repo_root / relative).exists(), f"missing: {relative}"


def test_no_empty_or_decorative_directories(repo_root: Path) -> None:
    """A directory holding only an unexplained keep file makes the tree look more complete
    than it is."""
    findings = check_no_empty_directories(repo_root)
    assert findings.ok, "\n".join(f.render() for f in findings.errors)


def test_no_secrets_or_secret_like_content(repo_root: Path) -> None:
    findings = check_no_secrets(repo_root)
    assert findings.ok, "\n".join(f.render() for f in findings.errors)


def test_nothing_above_internal_classification_is_committed(repo_root: Path) -> None:
    findings = check_no_restricted_fixtures(repo_root)
    assert findings.ok, "\n".join(f.render() for f in findings.errors)


def test_no_unqualified_zero_downtime_claim(repo_root: Path) -> None:
    findings = check_downtime_language(repo_root)
    assert findings.ok, "\n".join(f.render() for f in findings.errors)


def test_perishable_guidance_carries_a_verification_date(repo_root: Path) -> None:
    findings = check_dated_claims(repo_root)
    assert findings.ok, "\n".join(f.render() for f in findings.errors)


def test_readme_only_documents_real_commands(repo_root: Path) -> None:
    findings = check_readme_commands(repo_root)
    assert findings.ok, "\n".join(f.render() for f in findings.errors)


def test_every_command_appears_in_the_readme(repo_root: Path) -> None:
    """The reverse direction: a command nobody documents is a command nobody finds."""
    readme = (repo_root / "README.md").read_text(encoding="utf-8")
    undocumented = [name for name in sorted(command_names()) if name not in readme]
    assert not undocumented, f"Commands missing from the README: {undocumented}"


def test_structure_check_detects_a_missing_path(tmp_path: Path) -> None:
    """The check must be able to fail, or it is decoration."""
    findings = check_structure(tmp_path)
    assert not findings.ok
    assert any(f.rule == "REPO-MISSING-PATH" for f in findings.errors)


def test_secret_check_detects_a_planted_connection_string(tmp_path: Path) -> None:
    (tmp_path / "leak.md").write_text(
        "Server=tcp:db;Password=Str0ng!Passw0rd;Encrypt=true", encoding="utf-8"
    )
    findings = check_no_secrets(tmp_path)
    assert not findings.ok
    assert any(f.rule == "REPO-SECRET-LIKE" for f in findings.errors)


def test_downtime_check_detects_an_unqualified_claim(tmp_path: Path) -> None:
    (tmp_path / "pitch.md").write_text(
        "## Approach\n\nWe will deliver this with zero downtime.\n", encoding="utf-8"
    )
    findings = check_downtime_language(tmp_path)
    assert not findings.ok


def test_downtime_check_permits_a_prohibition(tmp_path: Path) -> None:
    (tmp_path / "rule.md").write_text(
        "## Approach\n\nNever claim zero downtime without a measured rehearsal.\n",
        encoding="utf-8",
    )
    assert check_downtime_language(tmp_path).ok


def test_downtime_check_permits_an_avoid_section(tmp_path: Path) -> None:
    """A rule has to be able to name the phrase it forbids."""
    (tmp_path / "skill.md").write_text(
        "## Avoid\n\n- Claiming zero downtime under any wording.\n", encoding="utf-8"
    )
    assert check_downtime_language(tmp_path).ok


def test_classification_check_detects_restricted_content(tmp_path: Path) -> None:
    (tmp_path / "evidence.json").write_text('{"classification": "restricted"}', encoding="utf-8")
    findings = check_no_restricted_fixtures(tmp_path)
    assert not findings.ok


def test_no_real_looking_identifiers(repo_root: Path) -> None:
    """Placeholders must be obviously fake, so nobody mistakes one for a real value."""
    guid = re.compile(
        r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
        re.IGNORECASE,
    )
    all_zero = "00000000-0000-0000-0000-000000000000"
    offenders: list[str] = []

    skip = {".git", ".venv", "__pycache__", ".mypy_cache", ".ruff_cache", ".pytest_cache"}
    for path in repo_root.rglob("*"):
        if not path.is_file() or any(part in skip for part in path.parts):
            continue
        if path.suffix.lower() not in {".md", ".json", ".yaml", ".yml", ".py", ".bicep"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for match in guid.finditer(text):
            if match.group(0).lower() != all_zero:
                offenders.append(f"{path.relative_to(repo_root).as_posix()}: {match.group(0)}")

    assert not offenders, f"Real-looking identifiers found: {offenders}"


def test_gitignore_blocks_credentials_and_engagement_output(repo_root: Path) -> None:
    text = (repo_root / ".gitignore").read_text(encoding="utf-8")
    for pattern in (".env", "*.pem", "*.key", "/engagements/", "/out/"):
        assert pattern in text, f".gitignore does not cover {pattern}"
