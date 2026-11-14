# Glossary

Plain-language definitions, added the first time each term appears. 🍽️ = restaurant analogy.

## Phase 0 — Setup

| Term | Plain meaning | 🍽️ |
|---|---|---|
| **Terminal / CLI** | A text window where you type commands instead of clicking. CLI = command-line interface. | Shouting orders through the kitchen hatch |
| **Homebrew** | An "app store" for developer tools on macOS, used from the terminal. | The supplier catalogue |
| **Git** | Records every version of your files: what changed, who, when, why. | The kitchen logbook |
| **Repository (repo)** | A project folder tracked by Git, including its full history. | The recipe book + its logbook |
| **Commit** | One saved, labelled snapshot of changes in Git. | One signed, dated logbook entry |
| **Branch** | A separate line of work, so changes don't touch the official version until approved. | Trying a recipe on a side counter |
| **`main`** | The official branch, which always holds approved, working code. | The official recipe book |
| **GitHub** | A website that hosts Git repos and lets teams review changes. | The head office holding the master copy |
| **`gh` (GitHub CLI)** | Controls GitHub from the terminal (create repos, open PRs). | Phoning head office instead of visiting |
| **Pull request (PR)** | A request to merge a branch into `main`, reviewed and checked first. | Submitting a new recipe for the head chef's approval |
| **Branch protection** | A rule on GitHub forbidding direct changes to `main`. Only PRs allowed. | Only the head chef can edit the official book |
| **Conventional commits** | A naming convention for commit messages (`feat:`, `fix:`, `docs:`, `chore:`). | Standard labels on every logbook entry |
| **`.gitignore`** | A list of files Git must never track (data, secrets, junk). | "Customer files: never leave the building" sign |
| **Secret / `.env`** | Passwords and keys kept in a local `.env` file that Git ignores. `.env.example` lists the names only. | The key rack: real keys locked away, labels on display |
| **Docker** | Runs software in sealed, identical boxes on any machine. | Standardised fridges that work in any kitchen |
| **Container** | One running sealed box (e.g. a database). | One fridge, switched on |
| **Image** | The blueprint a container is started from. | The fridge model in the catalogue |
| **Docker engine (daemon)** | The background program that actually runs containers. The `docker` command is just a remote control talking to it through a *socket*. | The power supply behind the fridges |
| **Docker Compose** | One file describing several containers that run together. | The kitchen floor plan |
| **`uv`** | Installs Python versions and each project's libraries, fast and isolated. | The pantry manager |
| **Dependency** | An external library your code relies on. | A bought-in ingredient |
| **pre-commit / hook** | Automatic checks that run before every commit. A *hook* is one check. | The hygiene inspector at the door |
| **ruff** | A fast tool that checks (lint) and tidies (format) Python code. | The inspector checking knife cuts are uniform |
| **Lint** | Automatically spotting bugs and style problems in code without running it. | Proofreading a recipe before cooking it |
| **ADR** | Architecture Decision Record: a short note on a decision and why it was made. | "Why we chose this oven" note in the binder |
| **CI/CD** | Continuous integration / delivery: a robot that tests (and ships) every change automatically. | The quality check before each dish leaves the pass |
| **GitHub Actions** | GitHub's hosted CI/CD service (Phase 1+). | Hired cleaning service |
| **Jenkins** | Self-hosted CI/CD server, common in enterprises (Phase 3). | Your own cleaning crew |
| **Kubernetes (K8s)** | Runs and self-heals many containers across machines (Phase 9). | Operations manager of a restaurant chain |
| **Staged** | Files queued for the next commit (`git add`). | Ingredients laid out on the counter, ready to cook |
| **Push / pull** | Upload your commits to GitHub / download others' commits from it. | Sending the logbook to head office / collecting the latest copy |
| **Merge (squash merge)** | Bringing a branch's changes into `main`. *Squash* combines them into one clean commit. | Signing the approved recipe into the official book as one entry |
| **Rewriting history (rebase / amend)** | Re-saving existing commits, e.g. to fix the author email. Safe only before anyone else has a copy. | Re-writing a logbook page before anyone has photocopied it |
| **Ruleset** | GitHub's server-side rules for a branch (e.g. "PR required, no deleting `main`"). Free on public repos. | The lock on the official recipe book |
| **No-reply email** | A private GitHub address used in commits so your real email isn't public. | Signing the logbook with your staff number, not your home address |
| **Public vs. private repo** | Public = anyone can read the code; private = only invited people. Data safety comes from the locks, not visibility. | A glass-walled kitchen: people see the cooking, never the customer files |

## Phase 1 — Foundations

| Term | Plain meaning | 🍽️ |
|---|---|---|
| **Ingestion** | Bringing data from its source (your iPhone export) into the platform. | Deliveries arriving at the back door |
| **Data lake** | Storage for raw files kept exactly as they arrived, so you can always rebuild from the originals. | The pantry: labelled, unopened boxes |
| **Data warehouse** | A database organised into tables, built for asking questions (Postgres here). | Organised shelves the chefs can reach |
| **Table** | Data in rows and columns, like a spreadsheet (e.g. one row per step-count reading). | One shelf of identical jars |
| **Postgres (PostgreSQL)** | A free, open-source, very widely used database. | The shelving system |
| **S3** | Amazon's file-storage service. Its *API* became the industry standard for data lakes. | The big supplier's warehouse standard |
| **API** | The agreed set of commands programs use to talk to a service. | The order form a supplier accepts |
| **S3-compatible** | Any storage that understands S3's API, so code written for S3 works unchanged. | A pantry built to the supplier's standard |
| **SeaweedFS** | The free, S3-compatible storage we run locally as our lake (replaced MinIO, see ADR 0002). | Our pantry |
| **Bucket** | A top-level folder in S3 (ours: `raw`). | One pantry room |
| **Access key / secret key** | S3's username / password. The secret is never sent itself; a *signature* calculated from it is. | Staff ID + PIN |
| **Port** | A numbered "door" on a computer that a service listens on (Postgres: 5432). `127.0.0.1` = only this Mac can use it. | The kitchen's door number; internal-only doors |
| **Volume** | Storage that lives outside a container, so data survives restarts and rebuilds. | Fridge contents survive swapping the fridge |
| **Pinned version** | An exact version number (`postgres:18.7`), so every install is identical. | "Barilla No. 5", not just "pasta" |
| **Healthcheck** | A small automatic test Docker runs to know whether a service is really working. | Checking the fridge is actually cold |
| **Smoke test** | A quick "does it basically work?" check after starting something. | Tasting the sauce before service |
| **Database client** | A program that connects to a database so you can browse and query it (VS Code PostgreSQL extension). | The window into the cold room |
