# Learnings

One section per phase, written at the phase gate: what we built, why, and the analogy, in my own words.

## Phase 0 — Setup (2026-11-14)

- **What we built:** a professional workspace. Tools checked or installed (Homebrew, Git, `gh`, Docker capped at 12 GB, `uv`, `pre-commit`); a public GitHub repo with `main` locked (changes only via pull request); a skeleton with README, `.gitignore`, `.env.example`, glossary, learnings, the first ADR, and pre-commit checks. First PR (#1) merged.
- **Why real teams do it:** rules that are automatic don't depend on people remembering. Privacy locks, quality checks and review steps set up *before* data arrives are cheap; fixing a leak afterwards is very hard.
- **🍽️ Analogy:** fitting out the kitchen before the first meal: fridges installed and sized (Docker), a hygiene inspector at the door (pre-commit), a "customer files never leave" sign (`.gitignore`), and an official recipe book only the head chef can change (protected `main` + PRs).
- **What surprised me / what broke:**
  - Docker Desktop closed during "Apply & restart". The `docker` command is only a remote control; with the engine off, it can't connect.
  - In `.gitignore`, `#` only starts a comment at the *start* of a line. A side comment silently breaks the rule, which is why we **test** safety rules instead of trusting them.
  - GitHub's free plan only enforces branch locks on public repos. We went public **after** auditing the history and replacing my email with GitHub's no-reply address.
  - Plan changes: Jenkins added to Phase 3 (CI comparison); Kubernetes (Phase 9) made required.

### Recap questions
1. *Two locks keep health data out of GitHub: what and why two?*
   - My answer: _waived: accepted the model answer below_
   - Model answer: `.gitignore` (Git never even sees data files by name) + pre-commit large-file check (blocks big files with names `.gitignore` didn't predict). Two layers, because any single safety net eventually has a gap.
2. *Why a branch + pull request instead of changing `main` directly?*
   - My answer: _waived: accepted the model answer below_
   - Model answer: `main` must always be the trustworthy version. Work happens on a side counter (branch) and only enters the official recipe book after review and checks (PR), leaving a record of what changed and why.
3. *What is a container, and why will Phase 1 need them?*
   - My answer: _waived: accepted the model answer below_
   - Model answer: a sealed box that runs a piece of software the same way on any machine. Phase 1 needs a database (Postgres) and a data lake (MinIO); containers let us run them on the Mac without messy installs, and remove them cleanly.

## Phase 1 — Foundations (2026-11-14)

- **What we built:** a local data lake (SeaweedFS, S3-compatible) and warehouse (Postgres 18) in Docker Compose; a streaming parser for the Apple Health export; a pipeline that stores the original zip in the lake and loads ~3 million records into `raw_apple_health.records` with dlt in under 2 minutes; CI on GitHub Actions, required before merging. 4 PRs (#3–#6), 14 tests.
- **Why real teams do it:**
  - **Lake + warehouse:** the untouched original lets you rebuild after any bug, and the warehouse makes it queryable.
  - **Streaming:** real files are too big to load at once (19 MB vs 1,274 MB on 1M records).
  - **Idempotency:** pipelines get re-run (failures, retries). Re-running must never duplicate.
  - **CI:** local checks can be skipped; the independent check on GitHub can't.
- **🍽️ Analogy:** deliveries arrive at the back door (ingestion), go into the pantry sealed and labelled by date (lake), then get unpacked jar by jar onto shelves (warehouse). An inspector at the pass (CI) checks every change before it reaches the official recipe book.
- **What surprised me / what broke:**
  - **MinIO** (the original plan) was archived in 2026, so we chose **SeaweedFS** (ADR 0002). Real AWS S3 was ruled out by my privacy rule and AWS's new credit-based free tier.
  - My iPhone named the file **`exportação.xml`**, not `export.xml`, and inside the zip the name arrived **garbled** (`exportac╠ºa╠âo.xml`). The code never relies on the file name, and the garbled name is now a test case.
  - The export has much more than steps: 70 record types from 36 sources, plus GPS routes and ECGs (very sensitive, kept in the lake only).
  - **Raw = as delivered:** values stay text and iPhone + Watch double-count steps. Cleaning and de-duplicating are Phase 2's job (dbt).
  - **Privacy in practice:** health values are only viewed locally (VS Code), never printed into the AI chat; dlt telemetry is off.

### Recap questions
1. *Why keep the original zip in the lake when the data is already in Postgres?*
   - My answer: _(pending)_
   - Model answer: it's the untouched original. If a parsing or loading bug is found later, we fix the code and rebuild the tables from the zip, with no need to re-export from the iPhone. It also proves exactly what was received.
2. *What does idempotent mean, and how did we prove it?*
   - My answer: _(pending)_
   - Model answer: running it twice gives the same result as once. We ran the full pipeline twice: the row count stayed at ~3.06M and the lake still had exactly one file.
3. *The Mac already runs checks before each commit. Why also run them in CI?*
   - My answer: _(pending)_
   - Model answer: local checks can be skipped or misconfigured on one laptop. CI runs on a clean machine for every PR, can't be skipped, and is required before merging, so it's the independent, trusted check.
