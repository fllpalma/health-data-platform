# 1. Record architecture decisions

- **Date:** 2026-11-14
- **Status:** Accepted

## Context
This project will make many technical choices (which database, which orchestrator, where to deploy).
Months later, nobody remembers *why* a choice was made, so people either re-argue it or are afraid to change it.

## Decision
We record every significant decision as a short, numbered Architecture Decision Record (ADR)
in `docs/adr/`, using this format: Context → Decision → Consequences.
ADRs are never deleted. If a decision changes, a new ADR *supersedes* the old one.

## Consequences
- ✅ Anyone (including future me) can see why the platform looks the way it does.
- ✅ Changes to decisions are deliberate and reviewed in a pull request like code.
- ➖ Small overhead: a few minutes of writing per decision.
