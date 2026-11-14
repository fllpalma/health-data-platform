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
| **XML** | A text format where data sits inside labelled tags, like `<Record value="412"/>`. Apple's export uses it. | Every jar wrapped and labelled |
| **Parser** | Code that reads a file format and turns it into structured records. | The person unpacking boxes and reading labels |
| **Streaming (parsing)** | Reading a file piece by piece instead of loading it all into memory (19 MB vs 1,274 MB in our test). | Unloading one box at a time onto a conveyor belt |
| **Generator** | Python code that hands out items one at a time, only when asked. This is what makes streaming possible. | A conveyor belt that moves only when you take a jar |
| **Raw layer** | Data stored exactly as delivered: no cleaning, values kept as text. Cleaning happens later (dbt). | Unopened deliveries |
| **Test / pytest** | Code that checks other code automatically; `pytest` runs all of them. | Tasting every dish against the recipe card |
| **Test fixture** | Fake sample data used by tests (our synthetic `export_sample.xml`). | A plastic display dish used for training |
| **TDD** | Test-driven development: write the test first (it fails = red), then the code (it passes = green). | Agreeing how the dish must taste before cooking |
| **Virtual environment (`.venv`)** | A project's private set of Python libraries, isolated from the rest of the Mac. | Each kitchen station's own spice rack |
| **Lockfile (`uv.lock`)** | Exact versions of every library, so every machine installs identical ones. | The exact brand list for every ingredient |
| **dlt** | A free Python library that loads data into databases: creates tables, handles batches. | The porter moving jars onto shelves |
| **boto3** | Amazon's official Python library for S3 (works with our S3-compatible lake). | The pantry's standard order form |
| **Idempotent** | Running something twice gives the same result as once: no duplicates. | Restocking a shelf to "10 jars", not "add 10 jars" |
| **Full snapshot / replace** | Each export contains your whole history, so each load replaces the table entirely. | Swapping the whole shelf for this week's complete delivery |
| **Object key / partition** | A file's full "path" in the lake. `export_date=2026-11-14/` organises files by date. | Shelf label with the delivery date |
| **Text encoding** | How letters become bytes. A mismatch garbles names like `exportação` → `exportac╠ºa╠âo`. | A label written in an alphabet the reader doesn't know |
| **Telemetry** | Usage statistics a tool sends home to its makers. We switched dlt's off. | A supplier asking for reports on how you use their goods |

## Phase 2 — Transformations

| Term | Plain meaning | 🍽️ |
|---|---|---|
| **dbt** | A tool where each table is a SQL "recipe" (model). It runs them in order, tests the results and documents them. | The prep chefs and their recipe cards |
| **Model (dbt)** | One SQL `select` that defines one table or view. | One recipe card |
| **Source (dbt)** | A raw table dbt reads from but doesn't create (our `raw_apple_health.records`). | The delivery dbt starts from |
| **Adapter** | The plug that lets dbt talk to a specific database (Postgres now, Snowflake in 2b). | The adapter that lets one appliance work in any kitchen |
| **Profile** | dbt's connection settings (`profiles.yml`), secrets read from `.env`. | The kitchen's address and door code |
| **Staging layer** | First clean-up: real types, clear names, 1 model per source. No business logic. | Wash and cut |
| **Intermediate layer** | Business logic: de-duplication, combining sources. | Combining prepared ingredients |
| **Mart** | Final, ready-to-use tables for people and dashboards (e.g. one row per day). | The plated dish |
| **Schema (database)** | A folder inside a database grouping tables (`raw_apple_health`, `staging`, `marts`). | Separate cold rooms per station |
| **View vs table** | A *view* is a saved query that runs when read; a *table* stores the results. | A recipe vs. a dish already cooked and waiting |
| **Materialization** | How dbt builds a model: as a view, a table, or incrementally. | Cook to order vs. batch-cook in advance |
| **Data test** | An automatic check on the data itself (not null, unique, accepted values, custom rules). | The taster checking every dish |
| **Surrogate key** | An ID we compute (e.g. `md5` of the record's fields) when the data has no reliable ID. | A barcode we print on unlabelled jars |
| **md5 / hash** | A function that turns any text into a fixed-length fingerprint; same input → same fingerprint. | A fingerprint for each jar |
| **Time zone (UTC vs local)** | UTC is one global clock; *local* is the wall-clock where you were. Daily tables use local days. | Head office clock vs. the kitchen clock |
| **Data profiling** | Looking at what's actually in the data (kinds, units, nulls) before modelling it. | Checking the delivery before writing the menu |
| **Duplicate (exact vs overlapping)** | Exact = the same record twice; overlapping = different devices recording the same event. | The same jar delivered twice vs. two suppliers sending the same item |
| **Medallion architecture** | Layer naming used in lakehouse/Databricks teams. Ours: 🥉 bronze = `raw_apple_health` (untouched), 🥈 silver = `staging` + `intermediate`, 🥇 gold = `marts`. | Sealed boxes → prepped ingredients → plated dish |
| **SQL dialect** | Each database's own flavour of SQL (e.g. Snowflake's `select * exclude` doesn't exist in Postgres). | Same cuisine, regional recipe differences |
| **Window function (`row_number`)** | Numbers rows within groups without collapsing them, used to keep "copy #1" of each duplicate. | Numbering identical jars on a shelf to keep just the first |
| **Data validation / sign-off** | A business owner confirms a metric matches reality (here: Health app) before it becomes official. | The head chef tasting before the dish goes on the menu |
| **Business rule** | A decision about what the data *means* (e.g. "a night belongs to the morning you wake up"), agreed with the data owner. | House rules for how a dish is portioned |
| **Data-quality rule** | A rule that excludes or flags data that can't be true (e.g. in bed > 16 h). Applied in silver; bronze is untouched. | Binning a jar with a broken seal, while keeping the delivery note |
| **Plausibility / range test** | A test that values fall within realistic limits (our custom `in_range`). It caught 3 real data problems. | "Soup served between 60 and 85 °C" |
| **Overlapping intervals** | Time records that cover the same minutes. Measure the time *covered*, don't add up records. | Tape strips on a ruler: measure the covered length, not the sum of strips |
| **Lineage graph** | The map of which table is built from which (dbt docs). | The family tree of every dish back to its deliveries |
| **Integration test** | Tests that the pieces work *together* end to end (pipeline + lake + warehouse + dbt), not each piece alone. | A full dress rehearsal of service |
| **Synthetic data** | Invented data with the same shape and traps as the real thing. Safe to use anywhere (CI, cloud, demos). | Plastic food for the rehearsal |
| **Deterministic** | Same input → identical output every run (our generator uses a fixed random seed). | A recipe that always yields the same dish |
| **Data contract** | A fixed, declared table shape (columns + types) that doesn't change with whatever data arrives. Found missing via the CI rehearsal. | Labelled shelf slots that stay even when empty |
| **Schema inference** | A tool guessing table columns from the data it sees. Convenient, but the shape can silently change. | Building shelves to fit whatever came in this week |
| **sqlfluff** | A style checker/fixer for SQL (like ruff for Python). | The inspector checking every recipe card follows the house format |
| **Service container (CI)** | A throwaway database started next to a CI job, deleted afterwards. | A rented rehearsal kitchen, cleared after use |

## Phase 2b — Snowflake sprint

| Term | Plain meaning | 🍽️ |
|---|---|---|
| **Snowflake** | A cloud data warehouse: you pay per second a "warehouse" (compute) runs, plus storage. | A rented professional kitchen with a meter on the stove |
| **Virtual warehouse** | Snowflake's compute engine, sized X-Small → 6X-Large. Separate from storage. Ours: X-Small, auto-suspend 60 s. | The stove: bigger = faster = pricier per minute |
| **Credit** | Snowflake's billing unit. X-Small uses 1 credit per running hour (billed per second, 60 s minimum). | Coins in the stove's meter |
| **Auto-suspend / auto-resume** | The warehouse switches off after idle time and on again when a query arrives. Most of cost control. | A stove that turns itself off when nobody's cooking |
| **Resource monitor** | A hard credit cap that notifies and then suspends warehouses. Our budget alarm. | A prepaid meter that cuts the gas at the limit |
| **Service user / key-pair auth** | A robot account that logs in with a private key (on the Mac) matching a public key (in Snowflake). No password. | A staff badge that only opens the back door |
| **Target (dbt)** | One named connection in `profiles.yml` (`local` = Postgres, `snowflake`). Same project, `--target` picks the warehouse. | Same recipes, choose which kitchen cooks them |
| **Cross-database macro** | A dbt helper (e.g. `dbt.datediff`) that writes the right SQL for each warehouse. | A recipe step written so any kitchen's equipment can do it |
| **Portable SQL** | SQL that runs unchanged on several databases. | A recipe that works in any kitchen |
| **Regression test** | Compare results before vs after a change: same input, same output? | Taste the dish after changing the method: still the same? |
| **Parity test** | Same input on two systems: identical output? Caught a silent precision bug. | Cook the same recipe in two kitchens, compare the plates |
| **Precision / scale** | Total digits / digits after the decimal point. `numeric(38,10)` = up to 10 decimals. | How finely the scale weighs |
| **Gaps and islands** | A standard SQL technique to merge overlapping time ranges using window functions. | Joining overlapping tape strips into continuous pieces |
| **Guardrail** | Code that makes the unsafe action impossible (refuses real data for Snowflake). | A lock on the door that customer files can't pass |
| **Infrastructure as code (Snowflake)** | `snowflake/setup.sql` + `teardown.sql`: reviewable, repeatable, reversible setup. | The written rental agreement, plus the move-out checklist |

## Phase 3 — Orchestration

| Term | Plain meaning | 🍽️ |
|---|---|---|
| **Orchestrator (Airflow)** | Software that runs pipeline steps in the right order, on time or on events, with retries and a history of every run. | The head chef's schedule |
| **DAG** | "Directed acyclic graph": a flowchart of tasks with arrows for "this before that", never looping back. | The order of prep for a dish |
| **Task** | One step in a DAG (e.g. "load the export", "build daily_sleep"). | One line on the prep list |
| **Executor (Local/Celery/Kubernetes)** | *Where* tasks run: inside the scheduler (Local), on worker machines (Celery), or as pods (Kubernetes). | Who actually cooks: the head chef, a brigade, or a chain of kitchens |
| **Scheduler** | The Airflow component that decides what runs when. | The head chef watching the clock |
| **API server / UI** | Airflow's web screen and API, showing every run, task and log. | The board on the office wall |
| **DAG processor** | Reads DAG files and keeps their definitions current. | The person who files new schedules |
| **Triggerer** | Waits efficiently for external events without blocking a worker. | A doorbell instead of someone staring at the door |
| **Metadata database** | Airflow's own database of runs and states (separate from our warehouse). | The kitchen's logbook of who cooked what, when |
| **Docker image / Dockerfile** | An image is a ready-to-run package; a Dockerfile is the recipe to build it. We extend the official Airflow image. | A pre-fitted kitchen unit, built from a fitting plan |
| **Fernet key** | A secret Airflow uses to encrypt stored passwords/connections. | The key to the kitchen safe |
| **Cosmos** | A free add-on that turns each dbt model into its own Airflow task. | Splitting "make dinner" into one ticket per dish |
| **YAML anchor (`&` / `*`)** | Define a block once (`&name`) and reuse it (`*name`) in a YAML file. | A standard fitting spec reused for every station |
