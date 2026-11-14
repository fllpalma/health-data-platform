# 3. dbt Core v1 (Apache-2.0) for transformations, not dbt v2 (yet)

- **Date:** 2026-11-14
- **Status:** Accepted

## Context
Phase 2 uses dbt to turn raw records into clean, tested tables in Postgres.
When installing, dbt announced that **v2** is now the default for new installations. v2 is a rewrite (Rust engine) distributed
under the proprietary *dbt Product Licensing Agreement*, with an Apache-2.0 subset ("dbt OSS"). Launch material lists
Snowflake, BigQuery, Databricks and Redshift; Postgres support could not be confirmed.

## Decision
Use **dbt Core 1.12 + dbt-postgres 1.11** (both Apache-2.0), installed via `uv`.
Project lives in `transform/`; credentials come from `.env` via `env_var()`; layers write to their own schemas
(`staging`, `intermediate`, `marts`).

## Consequences
- ✅ Fully open source, free, mature, supports Postgres; matches what most teams run today.
- ✅ SQL models and tests are largely portable: revisit v2 in Phase 2b (Snowflake is supported there).
- ➖ v1 will eventually be superseded; an upgrade will be needed later (record it as a new ADR).
