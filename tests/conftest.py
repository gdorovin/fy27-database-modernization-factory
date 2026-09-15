"""Shared fixtures.

Everything here is offline and deterministic. No test may require an Azure subscription, a
database, a model, a paid API, or customer data.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from dbmodernize.models.base import PlaybookRef
from dbmodernize.models.engagement import Engagement, EngagementScope, EngagementTrigger
from dbmodernize.policies.models import Playbook
from dbmodernize.validators.playbook import validate_playbook

REPO_ROOT = Path(__file__).resolve().parents[1]

#: Pinned so that nothing in the suite depends on the wall clock.
AS_OF = date(2026, 3, 2)
TIMESTAMP = datetime(2026, 3, 2, 0, 0, tzinfo=UTC)


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def contracts_dir(repo_root: Path) -> Path:
    return repo_root / "contracts"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture(scope="session")
def default_playbook(repo_root: Path) -> Playbook:
    playbook, findings = validate_playbook(repo_root / "playbooks" / "default", as_of=AS_OF)
    assert playbook is not None, "the default playbook must load for the suite to be meaningful"
    assert findings.ok, [f.render() for f in findings.errors]
    return playbook


@pytest.fixture(scope="session")
def playbook_ref(default_playbook: Playbook) -> PlaybookRef:
    return PlaybookRef(
        path=default_playbook.path,
        version=default_playbook.version,
        policy_ids=[policy.id for policy in default_playbook.policies],
    )


@pytest.fixture
def engagement(playbook_ref: PlaybookRef) -> Engagement:
    """A minimal valid engagement. Tests that need more should build on this, not repeat it."""
    return Engagement(
        id="eng-test",
        engagement_id="eng-test",
        created_at=TIMESTAMP,
        updated_at=TIMESTAMP,
        author="test-author",
        playbook=playbook_ref,
        customer_alias="contoso-test",
        as_of=AS_OF,
        primary_trigger=EngagementTrigger.END_OF_SUPPORT,
        desired_outcomes=["Remove unsupported database versions from the regulated estate."],
        business_context="A synthetic estate used to exercise the pipeline.",
        scope=EngagementScope(in_scope=["Everything in the fixture"]),
    )


@pytest.fixture(scope="session")
def scenario_dirs(repo_root: Path) -> list[Path]:
    return sorted(
        directory
        for directory in (repo_root / "scenarios").iterdir()
        if directory.is_dir() and (directory / "scenario.yaml").is_file()
    )
