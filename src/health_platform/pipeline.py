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
    FIELDS,
    is_synthetic_export,
    iter_records,
    open_export_xml,
    read_export_date,
)
from health_platform.lake import upload_raw  # noqa: E402

BATCH_SIZE = 10_000  # records handed to dlt per batch (fast, memory stays small)
WORK_DIR = Path("data/.dlt")  # dlt's working files stay inside the gitignored data/ folder

# Data contract: the raw table ALWAYS has these columns, even if a column has no values in an
# export (dlt would otherwise skip all-empty columns and silently change the table's shape).
RAW_COLUMNS = {
    **{column: {"data_type": "text", "nullable": True} for column in FIELDS.values()},
    "metadata": {"data_type": "json", "nullable": True},
    "export_date": {"data_type": "text", "nullable": False},
}


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


def snowflake_credentials() -> dict:
    env = os.environ
    return {
        "host": env["SNOWFLAKE_ACCOUNT"],
        "username": env["SNOWFLAKE_USER"],
        "role": env.get("SNOWFLAKE_ROLE", "HEALTH_TRANSFORMER"),
        "warehouse": env.get("SNOWFLAKE_WAREHOUSE", "HEALTH_WH"),
        "database": env.get("SNOWFLAKE_DATABASE", "HEALTH"),
        "private_key_path": env["SNOWFLAKE_PRIVATE_KEY_PATH"],
        "private_key_passphrase": env["SNOWFLAKE_PRIVATE_KEY_PASSPHRASE"],
    }


def check_allowed(destination: str, synthetic: bool) -> None:
    """Privacy guardrail (CLAUDE.md rule 4): only SYNTHETIC exports may leave the Mac."""
    if destination != "postgres" and not synthetic:
        raise PermissionError(
            f"Refusing to send a real health export to '{destination}'. "
            "Only synthetic exports (python -m health_platform.synthetic) may leave this Mac."
        )


def run(zip_path: Path, destination: str = "postgres") -> None:
    with open_export_xml(zip_path) as xml_file:
        synthetic = is_synthetic_export(xml_file)
    check_allowed(destination, synthetic)

    with open_export_xml(zip_path) as xml_file:
        export_date = read_export_date(xml_file)
    if not export_date:
        raise ValueError("No <ExportDate> found: is this an Apple Health export?")
    print(f"Export date: {export_date} | synthetic: {synthetic} | destination: {destination}")

    # ① Lake: store the original zip untouched, organised by export date
    key = f"apple_health/export_date={export_date[:10]}/{zip_path.name}"
    print(f"① Uploaded to lake: {upload_raw(zip_path, key)}")

    # ② Warehouse: stream every record into raw_apple_health.records
    @dlt.resource(
        name="records",
        write_disposition="replace",  # full snapshot each export -> replace, never duplicate
        columns=RAW_COLUMNS,
    )
    def records():
        with open_export_xml(zip_path) as xml_file:
            for batch in batched(iter_records(xml_file), BATCH_SIZE):
                for record in batch:
                    record["export_date"] = export_date
                yield batch

    if destination == "snowflake":
        target = dlt.destinations.snowflake(credentials=snowflake_credentials())
    else:
        target = dlt.destinations.postgres(credentials=postgres_url())

    pipeline = dlt.pipeline(
        pipeline_name=f"apple_health_{destination}",  # separate state per warehouse
        destination=target,
        dataset_name="raw_apple_health",
        pipelines_dir=str(WORK_DIR),
    )
    print(f"② Loading records into {destination} (this can take a few minutes)...")
    print(pipeline.run(records()))


def main() -> None:
    parser = argparse.ArgumentParser(description="Load an Apple Health export into the platform.")
    parser.add_argument("zip_path", type=Path, help="path to the export .zip")
    parser.add_argument(
        "--destination",
        choices=["postgres", "snowflake"],
        default="postgres",
        help="warehouse to load into (snowflake accepts synthetic exports only)",
    )
    args = parser.parse_args()
    run(args.zip_path, args.destination)


if __name__ == "__main__":
    main()
