"""Phase 1 pipeline: Apple Health export.zip -> lake (as-is) -> warehouse (raw tables).

Run it:
    uv run --env-file .env python -m health_platform.pipeline data/inbox/<export>.zip

🍽️ ① the sealed delivery goes into the pantry, untouched;
   ② its jars are unpacked one by one onto the shelves (Postgres).
Re-running is safe (idempotent): same lake key is overwritten, the table is replaced.
"""

import argparse
import os
from collections.abc import Iterable, Iterator
from itertools import islice
from pathlib import Path
from urllib.parse import quote_plus

# Privacy + tidiness, set before dlt starts:
os.environ.setdefault("RUNTIME__DLTHUB_TELEMETRY", "false")  # no usage stats sent to dlt's servers
os.environ.setdefault("LOAD__DELETE_COMPLETED_JOBS", "true")  # don't keep temp copies after loading

import dlt  # noqa: E402  (must come after the settings above)

from health_platform.apple_health import (  # noqa: E402
    iter_records,
    open_export_xml,
    read_export_date,
)
from health_platform.lake import upload_raw  # noqa: E402

BATCH_SIZE = 10_000  # records handed to dlt per batch (fast, memory stays small)
WORK_DIR = Path("data/.dlt")  # dlt's working files stay inside the gitignored data/ folder


def batched(items: Iterable[dict], size: int) -> Iterator[list[dict]]:
    iterator = iter(items)
    while batch := list(islice(iterator, size)):
        yield batch


def postgres_url() -> str:
    env = os.environ
    return (
        f"postgresql://{quote_plus(env['POSTGRES_USER'])}:{quote_plus(env['POSTGRES_PASSWORD'])}"
        f"@{env.get('POSTGRES_HOST', '127.0.0.1')}:{env.get('POSTGRES_PORT', '5432')}"
        f"/{env.get('POSTGRES_DB', 'health')}"
    )


def run(zip_path: Path) -> None:
    with open_export_xml(zip_path) as xml_file:
        export_date = read_export_date(xml_file)
    if not export_date:
        raise ValueError("No <ExportDate> found: is this an Apple Health export?")
    print(f"Export date: {export_date}")

    # ① Lake: store the original zip untouched, organised by export date
    key = f"apple_health/export_date={export_date[:10]}/{zip_path.name}"
    print(f"① Uploaded to lake: {upload_raw(zip_path, key)}")

    # ② Warehouse: stream every record into raw_apple_health.records
    @dlt.resource(
        name="records",
        write_disposition="replace",  # full snapshot each export -> replace, never duplicate
        columns={"metadata": {"data_type": "json"}},
    )
    def records():
        with open_export_xml(zip_path) as xml_file:
            for batch in batched(iter_records(xml_file), BATCH_SIZE):
                for record in batch:
                    record["export_date"] = export_date
                yield batch

    pipeline = dlt.pipeline(
        pipeline_name="apple_health",
        destination=dlt.destinations.postgres(credentials=postgres_url()),
        dataset_name="raw_apple_health",
        pipelines_dir=str(WORK_DIR),
    )
    print("② Loading records into Postgres (this can take a few minutes)...")
    print(pipeline.run(records()))


def main() -> None:
    parser = argparse.ArgumentParser(description="Load an Apple Health export into the platform.")
    parser.add_argument("zip_path", type=Path, help="path to the export .zip")
    run(parser.parse_args().zip_path)


if __name__ == "__main__":
    main()
