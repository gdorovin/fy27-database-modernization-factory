"""Turn a directory of exports into one normalized evidence bundle.

The interesting work is conflict detection. Two tools that disagree about a version or a
size are common, and the wrong response is to take the newer or the more precise one. The
bundle records the disagreement and refuses to progress until a human resolves it.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from dbmodernize.adapters.base import AdapterRegistry, default_registry
from dbmodernize.errors import InputNotFoundError, UsageError
from dbmodernize.models.evidence import (
    EvidenceBundle,
    EvidenceConflict,
    EvidenceRecord,
)
from dbmodernize.utils.hashing import stable_id
from dbmodernize.utils.logging import get_logger
from dbmodernize.utils.safe_paths import resolve_within

LOG = get_logger("evidence")

#: Attributes where a disagreement changes a decision. Differences elsewhere are noise.
DECISION_CRITICAL_ATTRIBUTES: frozenset[str] = frozenset(
    {
        "source_platform",
        "source_version",
        "edition",
        "environment",
        "support_status",
        "data_size_gb",
        "criticality",
        "data_residency",
    }
)

#: Relative tolerance for numeric attributes before a difference counts as a conflict.
NUMERIC_TOLERANCE = 0.05

_SKIP_NAMES = frozenset({".gitkeep", ".keep", "README.md"})


def normalize_directory(
    input_dir: Path,
    engagement_id: str,
    collected_on: date,
    registry: AdapterRegistry | None = None,
    adapter_name: str | None = None,
    generator: str = "dbmodernize normalize-evidence",
) -> EvidenceBundle:
    """Read every supported file under ``input_dir`` and emit one bundle."""
    if not input_dir.is_dir():
        raise InputNotFoundError(f"Input directory not found: {input_dir}")

    registry = registry or default_registry()
    records: list[EvidenceRecord] = []
    read_any = False

    for path in sorted(input_dir.rglob("*")):
        if not path.is_file() or path.name in _SKIP_NAMES:
            continue
        # Containment check: refuse anything a symlink dragged in from outside the root.
        resolve_within(input_dir, path.relative_to(input_dir))

        adapter = registry.by_name(adapter_name) if adapter_name else registry.for_path(path)
        if adapter is None or not adapter.supports(path):
            LOG.debug("No adapter for %s; skipping", path.name)
            continue
        read_any = True
        records.extend(adapter.extract(path, engagement_id, collected_on))

    if not read_any:
        raise UsageError(
            f"No supported evidence files found under {input_dir}. "
            f"Available adapters: {', '.join(registry.names)}"
        )

    records.sort(key=lambda record: (record.subject_id, record.source.value, record.id))
    conflicts = detect_conflicts(records)

    return EvidenceBundle(
        engagement_id=engagement_id,
        # Not the wall clock: reproducibility beats knowing the exact minute of a run.
        generated_at=datetime.combine(collected_on, datetime.min.time(), tzinfo=UTC),
        generator=generator,
        records=records,
        conflicts=conflicts,
    )


def detect_conflicts(records: list[EvidenceRecord]) -> list[EvidenceConflict]:
    """Find decision-critical attributes where sources disagree."""
    grouped: dict[tuple[str, str], list[tuple[str, Any]]] = defaultdict(list)
    for record in records:
        if record.superseded_by:
            continue
        for key, value in record.attributes.items():
            if key in DECISION_CRITICAL_ATTRIBUTES and value not in (None, "", []):
                grouped[(record.subject_id, key)].append((record.id, value))

    conflicts: list[EvidenceConflict] = []
    for (subject_id, attribute), entries in sorted(grouped.items()):
        if len({_normalise(value) for _, value in entries}) <= 1:
            continue
        if _within_tolerance([value for _, value in entries]):
            continue
        conflicts.append(
            EvidenceConflict(
                id=stable_id("conflict", subject_id, attribute),
                subject_id=subject_id,
                attribute=attribute,
                values=sorted({str(value) for _, value in entries}),
                evidence_refs=sorted({record_id for record_id, _ in entries}),
                resolution_owner_role="database-owner",
                resolved=False,
            )
        )
    return conflicts


def _normalise(value: Any) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, str):
        return value.strip().lower()
    return str(value)


def _within_tolerance(values: list[Any]) -> bool:
    """Numeric spread below the tolerance is measurement noise, not a disagreement."""
    numbers: list[float] = []
    for value in values:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return False
        numbers.append(float(value))
    if not numbers:
        return False
    low, high = min(numbers), max(numbers)
    if high == 0:
        return True
    return (high - low) / abs(high) <= NUMERIC_TOLERANCE


def merged_attributes(bundle: EvidenceBundle, subject_id: str) -> dict[str, Any]:
    """Merge a subject's records, preferring observed evidence over user-provided.

    Conflicting attributes are deliberately omitted: a merged view that silently picks a
    winner would hide the disagreement the bundle exists to surface.
    """
    conflicted = {
        c.attribute for c in bundle.conflicts if c.subject_id == subject_id and not c.resolved
    }
    ranked = sorted(
        bundle.by_subject(subject_id),
        key=lambda record: _precedence(record),
    )
    merged: dict[str, Any] = {}
    for record in ranked:
        for key, value in record.attributes.items():
            if key in conflicted or value in (None, "", []):
                continue
            merged.setdefault(key, value)
    return merged


_CLASS_RANK = {"observed": 0, "derived": 1, "user-provided": 2, "assumption": 3}
_CONFIDENCE_RANK = {"high": 0, "medium": 1, "low": 2}


def _precedence(record: EvidenceRecord) -> tuple[int, int, str]:
    return (
        _CLASS_RANK.get(record.evidence_class.value, 9),
        _CONFIDENCE_RANK.get(record.confidence.value, 9),
        record.id,
    )


def evidence_ids_for(bundle: EvidenceBundle, subject_id: str) -> list[str]:
    return sorted(record.id for record in bundle.by_subject(subject_id))


__all__ = [
    "DECISION_CRITICAL_ATTRIBUTES",
    "NUMERIC_TOLERANCE",
    "detect_conflicts",
    "evidence_ids_for",
    "merged_attributes",
    "normalize_directory",
]
