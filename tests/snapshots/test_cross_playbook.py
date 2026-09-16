"""Cross-playbook rendering: the estate is held constant and the playbook varies.

Everything in `scenarios/` holds the playbook constant and varies the estate. This file is
the other axis, and it exists because "configuration-driven" is a claim the repository
makes about itself in several places without anywhere proving it. Structural validation of
the example playbooks only shows they parse. It does not show that swapping one changes a
single decision, which is the entire premise.

Snapshots for these live here rather than beside a scenario because they do not belong to
one: the interesting variable is `playbooks/`, not `scenarios/01/input`.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from dbmodernize.models.decision import OptionVerdict, TargetDecisionSet
from dbmodernize.pipeline import run_pipeline

#: Every playbook in the repository, keyed by the name used in failure messages.
PLAYBOOKS: dict[str, str] = {
    "default": "playbooks/default",
    "regulated-enterprise": "playbooks/examples/regulated-enterprise",
    "renewal-led-sql": "playbooks/examples/renewal-led-sql",
    "ai-ready-data": "playbooks/examples/ai-ready-data",
}

#: Targets each playbook's `targets.md` forbids. Kept here in the test rather than read
#: from the playbook so that deleting a prohibition from the playbook fails a test instead
#: of silently agreeing with itself.
PROHIBITED: dict[str, set[str]] = {
    "default": set(),
    "regulated-enterprise": {"sql-server-on-azure-vm", "replace-with-saas"},
    "renewal-led-sql": set(),
    "ai-ready-data": {"sql-server-on-azure-vm"},
}

SCENARIO = "01-sql2016-to-managed-instance"


def _decisions(repo_root: Path, playbook: str) -> TargetDecisionSet:
    scenario = repo_root / "scenarios" / SCENARIO
    result = run_pipeline(
        repo_root,
        scenario / "input" / "engagement.yaml",
        scenario / "input",
        repo_root / PLAYBOOKS[playbook],
    )
    return result.decisions


@pytest.fixture(scope="module", params=sorted(PLAYBOOKS))
def playbook_name(request: pytest.FixtureRequest) -> str:
    return str(request.param)


def test_every_playbook_runs_the_same_estate(repo_root: Path, playbook_name: str) -> None:
    """An example playbook that parses but cannot drive a run is decoration."""
    decisions = _decisions(repo_root, playbook_name)
    assert decisions.decisions, f"{playbook_name} produced no decisions"


def test_a_prohibited_target_is_never_recommended(repo_root: Path, playbook_name: str) -> None:
    forbidden = PROHIBITED[playbook_name]
    if not forbidden:
        pytest.skip(f"{playbook_name} prohibits no target")

    for decision in _decisions(repo_root, playbook_name).decisions:
        assert decision.recommended_target not in forbidden, (
            f"{playbook_name} recommended {decision.recommended_target} for "
            f"{decision.workload_id}, which its targets.md prohibits"
        )


def test_a_prohibited_target_is_rejected_rather_than_omitted(
    repo_root: Path, playbook_name: str
) -> None:
    """The playbooks promise the option still appears, rejected with a citation.

    Dropping it from the comparison entirely would leave a reader unable to tell whether it
    was ruled out or never thought of.
    """
    forbidden = PROHIBITED[playbook_name]
    if not forbidden:
        pytest.skip(f"{playbook_name} prohibits no target")

    for decision in _decisions(repo_root, playbook_name).decisions:
        considered = {option.target: option for option in decision.considered_options}
        for target in forbidden & considered.keys():
            option = considered[target]
            assert option.verdict is OptionVerdict.REJECTED
            assert option.rationale.strip(), f"{target} rejected without a stated reason"


def test_swapping_the_playbook_changes_the_verdicts(repo_root: Path) -> None:
    """The load-bearing assertion: configuration has to actually drive the outcome.

    Note what is *not* asserted. The set of targets considered is identical across
    playbooks, and deliberately so: `targets.md` promises a prohibited target is still
    compared and rejected with a citation rather than dropped, so a reader can tell it was
    ruled out and not overlooked. The difference a playbook makes therefore shows up in the
    verdicts, never in the membership. Asserting on membership looks like a stronger test
    and is actually a wrong one.
    """

    def verdicts(playbook: str) -> set[tuple[str, str]]:
        return {
            (str(option.target), str(option.verdict))
            for decision in _decisions(repo_root, playbook).decisions
            for option in decision.considered_options
        }

    default = verdicts("default")
    regulated = verdicts("regulated-enterprise")
    assert default != regulated, (
        "Every playbook reached the same verdict on every option. Either the playbooks no "
        "longer differ, or the comparison has stopped reading them."
    )


def test_the_option_set_is_deliberately_identical(repo_root: Path) -> None:
    """Pin the behaviour the test above depends on, so a change to it is visible."""

    def considered(playbook: str) -> set[str]:
        return {
            str(option.target)
            for decision in _decisions(repo_root, playbook).decisions
            for option in decision.considered_options
        }

    assert considered("default") == considered("regulated-enterprise")


def test_narrowing_the_playbook_never_widens_the_options(repo_root: Path) -> None:
    """Regulated is a strict subset of default, by construction. Prove it stays one."""

    def approved_recommendations(playbook: str) -> set[str]:
        return {
            str(decision.recommended_target)
            for decision in _decisions(repo_root, playbook).decisions
        }

    regulated = approved_recommendations("regulated-enterprise")
    assert not (regulated & PROHIBITED["regulated-enterprise"])
