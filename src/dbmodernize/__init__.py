"""FY27 Database Modernization Factory.

A deterministic, offline-first toolkit that turns database estate evidence into
auditable modernization decisions, plans, and GitHub issues.

The package never mutates a customer environment. Every public entry point is
read-only or writes to a local output directory that the caller names.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "0.1.0"

#: Bumped independently of the package version. Artifacts record it so a consumer can
#: tell whether a stored artifact predates a contract change.
SCHEMA_VERSION = "1.0.0"
