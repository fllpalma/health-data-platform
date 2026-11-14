# 4. De-duplicate activity by keeping the highest single source per hour

- **Date:** 2026-11-14
- **Status:** Accepted. ⏳ Owner validation against the Health app pending (part of the Phase 2 gate).

## Context
Several devices record the same activity: 3 iPhones, 1 Apple Watch and 4 other apps/devices since 2020.
Profiling (counts only) showed 41% of hours with steps from more than one device class, and a **+28.1% inflation**
if all sources are simply summed. There were also **852 exact duplicate records** (0.03%).

Options considered:
| Option | Trade-off |
|---|---|
| A. One source per day (Watch if worn, else iPhone) | Simple, but undercounts days the Watch was removed midway |
| **B. Hourly maximum of per-source totals** ✅ | Close to Apple's own merging; simple to explain and test |
| C. Minute-level source-priority merge | Most accurate, but complex and hard to test |

## Decision
1. **Exact duplicates:** keep one copy per content-based `record_id` (`int_apple_health__records_deduplicated`).
2. **Overlapping sources** for cumulative metrics (steps, walking/running distance, active energy, exercise minutes, flights):
   per local hour, sum each source separately, keep the **highest** source total (`int_apple_health__activity_hourly`).

## Consequences
- ✅ Removes the double counting; one documented, tested definition of "steps per hour/day".
- ✅ When the phone is left on a desk, the Watch's higher count wins (max, not average).
- ➖ Approximation: a record spanning two hours is assigned to its start hour; small differences vs the Health app are expected.
- ➖ Non-cumulative metrics (heart rate, sleep) need their own rules (later PRs).
