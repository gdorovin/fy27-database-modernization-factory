"""Determinism helpers: hashing, canonical serialization, and file I/O."""

from __future__ import annotations

from pathlib import Path

import pytest

from dbmodernize.errors import OutputExistsError, UsageError
from dbmodernize.utils.hashing import canonical_json, content_hash, slugify, stable_id
from dbmodernize.utils.io import (
    read_csv_rows,
    read_json,
    read_yaml,
    write_json,
    write_text,
    write_yaml,
)


class TestHashing:
    def test_hash_is_independent_of_key_order(self) -> None:
        assert content_hash({"a": 1, "b": 2}) == content_hash({"b": 2, "a": 1})

    def test_hash_changes_when_content_changes(self) -> None:
        """This is what makes an approval stale when the artifact is edited."""
        assert content_hash({"a": 1}) != content_hash({"a": 2})

    def test_hash_is_prefixed_and_well_formed(self) -> None:
        digest = content_hash({"a": 1})
        assert digest.startswith("sha256:")
        assert len(digest) == len("sha256:") + 64

    def test_canonical_json_is_compact_and_sorted(self) -> None:
        assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'

    def test_stable_id_is_reproducible_and_readable(self) -> None:
        first = stable_id("wl", "Store operations")
        assert first == stable_id("wl", "Store operations")
        assert first.startswith("wl-store-operations-")

    def test_stable_id_disambiguates_names_that_slugify_alike(self) -> None:
        assert stable_id("wl", "Store Operations") != stable_id("wl", "Store-Operations!")

    @pytest.mark.parametrize(
        ("value", "expected"),
        [("Store Operations", "store-operations"), ("  ", "unknown"), ("A/B", "a-b")],
    )
    def test_slugify(self, value: str, expected: str) -> None:
        assert slugify(value) == expected


class TestFileIo:
    def test_write_uses_lf_endings_on_every_platform(self, tmp_path: Path) -> None:
        """CRLF would make generated artifacts differ between contributors."""
        path = write_text(tmp_path / "a.md", "one\ntwo")
        assert b"\r\n" not in path.read_bytes()

    def test_write_adds_a_trailing_newline(self, tmp_path: Path) -> None:
        path = write_text(tmp_path / "a.md", "no newline")
        assert path.read_text(encoding="utf-8").endswith("\n")

    def test_write_is_utf8_regardless_of_platform_default(self, tmp_path: Path) -> None:
        path = write_text(tmp_path / "a.md", "naïve café — ελληνικά")
        assert path.read_text(encoding="utf-8").startswith("naïve café")

    def test_existing_files_are_not_overwritten_silently(self, tmp_path: Path) -> None:
        target = tmp_path / "a.md"
        write_text(target, "first")
        with pytest.raises(OutputExistsError, match="--force"):
            write_text(target, "second")
        assert target.read_text(encoding="utf-8").strip() == "first"

    def test_force_overwrites(self, tmp_path: Path) -> None:
        target = tmp_path / "a.md"
        write_text(target, "first")
        write_text(target, "second", force=True)
        assert target.read_text(encoding="utf-8").strip() == "second"

    def test_dry_run_writes_nothing_but_reports_the_path(self, tmp_path: Path) -> None:
        target = write_text(tmp_path / "a.md", "content", dry_run=True)
        assert target == tmp_path / "a.md"
        assert not target.exists()

    def test_json_is_sorted_so_diffs_are_reviewable(self, tmp_path: Path) -> None:
        path = write_json(tmp_path / "a.json", {"b": 1, "a": 2})
        assert path.read_text(encoding="utf-8").index('"a"') < path.read_text(
            encoding="utf-8"
        ).index('"b"')

    def test_round_trip_json_and_yaml(self, tmp_path: Path) -> None:
        payload = {"alpha": [1, 2], "beta": {"gamma": "delta"}}
        assert read_json(write_json(tmp_path / "a.json", payload)) == payload
        assert read_yaml(write_yaml(tmp_path / "a.yaml", payload)) == payload

    def test_invalid_json_names_the_line(self, tmp_path: Path) -> None:
        path = tmp_path / "a.json"
        path.write_text('{"a": }', encoding="utf-8")
        with pytest.raises(UsageError, match="line"):
            read_json(path)

    def test_csv_headers_and_values_are_stripped(self, tmp_path: Path) -> None:
        path = tmp_path / "a.csv"
        path.write_text(" name , size \n Example , 10 \n", encoding="utf-8")
        assert read_csv_rows(path) == [{"name": "Example", "size": "10"}]


def test_oversized_read_is_configurable(tmp_path: Path) -> None:
    from dbmodernize.utils.io import read_text

    path = tmp_path / "a.txt"
    path.write_text("x" * 100, encoding="utf-8")

    with pytest.raises(UsageError, match="import limit"):
        read_text(path, max_bytes=10)
    assert len(read_text(path, max_bytes=1000)) == 100
