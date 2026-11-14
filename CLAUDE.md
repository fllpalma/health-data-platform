# CLAUDE.md — Personal Health Data Platform (learning project)

## What this project is
An end-to-end data platform built on my own Apple Health export, from raw data to ML models, automations and LLM agents.
It is a **learning project**: the goal is that I understand every piece, not just that it works.

## Who I am (adapt everything to this)
- I manage a Data & AI team. I am **not a computer scientist**.
- I want end-to-end visibility of how real data teams work: foundations → pipelines → ML → automations → LLMs.
- Explain in **simple terms**, with **analogies and real-world examples**. Define every technical term the first time it appears and add it to `docs/GLOSSARY.md`.
- Running analogy for the whole project: **a restaurant** (deliveries = ingestion, pantry = data lake, prep chefs with recipes = dbt, head chef's schedule = Airflow, order-ticket rail = Kafka, kitchen wall screen = Grafana, food truck = Lambda, kitchen assistant = n8n, sous-chef you can ask questions = LLM agent). Reuse it so the pieces connect.

## Golden rules
1. **Sequential, one phase at a time.** Only work on the CURRENT PHASE (below). Never create folders, files, services or dependencies for later phases. If something from a later phase would help, mention it in one line and move on.
2. **Free tools only.** Nothing paid except Claude. Before adding any tool or cloud service, confirm it is free for personal use and say so. Never create AWS resources outside the always-free tier; always have a budget alert and a teardown path.
3. **Do it like a real company.** Git branches + pull requests, conventional commits, tests, CI, infrastructure as code, documented decisions. When there's a "toy" way and a "company" way, use the company way and explain the difference briefly.
4. **Privacy.** My health data is sensitive.
   - Raw data NEVER goes into Git (`data/` and export files are gitignored; check before every commit).
   - Raw data stays on my Mac. Anything deployed to AWS uses synthetic sample data only.
   - LLMs run locally via Ollama only.
5. **Teach before you build.** For each step: what we'll do → why real teams do it → analogy → then do it → one-line recap. **Claude does all the typing** (code, commands, git, GitHub); I don't write code. Instead, pause after each meaningful step, show the key line and what it means, and check my understanding with a quick question.
6. **Ask before big moves.** Before installing tools, creating many files, or changing architecture, show a short plan and wait for my OK.
7. **Be credit-aware.** Keep explanations short by default; I'll say "go deeper" when I want more. Don't re-read or regenerate files unnecessarily.

## My machine
- MacBook M4 (Apple Silicon, arm64), 24 GB RAM.
- Docker (Docker Desktop or OrbStack) limited to ~12 GB. Use Docker Compose **profiles** so only the current phase's services run.
- Ollama runs natively on macOS (not in Docker) to use the GPU.

## Phases (full detail in `docs/PLAN.md`)
0. Setup — tools, GitHub repo, Docker, project skeleton
1. Foundations — ingest Apple Health export into a data lake (SeaweedFS, S3-compatible) + warehouse (Postgres)
2. Transformations — dbt models + tests
   - 2b. Snowflake sprint (optional, 30-day trial) — same dbt project on Snowflake
3. Orchestration — Airflow + CI on GitHub Actions and Jenkins (comparison)
4. Streaming — Kafka
5. Observability & lineage — Prometheus, Grafana, OpenLineage/Marquez
6. ML — model + MLflow → FastAPI → AWS Lambda (OpenTofu, GitHub Actions deploy)
7. Automation — n8n
8. LLMs — Ollama, LangChain/LangGraph, pgvector, Langfuse
9. Kubernetes & GitOps (required) — kind + Helm, Argo CD

## CURRENT PHASE: 3 — Orchestration
(Update this line when a phase gate is passed.)

## Phase gate (must pass before moving on)
- [ ] It works — I ran the check myself and saw the result
- [ ] Tested and merged to `main` via a pull request
- [ ] `docs/LEARNINGS.md` updated: what we built, why, analogy
- [ ] I answered 3 recap questions in plain words

## Conventions
- Language: Python 3.12+, managed with `uv`.
- Branches: `phase-N/short-description`. Commits: conventional (`feat:`, `fix:`, `docs:`, `chore:`).
- Secrets in `.env` (gitignored); provide `.env.example`.
- Docs live in `docs/`: `PLAN.md`, `GLOSSARY.md`, `LEARNINGS.md`, `adr/` (architecture decision records).
