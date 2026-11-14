"""apple_health_pipeline: new export in data/inbox/ -> lake + warehouse -> dbt (models + tests).

🍽️ The head chef's schedule:
  every 10 minutes, check the back door (inbox) for a new delivery;
  if there is one: store it in the pantry and load the shelves (our pipeline),
  then let the prep chefs cook every recipe in order, tasting each dish (dbt via Cosmos),
  and finally write the delivery in the logbook (ops.processed_exports).

Idempotent: each export's sha256 fingerprint is recorded, so the same file is never processed twice.
"""

import hashlib
import logging
import shlex
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.sdk import dag, task
from airflow.sdk.exceptions import AirflowSkipException
from cosmos import DbtTaskGroup, ExecutionConfig, ProfileConfig, ProjectConfig, RenderConfig
from cosmos.constants import InvocationMode

log = logging.getLogger(__name__)

PROJECT_DIR = Path("/opt/project")
INBOX = PROJECT_DIR / "data" / "inbox"
DBT_PROJECT = PROJECT_DIR / "transform"
PROJECT_PYTHON = "/opt/health-venv/bin/python"  # our project's own environment (see ADR 0007)
WAREHOUSE_CONN = "health_warehouse"

REGISTRY_DDL = """
create schema if not exists ops;
create table if not exists ops.processed_exports (
    sha256        text primary key,
    file_name     text not null,
    size_bytes    bigint not null,
    dag_run_id    text not null,
    processed_at  timestamptz not null default now()
);
"""


def notify_failure(context) -> None:
    """Failure alert: a loud log line for now; Phase 7 (n8n) turns it into a notification."""
    ti = context["task_instance"]
    log.error(
        "❌ PIPELINE FAILURE: dag=%s task=%s run=%s try=%s",
        ti.dag_id,
        ti.task_id,
        context["run_id"],
        ti.try_number,
    )


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dag(
    dag_id="apple_health_pipeline",
    description="New Apple Health export -> lake + warehouse -> dbt models and tests",
    schedule="*/10 * * * *",  # check the inbox every 10 minutes
    start_date=datetime(2026, 11, 1),
    catchup=False,  # don't run for past time slots: an export is an event, not a time period
    max_active_runs=1,  # never two loads at once
    default_args={
        "retries": 3,  # transient failures (network, DB restart) fix themselves
        "retry_delay": timedelta(minutes=5),
        "on_failure_callback": notify_failure,
    },
    tags=["apple-health", "ingestion", "dbt"],
)
def apple_health_pipeline():
    @task(retries=0)
    def find_new_export() -> dict:
        """Return the newest unprocessed export in the inbox; otherwise skip the run."""
        sys.path.append(str(PROJECT_DIR / "src"))  # our stdlib-only parser helpers
        from health_platform.apple_health import is_synthetic_export, open_export_xml

        hook = PostgresHook(postgres_conn_id=WAREHOUSE_CONN)
        hook.run(REGISTRY_DDL)
        done = {row[0] for row in hook.get_records("select sha256 from ops.processed_exports")}

        for path in sorted(INBOX.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True):
            with open_export_xml(path) as xml_file:
                if is_synthetic_export(
                    xml_file
                ):  # safety lock: never overwrite real data with fake
                    log.warning("Skipping synthetic export in inbox: %s", path.name)
                    continue
            fingerprint = _sha256(path)
            if fingerprint in done:
                log.info("Already processed: %s", path.name)
                continue
            log.info("New export found: %s (%s)", path.name, fingerprint[:12])
            return {"path": str(path), "sha256": fingerprint, "size": path.stat().st_size}

        raise AirflowSkipException("No new export in the inbox.")

    @task.bash(cwd=str(PROJECT_DIR))
    def load_export(export: dict) -> str:
        """① zip -> lake (as-is) -> raw_apple_health.records (our Phase 1 pipeline)."""
        return f"{PROJECT_PYTHON} -m health_platform.pipeline {shlex.quote(export['path'])}"

    transform = DbtTaskGroup(
        group_id="dbt",  # ② one Airflow task per dbt model, each followed by its tests
        project_config=ProjectConfig(dbt_project_path=DBT_PROJECT),
        profile_config=ProfileConfig(
            profile_name="health",
            target_name="local",
            profiles_yml_filepath=DBT_PROJECT / "profiles.yml",
        ),
        # dbt lives in our separate venv, so run it as its own program (subprocess)
        execution_config=ExecutionConfig(
            dbt_executable_path="/opt/health-venv/bin/dbt",
            invocation_mode=InvocationMode.SUBPROCESS,
        ),
        render_config=RenderConfig(  # also used to READ the project (dbt ls) when drawing the tasks
            dbt_executable_path="/opt/health-venv/bin/dbt",
            invocation_mode=InvocationMode.SUBPROCESS,
        ),
        default_args={"retries": 1},
    )

    @task
    def record_processed(export: dict, **context) -> None:
        """③ Write the delivery in the logbook, only after everything succeeded."""
        PostgresHook(postgres_conn_id=WAREHOUSE_CONN).run(
            "insert into ops.processed_exports (sha256, file_name, size_bytes, dag_run_id) "
            "values (%s, %s, %s, %s) on conflict (sha256) do nothing",
            parameters=(
                export["sha256"],
                Path(export["path"]).name,
                export["size"],
                context["run_id"],
            ),
        )
        log.info("✅ Recorded %s as processed.", Path(export["path"]).name)

    export = find_new_export()
    load_export(export) >> transform >> record_processed(export)


apple_health_pipeline()
