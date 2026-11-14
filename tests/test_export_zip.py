"""Tests for reading the export straight from its zip. All data is synthetic."""

import zipfile
from pathlib import Path

import pytest

from health_platform.apple_health import (
    find_export_xml,
    iter_records,
    open_export_xml,
    read_export_date,
)
from health_platform.pipeline import batched

SAMPLE = Path(__file__).parent / "fixtures" / "export_sample.xml"


@pytest.mark.parametrize(
    "main_name",
    [
        "apple_health_export/export.xml",  # English iPhone
        "apple_health_export/exportação.xml",  # Portuguese iPhone
        "apple_health_export/exportac╠ºa╠âo.xml",  # same, garbled by the zip (seen in real life)
    ],
)
def test_finds_main_xml_whatever_its_name(main_name):
    names = [
        "apple_health_export/",
        main_name,
        "apple_health_export/export_cda.xml",  # clinical copy: must be ignored
        "apple_health_export/workout-routes/route_1.gpx",
        "apple_health_export/electrocardiograms/ecg_1.csv",
    ]
    assert find_export_xml(names) == main_name


def test_refuses_to_guess_when_ambiguous():
    with pytest.raises(ValueError):
        find_export_xml(["a/export.xml", "a/other.xml"])
    with pytest.raises(ValueError):
        find_export_xml(["a/export_cda.xml"])  # no main file at all


@pytest.fixture
def sample_zip(tmp_path) -> Path:
    path = tmp_path / "exportação.zip"
    with zipfile.ZipFile(path, "w") as z:
        z.write(SAMPLE, "apple_health_export/exportação.xml")
        z.writestr("apple_health_export/export_cda.xml", "<ClinicalDocument/>")
        z.writestr("apple_health_export/workout-routes/route_1.gpx", "<gpx/>")
    return path


def test_streams_records_straight_from_zip(sample_zip):
    with open_export_xml(sample_zip) as xml_file:
        assert len(list(iter_records(xml_file))) == 5


def test_reads_export_date(sample_zip):
    with open_export_xml(sample_zip) as xml_file:
        assert read_export_date(xml_file) == "2026-11-14 10:00:00 +0000"


def test_batched_splits_without_losing_items():
    assert list(batched(range(5), 2)) == [[0, 1], [2, 3], [4]]


def test_raw_table_contract_covers_every_parsed_field():
    # Bug found in the CI rehearsal: dlt skipped the all-empty "device" column on synthetic data.
    from health_platform.apple_health import FIELDS
    from health_platform.pipeline import RAW_COLUMNS

    assert set(FIELDS.values()) | {"metadata", "export_date"} == set(RAW_COLUMNS)
