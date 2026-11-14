# Project Plan — Personal Health Data Platform

Each phase builds on the one before. Don't start a phase until the previous gate is passed (see `CLAUDE.md`).
🍽️ = the restaurant analogy for that phase.

---

## Phase 0 — Setup
**Goal:** a professional workspace before any data moves.
- Install: Homebrew, Git, GitHub CLI (`gh`), Docker (Docker Desktop or OrbStack), `uv` (Python manager), pre-commit.
- Create the GitHub repo, protect `main` (changes only via pull request).
- Skeleton: `README.md`, `.gitignore` (blocks `data/` and health exports), `.env.example`, `docs/` (PLAN, GLOSSARY, LEARNINGS, `adr/`), pre-commit with `ruff`.
- First pull request: merge the skeleton.
- 🍽️ Building the kitchen before cooking: counters, rules, and a recipe book everyone shares.
- **Gate check:** repo on GitHub, a PR merged, `git status` shows no data files tracked.

## Phase 1 — Foundations (ingestion, lake, warehouse)
**Goal:** get the Apple Health export from a zip on disk into queryable tables.
- Docker Compose: SeaweedFS (S3-compatible data lake, see ADR 0002) + Postgres (warehouse).
- Python + `dlt`: unzip, parse `export.xml` (streamed — it's huge), land raw files in the lake (S3 API), load raw tables into Postgres.
- Learn: batch ingestion, raw vs. clean data, idempotency (re-running doesn't duplicate), schemas.
- Tests with `pytest` on the parser. CI: lint + tests on every PR (GitHub Actions).
- 🍽️ Deliveries arrive at the back door and go into the pantry, labelled and untouched.
- **Gate check:** query "steps per day for the last 30 days" from raw tables in Postgres.

## Phase 2 — Transformations (dbt)
**Goal:** turn raw records into trustworthy, business-ready tables.
- dbt Core: `staging` (clean, rename, type) → `intermediate` (dedupe iPhone vs Watch) → `marts` (daily sleep, activity, heart).
- dbt tests (not null, unique, accepted ranges), docs site, sqlfluff. Slim CI in GitHub Actions.
- Learn: data modelling, data contracts, testing data like code.
- 🍽️ Prep chefs follow written recipes; raw ingredients become ready dishes, quality-checked.
- **Gate check:** `dbt build` passes; dbt docs show the lineage graph.

## Phase 2b — Snowflake sprint (optional, 30-day trial)
**Goal:** run the same dbt project on Snowflake to learn how teams migrate between warehouses (Postgres → Snowflake) and to get hands-on with the warehouse my team uses at work.
- Timing: start the Snowflake free trial only when Phase 2's gate is passed (the trial gives $400 of usage over 30 days and ends when either runs out).
- Cost rules: never add a credit card, so the trial just stops when it ends. Use an X-Small warehouse with auto-suspend at 60 seconds. Tear everything down before the trial ends.
- Privacy: no raw health data in Snowflake. Load only daily summary tables or synthetic data.
- What we'll do: create a dbt profile/target for Snowflake, load the summary data, run dbt build on Snowflake, and compare it with Postgres (SQL differences, cost model, performance).
- 🍽️ The same recipes cooked in a rented professional kitchen for a month.
- **Gate check:** dbt build passes on both Postgres and Snowflake, and `docs/LEARNINGS.md` explains the differences in plain words.

## Phase 3 — Orchestration (Airflow)
**Goal:** everything runs on its own, in the right order, with retries.
- Airflow 3 (official image, LocalExecutor, Compose profile `orchestration`; see ADR 0007) running ingestion → dbt as a DAG; triggered when a new export lands.
- Learn: scheduling, dependencies, retries, backfills, alerts on failure.
- CI comparison: run the same lint + test pipeline in **Jenkins** (self-hosted, Docker, `Jenkinsfile`) alongside GitHub Actions. GitHub Actions stays the official PR check.
- Learn: hosted vs. self-hosted CI, why many enterprises still run Jenkins, and why Jenkins is *not* a data orchestrator (vs. Airflow).
- 🍽️ The head chef's schedule: who does what, when, and what happens if someone's late.
- 🍽️ Hired cleaning service (GitHub Actions) vs. your own cleaning crew (Jenkins).
- **Gate check:** drop a new export → pipeline runs end to end with no manual steps.

## Phase 4 — Streaming (Kafka)
**Goal:** handle data that arrives continuously, not once a day.
- Kafka (KRaft mode) or Redpanda. Producer replays heart-rate samples as a live stream; consumer writes to the lake/warehouse.
- Learn: events, topics, producers/consumers, batch vs. streaming trade-offs.
- 🍽️ The order-ticket rail: orders keep coming in and the kitchen handles them as they arrive.
- **Gate check:** watch heart-rate rows appear in Postgres in near-real time.

## Phase 5 — Observability & lineage
**Goal:** one screen showing the health of the whole platform.
- Prometheus (metrics), Grafana (dashboards), Loki (logs), OpenLineage + Marquez (lineage map).
- Dashboards: pipeline runs, failures, data freshness, row counts, plus your health trends.
- Learn: monitoring vs. observability, SLAs, data freshness, lineage.
- 🍽️ The screen on the kitchen wall: what's cooking, what's late, what failed.
- **Gate check:** break something on purpose → you see it in Grafana and trace it in Marquez.

## Phase 6 — Machine learning → production (Lambda)
**Goal:** a model that runs in the cloud like a real product, deployed automatically.
- Use case: predict sleep quality (or detect unusual resting heart rate) from daily marts.
- scikit-learn/XGBoost, MLflow (experiments + model registry), Evidently (drift).
- Serving: FastAPI in Docker locally → AWS Lambda (zip package) + API Gateway.
- Infra: OpenTofu (S3, Lambda, IAM, budget alert at €1), tested against AWS Emulator, deployed to real AWS free tier by GitHub Actions (OIDC, no stored keys) on merge.
- Privacy: only the model and synthetic sample data go to AWS.
- 🍽️ The test-kitchen notebook picks the best recipe; the food truck serves it only when a customer shows up.
- **Gate check:** merge a PR → model deploys automatically → call the endpoint and get a prediction.

## Phase 7 — Automation (n8n)
**Goal:** routine work happens by itself.
- n8n self-hosted (Community edition). Workflows: failure alerts, weekly health digest, retrain trigger on drift.
- Learn: event-driven automation, webhooks, when to use n8n vs. Airflow.
- 🍽️ The kitchen assistant who handles routine chores without being asked.
- **Gate check:** a failed DAG triggers an alert; the weekly digest arrives.

## Phase 8 — LLMs (local, private)
**Goal:** talk to your data in plain English.
- Ollama (7–8B models), LangChain + LangGraph, pgvector (in Postgres), Langfuse (self-hosted tracing).
- Builds: "ask your data" text-to-SQL agent · RAG over dbt docs and lineage · pipeline-failure triage agent triggered by n8n.
- Learn: embeddings, RAG, agents, evaluation, LLM observability.
- 🍽️ A sous-chef you can ask "what did we cook most this week?"
- **Gate check:** ask "did I sleep better in weeks I exercised more?" and get a correct, traced answer.

## Phase 9 — Kubernetes & GitOps: how big teams run it (required)
**Goal:** run the platform the way large companies do, on Kubernetes.
- Local Kubernetes (`kind`), Airflow via official Helm chart, Argo CD (GitOps).
- Learn: pods, deployments, services, namespaces, Helm charts, desired state vs. actual state, self-healing, GitOps.
- **Gate check:** Airflow runs on local Kubernetes; delete a pod on purpose → it comes back by itself; a change merged to Git is applied by Argo CD automatically.
- 🍽️ Moving from one kitchen to a restaurant chain with a central operations manual.
