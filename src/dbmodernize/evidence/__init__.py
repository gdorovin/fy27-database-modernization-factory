"""Evidence ingestion and normalization.

``evidence.normalize`` is deliberately **not** re-exported here. It depends on the adapter
registry, and the adapters depend on ``evidence.injection``, so re-exporting it would create
an import cycle. Import it directly:
``from dbmodernize.evidence.normalize import normalize_directory``.
"""

from __future__ import annotations

from dbmodernize.evidence.injection import PATTERNS, scan_mapping, scan_text

__all__ = ["PATTERNS", "scan_mapping", "scan_text"]
