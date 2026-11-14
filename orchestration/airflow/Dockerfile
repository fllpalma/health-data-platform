# Our Airflow image: the official Apache image + what our pipeline needs, baked in and pinned.
# 🍽️ Two separate stations in one kitchen:
#   - Airflow's own Python (the head chef's office) gets only Cosmos (renders dbt models as tasks)
#   - /opt/health-venv (the prep station) gets OUR project + dbt + dlt, from uv.lock, so their
#     library versions never clash with Airflow's.
FROM apache/airflow:3.4.0-python3.12

# Airflow side: Cosmos only (pinned)
RUN pip install --no-cache-dir "astronomer-cosmos==1.16.0"

# Project side: exact versions from uv.lock, in a separate virtual environment
USER root
COPY --from=ghcr.io/astral-sh/uv:0.12.9 /uv /usr/local/bin/uv
ENV UV_PROJECT_ENVIRONMENT=/opt/health-venv \
    UV_PYTHON=/usr/local/bin/python \
    UV_PYTHON_DOWNLOADS=never \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
WORKDIR /opt/project
COPY pyproject.toml uv.lock .python-version ./
COPY src ./src
RUN uv sync --frozen --no-dev && chown -R airflow:0 /opt/health-venv /opt/project
USER airflow
WORKDIR /opt/airflow
