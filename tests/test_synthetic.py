"""The synthetic export must look like a real one to our parser, and be identical on every run."""

from health_platform.apple_health import iter_records, open_export_xml, read_export_date
from health_platform.synthetic import build_records, write_export_zip


def test_synthetic_zip_is_readable_by_the_real_parser(tmp_path):
    path = write_export_zip(tmp_path / "synthetic.zip")
    with open_export_xml(path) as xml_file:
        assert read_export_date(xml_file) == "2026-10-22 00:00:00 +0000"
    with open_export_xml(path) as xml_file:
        records = list(iter_records(xml_file))
    assert len(records) == len(build_records())
    types = {r["type"] for r in records}
    assert "HKQuantityTypeIdentifierStepCount" in types
    assert "HKCategoryTypeIdentifierSleepAnalysis" in types


def test_synthetic_data_is_deterministic():
    assert build_records(seed=42) == build_records(seed=42)


def test_synthetic_data_contains_the_known_traps():
    rows = build_records()
    assert len(rows) != len(set(rows)), "exact duplicates expected"
    assert any("Synthetic Watch 2" in r for r in rows), (
        "second Watch (duplicate stand hours) expected"
    )
