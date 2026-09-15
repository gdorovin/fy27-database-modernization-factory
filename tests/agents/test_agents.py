"""Agents: structure, least privilege, and the approval boundary.

The privilege tests matter more than the structural ones. An agent whose documented role is
non-editing but whose tool list includes an editor will eventually edit something, and the
governance story collapses the first time it does.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from dbmodernize.validators.agent import (
    DELEGATION_ALLOWED,
    KNOWN_TOOLS,
    MUTATING_TOOLS,
    NON_EDITING_AGENTS,
    REQUIRED_SECTIONS,
    validate_agent,
    validate_agents_tree,
)
from dbmodernize.validators.frontmatter import parse_document

EXPECTED_AGENTS = frozenset(
    {
        "engagement-orchestrator",
        "estate-assessor",
        "target-architect",
        "value-advisor",
        "migration-planner",
        "implementation-engineer",
        "validation-engineer",
        "governance-reviewer",
    }
)


def agents_root(repo_root: Path) -> Path:
    return repo_root / ".github" / "agents"


def agent_files(repo_root: Path) -> list[Path]:
    return sorted(agents_root(repo_root).glob("*.agent.md"))


def test_all_agents_validate(repo_root: Path) -> None:
    findings = validate_agents_tree(agents_root(repo_root))
    assert findings.ok, "\n".join(f.render() for f in findings.errors)


def test_expected_agents_are_present(repo_root: Path) -> None:
    present = {path.name.removesuffix(".agent.md") for path in agent_files(repo_root)}
    assert present == EXPECTED_AGENTS, f"Unexpected agent set: {sorted(present)}"


class TestLeastPrivilege:
    def test_every_agent_declares_an_explicit_tool_allowlist(self, repo_root: Path) -> None:
        """Without one, an agent inherits whatever the host offers."""
        for path in agent_files(repo_root):
            document, _ = parse_document(path)
            assert document is not None
            tools = document.frontmatter.get("tools")
            assert isinstance(tools, list) and tools, f"{path.name} has no tools list"

    def test_no_agent_declares_an_unknown_tool(self, repo_root: Path) -> None:
        for path in agent_files(repo_root):
            document, _ = parse_document(path)
            assert document is not None
            declared = {str(tool) for tool in document.frontmatter["tools"]}
            assert declared <= KNOWN_TOOLS, f"{path.name}: unknown {sorted(declared - KNOWN_TOOLS)}"

    def test_non_editing_agents_hold_no_mutating_tool(self, repo_root: Path) -> None:
        for name in sorted(NON_EDITING_AGENTS):
            document, _ = parse_document(agents_root(repo_root) / f"{name}.agent.md")
            assert document is not None
            declared = {str(tool) for tool in document.frontmatter["tools"]}
            assert not (declared & MUTATING_TOOLS), (
                f"{name} is documented as non-editing but declares "
                f"{sorted(declared & MUTATING_TOOLS)}"
            )

    def test_only_the_orchestrator_may_delegate(self, repo_root: Path) -> None:
        """Otherwise the handoff graph stops being traceable."""
        for path in agent_files(repo_root):
            name = path.name.removesuffix(".agent.md")
            document, _ = parse_document(path)
            assert document is not None
            declared = {str(tool) for tool in document.frontmatter["tools"]}
            if "delegate" in declared:
                assert name in DELEGATION_ALLOWED, f"{name} must not delegate"

    def test_only_one_agent_can_edit_implementation_code(self, repo_root: Path) -> None:
        editors: list[str] = []
        for path in agent_files(repo_root):
            document, _ = parse_document(path)
            assert document is not None
            declared = {str(tool) for tool in document.frontmatter["tools"]}
            if "edit" in declared:
                editors.append(path.name.removesuffix(".agent.md"))
        assert editors == ["implementation-engineer"], (
            f"Unexpected agents hold the edit tool: {editors}"
        )


class TestApprovalBoundary:
    def test_no_agent_permits_self_approval(self, repo_root: Path) -> None:
        for path in agent_files(repo_root):
            findings = validate_agent(path)
            assert not any(f.rule == "AGENT-SELF-APPROVAL" for f in findings.errors)

    def test_every_agent_names_what_needs_human_approval(self, repo_root: Path) -> None:
        for path in agent_files(repo_root):
            document, _ = parse_document(path)
            assert document is not None
            section = document.sections()["Decisions requiring human approval"]
            assert "approv" in section.lower()
            assert len(section) > 100, f"{path.name}: approval section is a placeholder"

    def test_the_reviewer_cannot_approve(self, repo_root: Path) -> None:
        """It may declare a plan ready for approval. That is a different authority."""
        body = (agents_root(repo_root) / "governance-reviewer.agent.md").read_text(encoding="utf-8")
        assert "never approves" in body.lower()
        assert "ready for human approval" in body.lower()


class TestAgentStructure:
    def test_every_agent_has_all_required_sections(self, repo_root: Path) -> None:
        for path in agent_files(repo_root):
            document, _ = parse_document(path)
            assert document is not None
            missing = set(REQUIRED_SECTIONS) - set(document.sections())
            assert not missing, f"{path.name} missing: {sorted(missing)}"

    def test_every_agent_declares_a_handoff(self, repo_root: Path) -> None:
        """Artifact-based handoff is what makes the workflow reviewable after the fact."""
        for path in agent_files(repo_root):
            document, _ = parse_document(path)
            assert document is not None
            handoff = document.sections()["Handoff"]
            assert len(handoff) > 80, f"{path.name}: handoff section is a placeholder"

    def test_every_agent_declares_a_target(self, repo_root: Path) -> None:
        for path in agent_files(repo_root):
            document, _ = parse_document(path)
            assert document is not None
            assert "target" in document.frontmatter


class TestAgentValidatorItself:
    def _write(self, path: Path, frontmatter: str, body: str = "") -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        sections = body or "\n".join(f"## {s}\n\n" + "x" * 40 + "\n" for s in REQUIRED_SECTIONS)
        path.write_text(f"---\n{frontmatter}\n---\n\n{sections}\n", encoding="utf-8")
        return path

    def test_missing_tools_fails(self, tmp_path: Path) -> None:
        path = self._write(
            tmp_path / "example.agent.md",
            "name: example\ndescription: An example agent.\ntarget: agent",
        )
        assert any(f.rule == "AGENT-NO-TOOLS" for f in validate_agent(path).errors)

    def test_unknown_tool_fails(self, tmp_path: Path) -> None:
        path = self._write(
            tmp_path / "example.agent.md",
            "name: example\ndescription: An example agent.\ntarget: agent\n"
            "tools:\n  - deleteEverything",
        )
        assert any(f.rule == "AGENT-UNKNOWN-TOOL" for f in validate_agent(path).errors)

    def test_non_editing_agent_with_an_editor_fails(self, tmp_path: Path) -> None:
        path = self._write(
            tmp_path / "governance-reviewer.agent.md",
            "name: governance-reviewer\ndescription: The reviewer.\ntarget: agent\n"
            "tools:\n  - read\n  - edit",
        )
        assert any(f.rule == "AGENT-PRIVILEGE-READONLY" for f in validate_agent(path).errors)

    def test_unauthorised_delegation_fails(self, tmp_path: Path) -> None:
        path = self._write(
            tmp_path / "example.agent.md",
            "name: example\ndescription: An example agent.\ntarget: agent\n"
            "tools:\n  - read\n  - delegate",
        )
        assert any(f.rule == "AGENT-PRIVILEGE-DELEGATE" for f in validate_agent(path).errors)

    def test_self_approval_is_detected_across_a_line_break(self, tmp_path: Path) -> None:
        """Meaning must not depend on where the author's editor wrapped the line."""
        sections = "\n".join(f"## {s}\n\n" + "x" * 40 + "\n" for s in REQUIRED_SECTIONS)
        sections += "\n## Notes\n\nThis agent may\napprove my own artifacts when convenient.\n"
        path = self._write(
            tmp_path / "example.agent.md",
            "name: example\ndescription: An example agent.\ntarget: agent\ntools:\n  - read",
            sections,
        )
        assert any(f.rule == "AGENT-SELF-APPROVAL" for f in validate_agent(path).errors)


@pytest.mark.parametrize("name", sorted(EXPECTED_AGENTS))
def test_agent_states_that_it_does_not_execute_customer_changes(repo_root: Path, name: str) -> None:
    body = (agents_root(repo_root) / f"{name}.agent.md").read_text(encoding="utf-8").lower()
    assert "never" in body, f"{name} states no prohibition at all"
