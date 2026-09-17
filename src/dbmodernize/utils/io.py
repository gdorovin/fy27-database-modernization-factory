"""Deterministic, UTF-8, LF-normalised file I/O with overwrite protection.

Windows defaults to cp1252 and CRLF. Both would make generated artifacts differ between
contributors and break snapshot comparison, so every read and write in this repository
goes through here.
"""

from __future__ import annotations

import csv
import io
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
    try:
        return path.read_text(encoding=ENCODING)
    except UnicodeDecodeError as exc:
        raise UsageError(
            f"{path} is not valid UTF-8 (byte {exc.start}). Re-export the file as UTF-8; "
            "a Windows-1252 spreadsheet export is the usual cause."
        ) from exc


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


#: Key under which cells beyond the header width are kept. A ragged row is a fact about
#: the export that the adapter reports; it is never trimmed to fit.
CSV_OVERFLOW_KEY = "__overflow__"


def read_csv_rows(path: Path, *, max_rows: int = 100_000) -> list[dict[str, str]]:
    """Read a CSV into row dictionaries with a row cap.

    Header names are stripped; values keep their content but have surrounding whitespace
    removed so that ``"SQL Server 2016 "`` and ``"SQL Server 2016"`` normalise alike.

    The text is parsed as one stream rather than line by line, so a quoted cell containing
    a newline survives intact instead of being glued to its neighbour. Cells past the header
    width are kept under :data:`CSV_OVERFLOW_KEY` so the adapter can report them.
    """
    text = read_text(path)
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""), restkey=CSV_OVERFLOW_KEY)
        if reader.fieldnames is None:
            raise UsageError(f"{path}: CSV has no header row")
        rows: list[dict[str, str]] = []
        for index, raw in enumerate(reader):
            if index >= max_rows:
                raise UsageError(f"{path}: more than {max_rows} rows; split the export")
            row: dict[str, str] = {}
            for key, value in raw.items():
                if key == CSV_OVERFLOW_KEY:
                    extra = [str(v).strip() for v in (value or [])]
                    if any(extra):
                        row[CSV_OVERFLOW_KEY] = ";".join(extra)
                    continue
                row[(key or "").strip()] = ("" if value is None else str(value)).strip()
            rows.append(row)
    except csv.Error as exc:
        raise UsageError(f"{path}: malformed CSV: {exc}") from exc
    return rows


def _guard_overwrite(path: Path, force: bool) -> None:
    if path.exists() and not force:
        raise OutputExistsError(
            f"{path} already exists. Re-run with --force to overwrite, "
            f"or choose a different --out directory."
        )


def write_text(path: Path, content: str, *, force: bool = False, dry_run: bool = False) -> Path:
    """Write text with LF endings. Adds a trailing newline if missing.

    A dry run writes nothing, so it also overwrites nothing: the overwrite guard applies
    only to a real write. Refusing a preview because the previous preview exists would
    make ``--dry-run`` unusable on exactly the second run where it is most wanted.
    """
    if not content.endswith("\n"):
        content += "\n"
    if dry_run:
        return path
    _guard_overwrite(path, force)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding=ENCODING, newline="\n") as handle:
        handle.write(content)
    return path


def write_json(path: Path, data: Any, *, force: bool = False, dry_run: bool = False) -> Path:
    """Write pretty, key-sorted JSON so that diffs are reviewable.

    No ``default=`` fallback: a value that is not JSON-serialisable is a bug in the caller,
    and stringifying it silently would turn that bug into a quiet content change inside a
    snapshot rather than a failure someone sees.
    """
    payload = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False)
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
