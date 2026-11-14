# 2. Local S3-compatible data lake with SeaweedFS (not MinIO, not AWS S3)

- **Date:** 2026-11-14
- **Status:** Accepted

## Context
Phase 1 needs a data lake: a place to store the raw Apple Health export exactly as delivered.
The industry standard interface for this is **Amazon S3**. Options considered:

| Option | Why not (or why) |
|---|---|
| **AWS S3 (real cloud)** | Breaks privacy rule 4 (raw data stays on my Mac). Also no longer reliably free: since July 2025, new AWS accounts get time-limited credits instead of a 12-month S3 allowance. |
| **MinIO** (original plan) | Community edition stopped publishing binaries/Docker images (Oct 2025) and the repository was archived (Apr 2026). Community forks exist but are unofficial and unaudited. |
| **RustFS** | MinIO-like UI, but a young project. |
| **Garage** | Lightweight, but no proper browser UI (less useful for learning). |
| **SeaweedFS** ✅ | Mature (10+ years), Apache-2.0, actively maintained, official Docker image, `mini` mode built for small/dev setups, includes an admin UI. |

## Decision
Run **SeaweedFS 4.53** (`weed mini`) locally in Docker Compose (profile `foundations`) as the data lake,
accessed **only through the standard S3 API** with standard credential names (`AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`).

Verified before deciding: anonymous requests → `AccessDenied`; wrong secret → `SignatureDoesNotMatch`; correct key → read/write OK.

## Consequences
- ✅ Raw health data never leaves the Mac. Ports are bound to `127.0.0.1` only.
- ✅ Code is written against the S3 API, so switching to real S3 later (Phase 6, synthetic data only) is a configuration change, not a rewrite.
- ✅ Free, with no account or credit card needed.
- ➖ SeaweedFS's admin UI is plainer than MinIO's.
- ➖ Not identical to AWS S3 in edge cases (e.g. some IAM policy features). Acceptable for a single-user dev lake.
