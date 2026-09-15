"""Map a workload and its chosen target onto a modernization disposition."""

from __future__ import annotations

from dbmodernize.models.base import AzureTarget, Disposition, SourcePlatform
from dbmodernize.models.workload import Workload
from dbmodernize.scoring.reference import HETEROGENEOUS_PAIRS, OS_LEVEL_FEATURES

#: Same-family moves onto infrastructure keep the engine and the operating model.
_REHOST_TARGETS = frozenset({AzureTarget.SQL_ON_AZURE_VM})

#: Targets that do not move the data at all.
_IN_PLACE_TARGETS = frozenset({AzureTarget.ARC_ENABLED_SQL, AzureTarget.RETAIN})


def classify(workload: Workload, target: AzureTarget) -> Disposition:
    """Return the disposition implied by moving ``workload`` to ``target``.

    Arc enablement classifies as ``retain``. It is governance and inventory over a system
    that has not moved, and calling it anything else would let an estate report progress
    it has not made.
    """
    if target is AzureTarget.RETIRE:
        return Disposition.RETIRE
    if target is AzureTarget.REPLACE_SAAS:
        return Disposition.REPLACE
    if target in _IN_PLACE_TARGETS:
        return Disposition.RETAIN

    if (workload.source_platform, target) in HETEROGENEOUS_PAIRS:
        # Crossing engine families means rewriting code, not relocating it.
        return Disposition.REFACTOR

    if target in _REHOST_TARGETS:
        return Disposition.REHOST

    if requires_application_change(workload, target):
        return Disposition.REFACTOR

    return Disposition.REPLATFORM


def requires_application_change(workload: Workload, target: AzureTarget) -> bool:
    """True when the application cannot reach the target unmodified."""
    if (workload.source_platform, target) in HETEROGENEOUS_PAIRS:
        return True
    if target in {AzureTarget.SQL_DATABASE, AzureTarget.SQL_DATABASE_HYPERSCALE}:
        from dbmodernize.scoring.reference import INSTANCE_SCOPED_FEATURES

        return bool(set(workload.instance_features) & INSTANCE_SCOPED_FEATURES)
    return False


def requires_conversion(workload: Workload, target: AzureTarget) -> bool:
    return (workload.source_platform, target) in HETEROGENEOUS_PAIRS


def blocks_platform_as_a_service(workload: Workload) -> list[str]:
    """Operating-system dependencies that rule out every managed target."""
    return sorted(set(workload.instance_features) & OS_LEVEL_FEATURES)


def is_open_source_relational(platform: SourcePlatform) -> bool:
    return platform in {SourcePlatform.POSTGRESQL, SourcePlatform.MYSQL, SourcePlatform.MARIADB}


__all__ = [
    "blocks_platform_as_a_service",
    "classify",
    "is_open_source_relational",
    "requires_application_change",
    "requires_conversion",
]
