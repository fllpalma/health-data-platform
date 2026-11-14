"""Tests for the Apple Health export parser.

They use a small SYNTHETIC export (tests/fixtures/export_sample.xml), never real data.
"""

from collections.abc import Iterator
from pathlib import Path

from health_platform.apple_health import iter_records

SAMPLE = Path(__file__).parent / "fixtures" / "export_sample.xml"


def test_reads_only_top_level_records():
    # 5 top-level records; the copy nested inside the blood-pressure Correlation
    # must NOT be counted twice, and Workout / ActivitySummary are not records.
    records = list(iter_records(SAMPLE))
    assert len(records) == 5


def test_maps_fields_and_keeps_values_raw():
    first = next(iter_records(SAMPLE))
    assert first == {
        "type": "HKQuantityTypeIdentifierStepCount",
        "source_name": "Test iPhone",
        "source_version": "18.0",
        "device": "<<HKDevice: 0x1>, name:iPhone>",
        "unit": "count",
        "creation_date": "2026-11-01 09:05:00 +0000",
        "start_date": "2026-11-01 09:00:00 +0000",
        "end_date": "2026-11-01 09:05:00 +0000",
        "value": "412",  # raw layer: kept as text, exactly as delivered
        "metadata": {},
    }


def test_missing_attributes_become_none():
    # The Watch step record has no "device"; the sleep record has no "unit".
    records = list(iter_records(SAMPLE))
    assert records[1]["device"] is None
    assert records[3]["unit"] is None


def test_collects_metadata_entries():
    heart_rate = list(iter_records(SAMPLE))[2]
    assert heart_rate["metadata"] == {"HKMetadataKeyHeartRateMotionContext": "1"}


def test_category_values_are_text():
    sleep = list(iter_records(SAMPLE))[3]
    assert sleep["value"] == "HKCategoryValueSleepAnalysisAsleepCore"


def test_streams_lazily():
    # Must hand records out one at a time (a generator), not build one giant list,
    # so a multi-GB export never has to fit in memory.
    assert isinstance(iter_records(SAMPLE), Iterator)


def test_accepts_an_open_file():
    # PR 3 will read export.xml straight out of export.zip without unzipping to disk.
    with SAMPLE.open("rb") as f:
        assert len(list(iter_records(f))) == 5
