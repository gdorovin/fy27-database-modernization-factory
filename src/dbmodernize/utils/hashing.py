"""Stable hashing and identifier derivation.

Artifacts reference each other by ID and are approved against a content hash. Both must
be reproducible across machines and Python runs, so nothing here uses ``hash()`` or
insertion order.
"""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any

_SLUG_STRIP = re.compile(r"[^a-z0-9]+")


def canonical_json(data: Any) -> str:
    """Serialize to the canonical form used for hashing and for on-disk artifacts."""
    return json.dumps(
        data,
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
        default=str,
    )


def content_hash(data: Any) -> str:
    """Return a ``sha256:<hex>`` digest of the canonical serialization.

    Approval artifacts store this so that editing an approved artifact invalidates the
    approval instead of silently inheriting it.
    """
    payload = canonical_json(data).encode("utf-8")
    return f"sha256:{hashlib.sha256(payload).hexdigest()}"


def slugify(value: str) -> str:
    """Lowercase, hyphen-separated slug. Empty input yields ``unknown``."""
    slug = _SLUG_STRIP.sub("-", value.strip().lower()).strip("-")
    return slug or "unknown"


def stable_id(prefix: str, *parts: str) -> str:
    """Derive a deterministic, readable identifier.

    The short digest disambiguates names that slugify identically, without depending on
    iteration order or a random seed.
    """
    joined = "|".join(parts)
    digest = hashlib.sha256(joined.encode("utf-8")).hexdigest()[:8]
    return f"{prefix}-{slugify(joined)[:40]}-{digest}".strip("-")
