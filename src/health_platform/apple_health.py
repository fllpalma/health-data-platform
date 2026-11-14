"""Read health records from an Apple Health export.xml, one at a time (streaming).

🍽️ The delivery arrives as one enormous box (export.xml can be several GB).
Instead of tipping it all onto the floor, we unload one jar at a time,
note what's on its label, and throw away the packaging before the next jar.

This is the RAW layer: values are kept exactly as delivered (all text).
Cleaning, typing and de-duplicating happen later, in dbt (Phase 2).
"""

from collections.abc import Iterator
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
