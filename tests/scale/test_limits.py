"""Scale behaviour at the documented limits.

`MAX_RECORDS_PER_FILE` and `MAX_IMPORT_BYTES` were stated in code comments and in
SECURITY.md and exercised nowhere, which meant two claims went untested: that the limits
actually stop an oversized import, and that an estate just under them still works.

The second matters more. A limit that also breaks the normal case is not a safety control,
it is an outage — and 5,000 databases is a large estate, not an implausible one.

Marked `slow` so the fast loop stays fast. CI runs the full suite.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from dbmodernize.adapters.base import MAX_RECORDS_PER_FILE
from dbmodernize.adapters.csv_adapter import CsvInventoryAdapter
from dbmodernize.errors import UsageError
from dbmodernize.evidence.normalize import normalize_directory
from dbmodernize.utils.io import MAX_IMPORT_BYTES, read_csv_rows

pytestmark = pytest.mark.slow

HEADER = "name,engine,version,size_gb,measured,deps_confirmed,features,notes\n"


def _inventory(path: Path, rows: int) -> Path:
    body = "".join(
        f"db-{index:05d},sql-server,15.0,{100 + index},true,true,,\n" for index in range(rows)
    )
    path.write_text(HEADER + body, encoding="utf-8", newline="\n")
    return path


def test_an_estate_just_under_the_limit_still_works(tmp_path: Path) -> None:
    path = _inventory(tmp_path / "large.csv", MAX_RECORDS_PER_FILE - 1)
    records = CsvInventoryAdapter().extract(path, "eng-scale", date(2026, 3, 2))

    assert len(records) == MAX_RECORDS_PER_FILE - 1
    assert len({record.id for record in records}) == len(records), "record ids collided at scale"


def test_exceeding_the_record_limit_is_refused_with_a_usable_message(tmp_path: Path) -> None:
    path = _inventory(tmp_path / "toolarge.csv", MAX_RECORDS_PER_FILE + 1)
    with pytest.raises(UsageError) as excinfo:
        CsvInventoryAdapter().extract(path, "eng-scale", date(2026, 3, 2))

    message = str(excinfo.value)
    assert str(MAX_RECORDS_PER_FILE) in message
    assert "Split the export" in message, "refusal must say what to do next"


def test_normalization_holds_up_across_a_large_estate(tmp_path: Path) -> None:
    """Sorting, merging and conflict detection are the parts that scale badly."""
    evidence = tmp_path / "evidence"
    evidence.mkdir()
    _inventory(evidence / "inventory.csv", 2_000)

    bundle = normalize_directory(evidence, engagement_id="eng-scale", collected_on=date(2026, 3, 2))

    assert len(bundle.records) == 2_000
    assert not bundle.unresolved_conflicts, "one source cannot disagree with itself"
    ids = [record.id for record in bundle.records]
    assert ids == sorted(ids), "records must stay sorted or output stops being reproducible"


def test_a_file_above_the_byte_limit_is_refused_before_it_is_parsed(tmp_path: Path) -> None:
    """The byte guard has to fire on size alone; parsing first is how you run out of memory."""
    path = tmp_path / "huge.csv"
    filler = "x" * 1024
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(HEADER)
        written = len(HEADER)
        while written <= MAX_IMPORT_BYTES:
            line = f"db,sql-server,15.0,1,true,true,,{filler}\n"
            handle.write(line)
            written += len(line)

    with pytest.raises(UsageError) as excinfo:
        read_csv_rows(path)

    message = str(excinfo.value)
    assert str(MAX_IMPORT_BYTES) in message, "the refusal must name the limit it enforced"
    assert "import limit" in message
