"""Adapters and evidence normalization."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from dbmodernize.adapters import default_registry
from dbmodernize.adapters.csv_adapter import CsvInventoryAdapter
from dbmodernize.errors import UsageError
from dbmodernize.evidence.normalize import (
    detect_conflicts,
    merged_attributes,
    normalize_directory,
)
from dbmodernize.models.evidence import Confidence, EvidenceClass, EvidenceSource

HEADER = "name,platform,version,size_gb,measured,deps_confirmed,features,notes"


def _csv(tmp_path: Path, *rows: str, filename: str = "inventory.csv") -> Path:
    path = tmp_path / filename
    path.write_text("\n".join([HEADER, *rows]) + "\n", encoding="utf-8")
    return path


class TestCsvAdapter:
    def test_unmeasured_rows_are_user_provided_not_observed(self, tmp_path: Path) -> None:
        """A spreadsheet is what a human believes, not what a tool measured."""
        path = _csv(tmp_path, "Example,sql-server,15.0,120,false,true,,Filled in by hand")
        records = CsvInventoryAdapter().extract(path, "eng-test", date(2026, 3, 2))

        assert len(records) == 1
        assert records[0].evidence_class is EvidenceClass.USER_PROVIDED
        assert records[0].confidence is Confidence.LOW

    def test_measured_rows_are_observed(self, tmp_path: Path) -> None:
        path = _csv(tmp_path, "Example,sql-server,15.0,120,true,true,,Measured over a week")
        records = CsvInventoryAdapter().extract(path, "eng-test", date(2026, 3, 2))

        assert records[0].evidence_class is EvidenceClass.OBSERVED
        assert records[0].confidence is Confidence.MEDIUM

    def test_source_ref_locates_the_row(self, tmp_path: Path) -> None:
        path = _csv(tmp_path, "Example,sql-server,15.0,120,true,true,,")
        records = CsvInventoryAdapter().extract(path, "eng-test", date(2026, 3, 2))
        assert records[0].source_ref == "inventory.csv#row=2"

    def test_empty_cells_become_absent_rather_than_guessed(self, tmp_path: Path) -> None:
        path = _csv(tmp_path, "Example,sql-server,,,,true,,")
        records = CsvInventoryAdapter().extract(path, "eng-test", date(2026, 3, 2))
        assert "source_version" not in records[0].attributes
        assert "data_size_gb" not in records[0].attributes

    def test_semicolon_lists_are_split_and_sorted(self, tmp_path: Path) -> None:
        path = _csv(tmp_path, "Example,sql-server,15.0,10,true,true,sql-agent;clr;filestream,")
        records = CsvInventoryAdapter().extract(path, "eng-test", date(2026, 3, 2))
        assert records[0].attributes["instance_features"] == ["clr", "filestream", "sql-agent"]

    def test_header_only_file_yields_nothing(self, tmp_path: Path) -> None:
        path = _csv(tmp_path)
        assert CsvInventoryAdapter().extract(path, "eng-test", date(2026, 3, 2)) == []

    def test_missing_header_is_an_error(self, tmp_path: Path) -> None:
        path = tmp_path / "empty.csv"
        path.write_text("", encoding="utf-8")
        with pytest.raises(UsageError, match="no header"):
            CsvInventoryAdapter().extract(path, "eng-test", date(2026, 3, 2))


class TestCsvColumnCoverage:
    """Unrecognised columns must be reported, because dropping one invents a finding.

    If ``Recovery Point Objective (min)`` is discarded in silence, the assessment reports
    no stated recovery objective. That reads as a fact about the customer's estate when it
    is really a fact about our column map, and nobody downstream can tell the difference.
    """

    def test_spelling_variations_reach_the_same_attribute(self, tmp_path: Path) -> None:
        path = tmp_path / "variants.csv"
        path.write_text(
            "Database Name,Engine,Data Size (GB),RPO (min),Measured\n"
            "Example,sql-server,120,15,true\n",
            encoding="utf-8",
        )
        records = CsvInventoryAdapter().extract(path, "eng-test", date(2026, 3, 2))

        assert records[0].attributes["data_size_gb"] == 120.0
        assert records[0].attributes["rpo_minutes"] == 15
        assert "unmapped_columns" not in records[0].attributes

    def test_an_unrecognised_column_is_reported_on_every_row_it_affects(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "extra.csv"
        path.write_text(
            "Database Name,Engine,Encryption At Rest\n"
            "Example,sql-server,tde\n"
            "Second,sql-server,none\n",
            encoding="utf-8",
        )
        records = CsvInventoryAdapter().extract(path, "eng-test", date(2026, 3, 2))

        assert len(records) == 2
        for record in records:
            assert record.attributes["unmapped_columns"] == ["Encryption At Rest"]

    def test_the_reported_spelling_is_the_author_s_not_ours(self, tmp_path: Path) -> None:
        """A normalized name would send the reader looking for a column that is not there."""
        path = tmp_path / "extra.csv"
        path.write_text("name,engine,Backup Vendor\nExample,sql-server,acme\n", encoding="utf-8")
        records = CsvInventoryAdapter().extract(path, "eng-test", date(2026, 3, 2))
        assert records[0].attributes["unmapped_columns"] == ["Backup Vendor"]

    def test_deliberately_ignored_columns_are_not_reported(self, tmp_path: Path) -> None:
        """Discarding a cost centre on purpose is not the same as failing to read it."""
        path = tmp_path / "cmdb.csv"
        path.write_text(
            "name,engine,CMDB ID,Cost Centre,Last Updated\nExample,sql-server,X1,CC-9,2026-01-01\n",
            encoding="utf-8",
        )
        records = CsvInventoryAdapter().extract(path, "eng-test", date(2026, 3, 2))
        assert "unmapped_columns" not in records[0].attributes


class TestAdapterSelection:
    def test_json_adapters_discriminate_on_document_shape(self, tmp_path: Path) -> None:
        """Three adapters read .json. Selection must depend on content, not extension."""
        registry = default_registry()
        shapes = {
            "arc.json": ({"instances": []}, EvidenceSource.ARC_ENABLED_SQL),
            "migrate.json": ({"databases": []}, EvidenceSource.AZURE_MIGRATE),
            "dms.json": ({"results": []}, EvidenceSource.DATA_MIGRATION_SERVICE),
            "ssma.json": ({"schemas": []}, EvidenceSource.SSMA),
        }

        for filename, (document, expected) in shapes.items():
            path = tmp_path / filename
            path.write_text(json.dumps(document), encoding="utf-8")
            adapter = registry.for_path(path)
            assert adapter is not None, f"no adapter matched {filename}"
            assert adapter.source is expected

    def test_unknown_adapter_name_is_rejected_with_the_options(self) -> None:
        with pytest.raises(UsageError, match="Available:"):
            default_registry().by_name("not-a-real-adapter")


class TestNormalization:
    def test_directory_with_nothing_readable_is_an_error(self, tmp_path: Path) -> None:
        (tmp_path / "notes.txt").write_text("not an export", encoding="utf-8")
        with pytest.raises(UsageError, match="No supported evidence files"):
            normalize_directory(tmp_path, "eng-test", date(2026, 3, 2))

    def test_generated_at_comes_from_the_engagement_not_the_clock(self, tmp_path: Path) -> None:
        """Reproducibility beats knowing the exact minute a run happened."""
        _csv(tmp_path, "Example,sql-server,15.0,10,true,true,,")
        bundle = normalize_directory(tmp_path, "eng-test", date(2026, 3, 2))
        assert bundle.generated_at.date() == date(2026, 3, 2)

    def test_conflicting_versions_are_recorded_not_resolved(self, tmp_path: Path) -> None:
        _csv(tmp_path, "Example,sql-server,15.0,100,true,true,,", filename="a.csv")
        _csv(tmp_path, "Example,sql-server,13.0,100,true,true,,", filename="b.csv")

        bundle = normalize_directory(tmp_path, "eng-test", date(2026, 3, 2))
        conflicts = [c for c in bundle.unresolved_conflicts if c.attribute == "source_version"]

        assert conflicts, "a version disagreement must be surfaced"
        assert sorted(conflicts[0].values) == ["13.0", "15.0"]
        assert conflicts[0].resolution_owner_role

    def test_conflicted_attributes_are_omitted_from_the_merged_view(self, tmp_path: Path) -> None:
        """A merged view that silently picks a winner hides the disagreement."""
        _csv(tmp_path, "Example,sql-server,15.0,100,true,true,,", filename="a.csv")
        _csv(tmp_path, "Example,sql-server,13.0,100,true,true,,", filename="b.csv")

        bundle = normalize_directory(tmp_path, "eng-test", date(2026, 3, 2))
        merged = merged_attributes(bundle, "wl-example")
        assert "source_version" not in merged

    def test_small_numeric_differences_are_measurement_noise(self, tmp_path: Path) -> None:
        _csv(tmp_path, "Example,sql-server,15.0,100,true,true,,", filename="a.csv")
        _csv(tmp_path, "Example,sql-server,15.0,102,true,true,,", filename="b.csv")

        bundle = normalize_directory(tmp_path, "eng-test", date(2026, 3, 2))
        assert not [c for c in bundle.conflicts if c.attribute == "data_size_gb"]

    def test_large_numeric_differences_are_a_conflict(self, tmp_path: Path) -> None:
        _csv(tmp_path, "Example,sql-server,15.0,100,true,true,,", filename="a.csv")
        _csv(tmp_path, "Example,sql-server,15.0,900,true,true,,", filename="b.csv")

        bundle = normalize_directory(tmp_path, "eng-test", date(2026, 3, 2))
        assert [c for c in bundle.conflicts if c.attribute == "data_size_gb"]

    def test_records_are_sorted_for_stable_output(self, tmp_path: Path) -> None:
        _csv(
            tmp_path,
            "Zulu,sql-server,15.0,10,true,true,,",
            "Alpha,sql-server,15.0,10,true,true,,",
        )
        bundle = normalize_directory(tmp_path, "eng-test", date(2026, 3, 2))
        subjects = [record.subject_id for record in bundle.records]
        assert subjects == sorted(subjects)

    def test_no_conflict_when_only_one_source_reports_an_attribute(self, tmp_path: Path) -> None:
        _csv(tmp_path, "Example,sql-server,15.0,,true,true,,", filename="a.csv")
        _csv(tmp_path, "Example,sql-server,,100,true,true,,", filename="b.csv")

        bundle = normalize_directory(tmp_path, "eng-test", date(2026, 3, 2))
        assert not bundle.unresolved_conflicts
        merged = merged_attributes(bundle, "wl-example")
        assert merged["source_version"] == "15.0"
        assert merged["data_size_gb"] == 100.0


def test_detect_conflicts_ignores_attributes_that_do_not_change_a_decision() -> None:
    """Noise in a free-text field is not a disagreement worth stopping the line for."""
    from dbmodernize.models.evidence import EvidenceRecord

    def record(identifier: str, note: str) -> EvidenceRecord:
        return EvidenceRecord(
            id=identifier,
            engagement_id="eng-test",
            subject_type="workload",
            subject_id="wl-a",
            source=EvidenceSource.CSV_INVENTORY,
            source_ref=f"{identifier}.csv",
            collected_on=date(2026, 3, 2),
            evidence_class=EvidenceClass.OBSERVED,
            attributes={"host_alias": note},
        )

    assert detect_conflicts([record("ev-1", "host-a"), record("ev-2", "host-b")]) == []
