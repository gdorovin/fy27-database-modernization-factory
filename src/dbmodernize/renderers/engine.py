"""Jinja2 environment for document rendering.

Rendering is pure: the same artifact renders to the same bytes on any machine. That means
no wall-clock timestamps, no dictionary iteration order, and no locale-dependent
formatting. Undefined variables raise rather than silently rendering as empty, because a
blank section in a migration plan is worse than a crash.
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined

from dbmodernize.errors import InputNotFoundError

TEMPLATE_DIR_NAME = "templates"


def templates_dir(repo_root: Path) -> Path:
    path = repo_root / TEMPLATE_DIR_NAME
    if not path.is_dir():
        raise InputNotFoundError(f"Templates directory not found at {path}")
    return path


@functools.lru_cache(maxsize=4)
def environment(repo_root: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(templates_dir(repo_root)), encoding="utf-8"),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
        autoescape=False,  # noqa: S701 - Markdown output, never HTML in a browser context
    )
    env.filters["bullets"] = _bullets
    env.filters["yes_no"] = _yes_no
    env.filters["titlecase"] = _titlecase
    env.filters["sentence"] = _sentence
    env.filters["percent"] = _percent
    return env


def render(repo_root: Path, template_name: str, context: dict[str, Any]) -> str:
    """Render a template. Missing context keys raise instead of producing a gap."""
    return environment(repo_root).get_template(template_name).render(**context)


def _bullets(items: list[Any], indent: int = 0, empty: str = "_None recorded._") -> str:
    if not items:
        return " " * indent + empty
    prefix = " " * indent + "- "
    return "\n".join(f"{prefix}{item}" for item in items)


def _yes_no(value: object) -> str:
    return "Yes" if value else "No"


def _titlecase(value: str) -> str:
    return value.replace("-", " ").replace("_", " ").strip().capitalize()


def _sentence(value: str) -> str:
    """Ensure a fragment reads as a sentence, so generated prose is not a list of stubs."""
    text = str(value).strip()
    if not text:
        return text
    if text[-1] not in ".!?":
        text += "."
    return text[0].upper() + text[1:]


def _percent(value: float | int | None, digits: int = 0) -> str:
    if value is None:
        return "unknown"
    return f"{value:.{digits}f}%"


__all__ = ["TEMPLATE_DIR_NAME", "environment", "render", "templates_dir"]
