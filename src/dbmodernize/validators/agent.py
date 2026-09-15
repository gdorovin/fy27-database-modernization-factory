"""Structural and least-privilege validation of agent definitions.

The important check here is not shape, it is privilege. An agent whose documented role is
read-only but whose tool list includes an editor will eventually edit something, and the
governance story collapses the first time it does.
"""

from __future__ import annotations

import re
from pathlib import Path

from dbmodernize.errors import FindingSet
from dbmodernize.validators.frontmatter import parse_document, require_sections

REQUIRED_SECTIONS: tuple[str, ...] = (
    "Objective",
    "Inputs",
    "Outputs",
    "Decisions I may make",
    "Decisions requiring human approval",
    "Failure and escalation",
    "Handoff",
    "Constraints",
)

#: Tools an agent may declare. Anything outside this set is rejected rather than assumed.
KNOWN_TOOLS = frozenset(
    {
        "search",
        "read",
        "list",
        "fetch",
        "edit",
        "create",
        "runCommands",
        "runTests",
        "delegate",
        "githubIssues",
    }
)

#: Tools that can change repository state.
MUTATING_TOOLS = frozenset({"edit", "create"})

#: Tools that can run arbitrary processes.
EXECUTING_TOOLS = frozenset({"runCommands", "runTests"})

#: Agents that must never hold a mutating tool. Mirrors docs/governance/decision-rights.md.
#:
#: Note the name: these agents may still *run* the CLI, because the CLI cannot mutate a
#: customer environment and writes only to the output directory the caller names. The
#: control that matters is that they cannot edit repository artifacts, which is what this
#: set enforces.
NON_EDITING_AGENTS = frozenset(
    {"governance-reviewer", "estate-assessor", "value-advisor", "engagement-orchestrator"}
)

#: Only the orchestrator routes between specialists.
DELEGATION_ALLOWED = frozenset({"engagement-orchestrator"})

_NAME_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

_SELF_APPROVAL = re.compile(r"(?i)\b(approve (?:my|its) own|self[- ]approv)")


def validate_agent(path: Path) -> FindingSet:
    findings = FindingSet()
    document, parse_findings = parse_document(path)
    findings.extend(parse_findings)
    if document is None:
        return findings

    stem = path.name.removesuffix(".agent.md")
    name = str(document.frontmatter.get("name", "")).strip()
    description = str(document.frontmatter.get("description", "")).strip()
    tools = document.frontmatter.get("tools")

    if not name:
        findings.add(rule="AGENT-NO-NAME", message="Frontmatter has no 'name'", path=str(path))
    else:
        if not _NAME_PATTERN.match(name):
            findings.add(
                rule="AGENT-NAME-FORMAT",
                message=f"Name {name!r} must be lowercase and hyphen-separated",
                path=str(path),
            )
        if name != stem:
            findings.add(
                rule="AGENT-NAME-MISMATCH",
                message=f"Frontmatter name {name!r} does not match file stem {stem!r}",
                path=str(path),
            )

    if not description:
        findings.add(
            rule="AGENT-NO-DESCRIPTION",
            message="Frontmatter has no 'description'",
            path=str(path),
        )

    findings.extend(_check_tools(name or stem, tools, path))

    if "target" not in document.frontmatter:
        findings.add(
            rule="AGENT-NO-TARGET",
            message="Frontmatter has no 'target'; the execution surface is undefined",
            path=str(path),
        )

    findings.extend(require_sections(document, REQUIRED_SECTIONS, "AGENT"))
    findings.extend(_check_approval_boundary(document.body, name or stem, path))
    return findings


def _check_tools(name: str, tools: object, path: Path) -> FindingSet:
    findings = FindingSet()
    if not isinstance(tools, list) or not tools:
        findings.add(
            rule="AGENT-NO-TOOLS",
            message=(
                "Frontmatter has no non-empty 'tools' list. An agent without an explicit "
                "allowlist inherits whatever the host offers, which is the opposite of "
                "least privilege."
            ),
            path=str(path),
        )
        return findings

    declared = {str(tool).strip() for tool in tools}
    unknown = sorted(declared - KNOWN_TOOLS)
    if unknown:
        findings.add(
            rule="AGENT-UNKNOWN-TOOL",
            message=(
                f"Unknown tools declared: {', '.join(unknown)}. Add them to KNOWN_TOOLS "
                "deliberately, with a note on why the privilege is needed."
            ),
            path=str(path),
        )

    if name in NON_EDITING_AGENTS:
        violating = sorted(declared & MUTATING_TOOLS)
        if violating:
            findings.add(
                rule="AGENT-PRIVILEGE-READONLY",
                message=(
                    f"{name} is documented as non-editing but declares "
                    f"{', '.join(violating)}. Remove the tool or change the documented "
                    "role; the two must agree."
                ),
                path=str(path),
            )

    if "delegate" in declared and name not in DELEGATION_ALLOWED:
        findings.add(
            rule="AGENT-PRIVILEGE-DELEGATE",
            message=(
                f"{name} declares 'delegate'. Only "
                f"{', '.join(sorted(DELEGATION_ALLOWED))} may route between specialists; "
                "otherwise the handoff graph becomes untraceable."
            ),
            path=str(path),
        )
    return findings


def _check_approval_boundary(body: str, name: str, path: Path) -> FindingSet:
    findings = FindingSet()
    section_header = "## Decisions requiring human approval"
    if section_header in body:
        start = body.index(section_header)
        segment = body[start : start + 2000]
        if not re.search(r"(?i)\bapprov", segment):
            findings.add(
                rule="AGENT-APPROVAL-VAGUE",
                message="'Decisions requiring human approval' does not name an approval",
                path=str(path),
                severity="warning",
            )

    # Collapse whitespace first: a sentence's meaning must not depend on where the author's
    # editor happened to wrap the line. Word boundaries matter here too -- without them,
    # a heading such as "Notes" satisfies the negation and the check silently passes.
    flat = re.sub(r"\s+", " ", body)
    if _SELF_APPROVAL.search(flat) and not re.search(
        r"(?i)\b(never|not|cannot|must not)\b[^.]{0,60}(approve (?:my|its) own|self[- ]approv)",
        flat,
    ):
        findings.add(
            rule="AGENT-SELF-APPROVAL",
            message=f"{name} appears to permit self-approval",
            path=str(path),
        )
    return findings


def validate_agents_tree(agents_root: Path) -> FindingSet:
    findings = FindingSet()
    if not agents_root.is_dir():
        findings.add(
            rule="AGENT-ROOT-MISSING",
            message=f"Agents directory not found: {agents_root}",
            path=str(agents_root),
        )
        return findings

    files = sorted(agents_root.glob("*.agent.md"))
    if not files:
        findings.add(
            rule="AGENT-ROOT-EMPTY",
            message=f"No agent definitions found under {agents_root}",
            path=str(agents_root),
        )
    for file in files:
        findings.extend(validate_agent(file))
    return findings


__all__ = [
    "DELEGATION_ALLOWED",
    "EXECUTING_TOOLS",
    "KNOWN_TOOLS",
    "MUTATING_TOOLS",
    "NON_EDITING_AGENTS",
    "REQUIRED_SECTIONS",
    "validate_agent",
    "validate_agents_tree",
]
