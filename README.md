# Personal Health Data Platform

A learning project: an end-to-end data platform built on my own Apple Health export,
from raw data → pipelines → ML → automations → LLM agents, built the way real data teams work.

> 🔒 **Privacy:** raw health data never enters Git and never leaves this Mac.
> See `.gitignore`. Anything deployed to the cloud uses synthetic data only.

## Status
Current phase: **3 — Orchestration**. Full roadmap: [docs/PLAN.md](docs/PLAN.md)

## Prerequisites (macOS, Apple Silicon)
| Tool | Purpose |
|---|---|
| Homebrew | Installs developer tools |
| Git + GitHub CLI (`gh`) | Version control + GitHub from the terminal |
| Docker Desktop (memory capped at ~12 GB) | Runs services in containers |
| `uv` | Python versions + project dependencies |
| `pre-commit` (`uv tool install pre-commit`) | Automatic checks before every commit |

## Getting started
```bash
git clone https://github.com/fllpalma/health-data-platform.git
cd health-data-platform
pre-commit install          # switch on the automatic checks for this copy
cp .env.example .env        # then fill in real values (never commit .env)
docker compose --profile foundations up -d --wait   # Phase 1: start the lake + warehouse
```

## How we work
- Branches: `phase-N/short-description`. `main` is protected: changes only via pull request.
- Commits: [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `chore:`).
- Decisions are recorded in [docs/adr/](docs/adr/). Terms are explained in [docs/GLOSSARY.md](docs/GLOSSARY.md).
