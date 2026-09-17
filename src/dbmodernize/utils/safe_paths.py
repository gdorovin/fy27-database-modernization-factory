"""Path containment and archive-extraction safety.

Adapters ingest third-party exports. Those exports are untrusted: a member name inside a
zip, or a path column inside a CSV, can try to escape the destination directory or
exhaust the disk. Everything that turns imported text into a filesystem path goes
through this module.
"""

from __future__ import annotations

import zipfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from dbmodernize.errors import PolicyViolationError, UsageError

#: Characters that never appear in a legitimate relative path from an export.
_FORBIDDEN_FRAGMENTS = ("\x00",)


@dataclass(frozen=True, slots=True)
class ArchiveLimits:
    """Bounds applied before any archive entry is written to disk.

    Defaults are deliberately small. A real assessment export that exceeds them should
    raise a conversation, not be silently expanded.
    """

    max_entries: int = 2_000
    max_entry_bytes: int = 64 * 1024 * 1024
    max_total_bytes: int = 512 * 1024 * 1024
    max_compression_ratio: int = 200


def resolve_within(root: Path, candidate: str | Path) -> Path:
    """Resolve ``candidate`` relative to ``root`` and refuse to leave ``root``.

    Absolute paths, parent traversal, symlink escapes, drive-letter tricks, and embedded
    NUL bytes are all rejected.
    """
    raw = str(candidate)
    for fragment in _FORBIDDEN_FRAGMENTS:
        if fragment in raw:
            raise PolicyViolationError(f"Path contains a forbidden character: {raw!r}")

    candidate_path = Path(raw)
    if candidate_path.is_absolute() or candidate_path.drive or raw.startswith(("/", "\\")):
        raise PolicyViolationError(f"Absolute paths are not accepted from imported data: {raw!r}")

    root_resolved = root.resolve()
    target = (root_resolved / candidate_path).resolve()

    if target != root_resolved and root_resolved not in target.parents:
        raise PolicyViolationError(
            f"Path escapes the allowed root. root={root_resolved} resolved={target}"
        )
    return target


#: Read size used while extracting, so memory use is bounded by this rather than by the
#: size an untrusted header claims.
_CHUNK_BYTES = 1024 * 1024


def safe_extract(
    archive: Path,
    destination: Path,
    limits: ArchiveLimits | None = None,
) -> list[Path]:
    """Extract a zip archive with containment and resource limits.

    Returns the list of written files. Raises :class:`PolicyViolationError` on the first
    violation, before writing anything for that entry.
    """
    limits = limits or ArchiveLimits()
    if not archive.is_file():
        raise UsageError(f"Archive not found: {archive}")

    destination.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    total = 0

    with zipfile.ZipFile(archive) as handle:
        members = handle.infolist()
        if len(members) > limits.max_entries:
            raise PolicyViolationError(
                f"Archive has {len(members)} entries, limit is {limits.max_entries}"
            )

        for member in members:
            name = member.filename
            if name.endswith("/"):
                continue
            if PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts:
                raise PolicyViolationError(f"Archive entry escapes the destination: {name!r}")

            if member.file_size > limits.max_entry_bytes:
                raise PolicyViolationError(
                    f"Archive entry {name!r} is {member.file_size} bytes, "
                    f"limit is {limits.max_entry_bytes}"
                )
            total += member.file_size
            if total > limits.max_total_bytes:
                raise PolicyViolationError(
                    f"Archive expands to more than {limits.max_total_bytes} bytes"
                )
            if member.compress_size > 0:
                ratio = member.file_size // max(member.compress_size, 1)
                if ratio > limits.max_compression_ratio:
                    raise PolicyViolationError(
                        f"Archive entry {name!r} has a compression ratio of {ratio}:1, "
                        f"limit is {limits.max_compression_ratio}:1"
                    )

            target = resolve_within(destination, name)
            target.parent.mkdir(parents=True, exist_ok=True)
            # The header sizes checked above are written by whoever built the archive. The
            # bytes are counted again as they are actually decompressed, so a header that
            # lies about its size is caught before the limit is exceeded, not after.
            extracted = 0
            with handle.open(member) as source, target.open("wb") as sink:
                while chunk := source.read(_CHUNK_BYTES):
                    extracted += len(chunk)
                    if extracted > limits.max_entry_bytes:
                        sink.close()
                        target.unlink(missing_ok=True)
                        raise PolicyViolationError(
                            f"Archive entry {name!r} decompressed past its declared size; "
                            f"limit is {limits.max_entry_bytes} bytes"
                        )
                    sink.write(chunk)
            total += max(0, extracted - member.file_size)
            if total > limits.max_total_bytes:
                target.unlink(missing_ok=True)
                raise PolicyViolationError(
                    f"Archive expands to more than {limits.max_total_bytes} bytes"
                )
            written.append(target)

    return sorted(written)
