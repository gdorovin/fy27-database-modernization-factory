"""Logging with redaction applied at the handler boundary.

A caller cannot forget to redact: the filter runs on every record regardless of how the
message was built.
"""

from __future__ import annotations

import logging
import sys

from dbmodernize.utils.redaction import redact

_CONFIGURED = False


class RedactingFilter(logging.Filter):
    """Mask secret-like values in the message and in string arguments."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {
                    key: redact(value) if isinstance(value, str) else value
                    for key, value in record.args.items()
                }
            elif isinstance(record.args, tuple):
                record.args = tuple(
                    redact(value) if isinstance(value, str) else value for value in record.args
                )
        return True


def configure(verbose: bool = False) -> None:
    """Install the redacting handler once. Safe to call repeatedly."""
    global _CONFIGURED  # noqa: PLW0603
    if _CONFIGURED:
        logging.getLogger("dbmodernize").setLevel(logging.DEBUG if verbose else logging.INFO)
        return

    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
    handler.addFilter(RedactingFilter())

    root = logging.getLogger("dbmodernize")
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.DEBUG if verbose else logging.INFO)
    root.propagate = False
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    configure()
    return logging.getLogger(f"dbmodernize.{name}")
