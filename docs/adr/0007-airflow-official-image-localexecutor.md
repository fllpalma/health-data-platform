# 7. Airflow 3 from the official image, LocalExecutor, in our own Compose file

- **Date:** 2026-11-14
- **Status:** Accepted

## Context
Phase 3 adds orchestration. `PLAN.md` suggested the Astro CLI (Astronomer). The project rules require Docker Compose
**profiles** per phase, everything as code, and Docker limited to ~12 GB. Apache's reference Compose file (Airflow 3.4.0)
uses CeleryExecutor + Redis + workers + Flower, sized for teams.

Airflow also has strict library constraints; our pipeline (dlt) and dbt pin their own versions.

## Decision
- **Official `apache/airflow:3.4.0-python3.12` image**, extended by our own `orchestration/airflow/Dockerfile` (pinned, built once).
- **LocalExecutor**: tasks run inside the scheduler. No Redis, Celery workers or Flower.
- Services under Compose profile **`orchestration`**: `airflow-db` (own Postgres, separate from the warehouse),
  `airflow-init`, `airflow-apiserver` (UI on `127.0.0.1:8080`), `airflow-scheduler`, `airflow-dag-processor`, `airflow-triggerer`.
- **Two Python environments in one image**: Airflow's (+ Cosmos 1.16.0, Apache-2.0) and `/opt/health-venv`
  (our project + dbt + dlt, installed from `uv.lock`), so neither can break the other.
- Secrets (DB password, Fernet key, JWT secret, admin password) are random values in `.env`; no defaults.
- Code (`src/`, `dags/`, `transform/`) is mounted, so code changes need no rebuild; dependency changes do.

## Consequences
- ✅ One infrastructure file, one start command per phase; ~5 GB lighter than the reference setup.
- ✅ Matches most self-hosted Airflow setups; skills transfer to Astronomer/MWAA/Composer (same DAG code).
- ➖ LocalExecutor doesn't scale beyond one machine. A team would switch to Celery or Kubernetes executors (Phase 9 covers Kubernetes).
- ➖ We don't learn the Astro CLI workflow itself.
