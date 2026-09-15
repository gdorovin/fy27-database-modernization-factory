"""Deterministic, UTF-8, LF-normalised file I/O with overwrite protection.

Windows defaults to cp1252 and CRLF. Both would make generated artifacts differ between
contributors and break snapshot comparison, so every read and write in this repository
goes through here.
"""

from __future__ import annotations

import csv
import json
from collections.abc import Iterator, Sequence
from pathlib import Path
from typing import Any

import yaml

from dbmodernize.errors import InputNotFoundError, OutputExistsError, UsageError

ENCODING = "utf-8"

#: Refuse to parse an imported text file larger than this without an explicit override.
MAX_IMPORT_BYTES = 32 * 1024 * 1024


def read_text(path: Path, *, max_bytes: int = MAX_IMPORT_BYTES) -> str:
    if not path.is_file():
        raise InputNotFoundError(f"File not found: {path}")
    size = path.stat().st_size
    if size > max_bytes:
        raise UsageError(f"File {path} is {size} bytes, above the {max_bytes} byte import limit")
    return path.read_text(encoding=ENCODING)


def read_json(path: Path) -> Any:
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise UsageError(f"{path}: invalid JSON at line {exc.lineno}: {exc.msg}") from exc


def read_yaml(path: Path) -> Any:
    try:
        # safe_load only. Never yaml.load: imported documents are untrusted.
        return yaml.safe_load(read_text(path))
    except yaml.YAMLError as exc:
        raise UsageError(f"{path}: invalid YAML: {exc}") from exc


def read_structured(path: Path) -> Any:
    """Read JSON or YAML based on the file suffix."""
    suffix = path.suffix.lower()
    if suffix == ".json":
        return read_json(path)
    if suffix in {".yaml", ".yml"}:
        return read_yaml(path)
    raise UsageError(f"Unsupported structured format for {path}; expected .json, .yaml, or .yml")


def read_csv_rows(path: Path, *, max_rows: int = 100_000) -> list[dict[str, str]]:
    """Read a CSV into row dictionaries with a row cap.

    Header names are stripped; values keep their content but have surrounding whitespace
    removed so that ``"SQL Server 2016 "`` and ``"SQL Server 2016"`` normalise alike.
    """
    text = read_text(path)
    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames is None:
        raise UsageError(f"{path}: CSV has no header row")
    rows: list[dict[str, str]] = []
    for index, raw in enumerate(reader):
        if index >= max_rows:
            raise UsageError(f"{path}: more than {max_rows} rows; split the export")
        rows.append(
            {
                (key or "").strip(): (value or "").strip()
                for key, value in raw.items()
                if key is not None
            }
        )
    return rows


def _guard_overwrite(path: Path, force: bool) -> None:
    if path.exists() and not force:
        raise OutputExistsError(
            f"{path} already exists. Re-run with --force to overwrite, "
            f"or choose a different --out directory."
        )


def write_text(path: Path, content: str, *, force: bool = False, dry_run: bool = False) -> Path:
    """Write text with LF endings. Adds a trailing newline if missing."""
    _guard_overwrite(path, force)
    if not content.endswith("\n"):
        content += "\n"
    if dry_run:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=ENCODING, newline="\n") as handle:
        handle.write(content)
    return path


def write_json(path: Path, data: Any, *, force: bool = False, dry_run: bool = False) -> Path:
    """Write pretty, key-sorted JSON so that diffs are reviewable."""
    payload = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False, default=str)
    return write_text(path, payload, force=force, dry_run=dry_run)


def write_yaml(path: Path, data: Any, *, force: bool = False, dry_run: bool = False) -> Path:
    payload = yaml.safe_dump(data, sort_keys=True, allow_unicode=True, default_flow_style=False)
    return write_text(path, payload, force=force, dry_run=dry_run)


def write_csv(
    path: Path,
    rows: Sequence[dict[str, Any]],
    fieldnames: Sequence[str],
    *,
    force: bool = False,
    dry_run: bool = False,
) -> Path:
    lines = [",".join(fieldnames)]
    for row in rows:
        lines.append(",".join(_csv_cell(row.get(name, "")) for name in fieldnames))
    return write_text(path, "\n".join(lines), force=force, dry_run=dry_run)


def _csv_cell(value: Any) -> str:
    text = "" if value is None else str(value)
    if any(ch in text for ch in (",", '"', "\n")):
        escaped = text.replace('"', '""')
        return f'"{escaped}"'
    return text


def iter_files(root: Path, pattern: str) -> Iterator[Path]:
    """Yield matching files in a stable, sorted order."""
    yield from sorted(p for p in root.rglob(pattern) if p.is_file())
