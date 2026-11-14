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
   - My answer: _(pending)_
   - Model answer: `.gitignore` (Git never even sees data files by name) + pre-commit large-file check (blocks big files with names `.gitignore` didn't predict). Two layers, because any single safety net eventually has a gap.
2. *Why a branch + pull request instead of changing `main` directly?*
   - My answer: _(pending)_
   - Model answer: `main` must always be the trustworthy version. Work happens on a side counter (branch) and only enters the official recipe book after review and checks (PR), leaving a record of what changed and why.
3. *What is a container, and why will Phase 1 need them?*
   - My answer: _(pending)_
   - Model answer: a sealed box that runs a piece of software the same way on any machine. Phase 1 needs a database (Postgres) and a data lake (MinIO); containers let us run them on the Mac without messy installs, and remove them cleanly.
