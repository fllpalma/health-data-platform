# 5. Sleep: night assignment, best source per night, and data-quality rules

- **Date:** 2026-11-14
- **Status:** Accepted. ⏳ Owner validation against the Health app pending (part of the Phase 2 gate).

## Context
Sleep crosses midnight, comes from several sources, and profiling (counts only) showed:
- the Watch recorded sleep on only ~9–13 nights; a third-party sleep app recorded ~800 nights (stages on ~84);
  the iPhone records only "in bed" from the bedtime schedule;
- overlapping records **within** a source (summing inflated in-bed time by 10.5%);
- implausible "in bed" records of 16–24+ hours from one app (100 records): an app glitch.
The marts' `in_range` tests (in-bed ≤ 24 h) caught the last two.

## Decision
1. **Night rule:** sleep starting between 18:00 on day D-1 and 18:00 on day D belongs to **day D** (the morning you wake up).
2. **Best source per night:** the source with the most time asleep (ties → most time in bed). In-bed time uses the
   best in-bed source that night (often the iPhone).
3. **Covered time, not summed records:** overlapping segments are merged before measuring (Postgres `range_agg`).
4. **Plausibility rule:** in-bed records longer than **16 h** are excluded in the silver layer (bronze untouched).
5. **Stand hours:** distinct clock hours (two Watches reported the same hours: 1,395 duplicates).

## Consequences
- ✅ No impossible values; definitions are explicit, tested and reviewable.
- ➖ `range_agg` is Postgres-specific: Phase 2b (Snowflake) needs an equivalent.
- ➖ The 16 h threshold is a judgement call; change it in `int_apple_health__sleep_segments` (one variable).
