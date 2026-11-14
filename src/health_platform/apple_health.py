"""Read health records from an Apple Health export.xml, one at a time (streaming).

🍽️ The delivery arrives as one enormous box (export.xml can be several GB).
Instead of tipping it all onto the floor, we unload one jar at a time,
note what's on its label, and throw away the packaging before the next jar.

This is the RAW layer: values are kept exactly as delivered (all text).
Cleaning, typing and de-duplicating happen later, in dbt (Phase 2).
"""

import zipfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO
from xml.etree.ElementTree import iterparse

# XML attribute name -> our column name (snake_case, the usual style for tables)
FIELDS = {
    "type": "type",
    "sourceName": "source_name",
    "sourceVersion": "source_version",
    "device": "device",
    "unit": "unit",
    "creationDate": "creation_date",
    "startDate": "start_date",
    "endDate": "end_date",
    "value": "value",
}


def iter_records(source: str | Path | BinaryIO) -> Iterator[dict]:
    """Yield each top-level <Record> in the export as a dict, one at a time.

    `source` can be a file path or an already-open file (e.g. straight from a zip).
    Records nested inside other elements (e.g. blood-pressure <Correlation>) are
    skipped, because the export already lists them again at the top level.
    """
    depth = 0  # how deep we are: 0 = <HealthData>, 1 = its direct children
    root = None

    for event, elem in iterparse(source, events=("start", "end")):
        if event == "start":
            if root is None:
                root = elem  # remember <HealthData> so we can clear it as we go
            depth += 1
            continue

        # event == "end": this element and everything inside it is fully read
        depth -= 1
        if depth == 1:  # a direct child of <HealthData> just finished
            if elem.tag == "Record":
                yield _to_dict(elem)
            root.clear()  # throw away the packaging -> memory stays flat


def _to_dict(elem) -> dict:
    record = {column: elem.get(attribute) for attribute, column in FIELDS.items()}
    record["metadata"] = {
        entry.get("key"): entry.get("value") for entry in elem.iter("MetadataEntry")
    }
    return record


# --- Reading straight from the zip (the original delivery) -------------------


def find_export_xml(names: list[str]) -> str:
    """Pick the main records file among the zip's file names.

    Real-world trap: the file is named after the phone's language
    ("export.xml", "exportação.xml", ...) and the name can arrive garbled
    because zips don't always record their text encoding. So we never search
    for a fixed name: we take the one .xml that is NOT the clinical export_cda.xml.
    """
    candidates = [
        name
        for name in names
        if name.lower().endswith(".xml")
        and not name.rsplit("/", 1)[-1].lower().startswith("export_cda")
    ]
    if len(candidates) != 1:
        raise ValueError(f"Expected exactly one main export .xml, found: {candidates}")
    return candidates[0]


@contextmanager
def open_export_xml(zip_path: str | Path) -> Iterator[BinaryIO]:
    """Open the main export XML inside the zip as a stream (nothing unzipped to disk)."""
    with zipfile.ZipFile(zip_path) as archive:
        with archive.open(find_export_xml(archive.namelist())) as xml_file:
            yield xml_file


def read_export_date(source: str | Path | BinaryIO) -> str | None:
    """Return the export's <ExportDate value>. It sits at the top, so this stops early."""
    for _event, elem in iterparse(source, events=("end",)):
        if elem.tag == "ExportDate":
            return elem.get("value")
    return None


def is_synthetic_export(source: str | Path | BinaryIO) -> bool:
    """True only if stamped synthetic="true" (our generator). Real exports never are."""
    for _event, elem in iterparse(source, events=("start",)):
        return elem.tag == "HealthData" and elem.get("synthetic") == "true"
    return False
