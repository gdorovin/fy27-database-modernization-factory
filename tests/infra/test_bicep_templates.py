"""Assertions about the Bicep templates as files. Nothing here contacts Azure.

These exist because `infra/tests/README.md` listed three security properties as enforced
by "Review". A control that depends on someone remembering to look is not a control, and
all three are checkable from the text of the templates.

Deliberately narrow: these tests read what the templates say, they do not model what Azure
would do with them. A property that can only be confirmed against a live API version is
better left to `bicep build` and a what-if review than approximated here.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

BICEP_DIR = "infra/bicep"

#: Credential-shaped parameters. Their absence is what makes the Entra-only claim in
#: `sql-managed-instance.bicep` verifiable rather than aspirational.
_CREDENTIAL_PARAM = re.compile(
    r"^\s*param\s+\w*(password|administratorLogin|adminUser|secret)\w*\s",
    re.IGNORECASE | re.MULTILINE,
)

#: Any `minimalTlsVersion`/`minimumTlsVersion` assignment, so a downgrade is visible.
_TLS_ASSIGNMENT = re.compile(r"min(?:imal|imum)TlsVersion:\s*'([\d.]+)'")

#: A literal GUID. Real subscription and tenant ids look like this; so do a few harmless
#: things, which is why the secret scanner owns the final say and this is a second net.
_GUID = re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I)

#: Modules that create something reachable over a network must decide, in the template,
#: whether it is publicly reachable. Silence is the dangerous answer.
_PUBLIC_ACCESS_DECISION = ("publicNetworkAccess:", "publicDataEndpointEnabled:")

DATA_PLANE_MODULES = (
    "sql-database.bicep",
    "sql-managed-instance.bicep",
    "postgresql-flexible.bicep",
)


@pytest.fixture(scope="module")
def bicep_files(repo_root: Path) -> list[Path]:
    files = sorted((repo_root / BICEP_DIR).rglob("*.bicep"))
    assert files, "no Bicep templates found"
    return files


@pytest.fixture(scope="module")
def main_bicep(repo_root: Path) -> str:
    return (repo_root / BICEP_DIR / "main.bicep").read_text(encoding="utf-8")


def test_no_template_declares_a_credential_parameter(bicep_files: list[Path]) -> None:
    """Entra-only is a design claim. A password parameter would quietly retract it."""
    offenders = [
        path.name for path in bicep_files if _CREDENTIAL_PARAM.search(path.read_text("utf-8"))
    ]
    assert not offenders, f"credential-shaped parameter in: {', '.join(offenders)}"


@pytest.mark.parametrize("module", DATA_PLANE_MODULES)
def test_data_plane_modules_decide_public_reachability(repo_root: Path, module: str) -> None:
    text = (repo_root / BICEP_DIR / "modules" / module).read_text(encoding="utf-8")
    assert any(marker in text for marker in _PUBLIC_ACCESS_DECISION), (
        f"{module} creates a network-reachable resource without stating whether it is "
        "publicly reachable. Inheriting that from an Azure default makes the security "
        "posture depend on a default nobody in this repository controls."
    )


@pytest.mark.parametrize("module", DATA_PLANE_MODULES)
def test_public_reachability_defaults_to_closed(repo_root: Path, module: str) -> None:
    text = (repo_root / BICEP_DIR / "modules" / module).read_text(encoding="utf-8")
    assert "publicNetworkAccess: 'Enabled'" not in text
    assert "publicDataEndpointEnabled: true" not in text


def test_no_template_downgrades_tls(bicep_files: list[Path]) -> None:
    for path in bicep_files:
        for version in _TLS_ASSIGNMENT.findall(path.read_text(encoding="utf-8")):
            assert float(version) >= 1.2, f"{path.name} sets TLS {version}"


def test_no_template_carries_a_real_identifier(bicep_files: list[Path]) -> None:
    offenders = [path.name for path in bicep_files if _GUID.search(path.read_text("utf-8"))]
    assert not offenders, f"GUID literal in: {', '.join(offenders)}"


def test_region_has_no_default(main_bicep: str) -> None:
    """A defaulted region deploys somewhere nobody chose, which is a sovereignty problem."""
    declaration = next(
        line for line in main_bicep.splitlines() if line.strip().startswith("param location ")
    )
    assert "=" not in declaration, f"location carries a default: {declaration.strip()}"


def test_main_composes_and_holds_no_resources_itself(main_bicep: str) -> None:
    """Stated as a rule in infra/tests/README.md; worth more as a test than as prose."""
    declarations = [
        line for line in main_bicep.splitlines() if line.strip().startswith("resource ")
    ]
    assert not declarations, f"main.bicep declares resources: {declarations}"


def test_every_module_is_reachable_from_main(repo_root: Path, main_bicep: str) -> None:
    """An orphaned module is untested, unreviewed, and still looks like guidance."""
    modules_dir = repo_root / BICEP_DIR / "modules"
    referenced = set(re.findall(r"'(?:modules/)?([\w-]+\.bicep)'", main_bicep))
    for module in sorted(modules_dir.glob("*.bicep")):
        transitive = any(
            module.name in sibling.read_text(encoding="utf-8")
            for sibling in modules_dir.glob("*.bicep")
            if sibling != module
        )
        assert module.name in referenced or transitive, (
            f"{module.name} is referenced by nothing. Delete it or compose it."
        )
