# 6. Portable SQL: one dbt project for Postgres and Snowflake

- **Date:** 2026-11-14
- **Status:** Accepted

## Context
Phase 2b runs the same dbt project on Snowflake (trial; **synthetic data only**, enforced in code by a guardrail
that refuses real exports for any destination other than local Postgres). The first `dbt build --target snowflake`
failed on Postgres-only SQL, and a parity test later found a **silent** precision bug.

| Difference found | Postgres | Snowflake | Fix (portable) |
|---|---|---|---|
| Conditional aggregates | `sum(x) filter (where …)` | ❌ syntax error | `sum(case when … then x end)` |
| Seconds between timestamps | `extract(epoch from b - a)` | ❌ invalid `epoch` | `dbt.datediff(a, b, "second")` (cross-database macro) |
| Merging overlapping intervals | `range_agg(tsrange(…))` | ❌ doesn't exist | "gaps and islands" with standard window functions |
| Adding hours | `ts + interval '6 hours'` | works, but differs elsewhere | `dbt.dateadd("hour", 6, ts)` |
| **Bare `numeric`** | keeps all decimals | **NUMBER(38,0) = no decimals** (silent!) | explicit `numeric(38, 10)` |
| `round(x, 2)` after `dbt.datediff` | needs `numeric`, not float | fine | `cast(… as dbt.type_numeric())` |
| `select * exclude (…)` | ❌ doesn't exist | works | list columns explicitly (found in Phase 2) |

## Decision
1. Prefer **portable SQL** (standard SQL + dbt cross-database macros). Use `adapter.dispatch` only when no portable form exists.
2. Always give numeric casts an **explicit precision and scale**.
3. A migration is accepted only after a **regression test** (old vs new SQL on the same warehouse) and a
   **parity test** (same input on both warehouses), with an agreed tolerance.

## Results
- `dbt build`: 35/35 on Postgres (real data) and 35/35 on Snowflake (synthetic).
- Parity on synthetic data: all gold rows identical across warehouses.
- Regression on real data (Postgres): identical, except ≤ 1 minute rounding on 5 of 1,529 nights
  (summing seconds before dividing is more precise than dividing each piece). Tolerance: ±1 minute.

## Consequences
- ✅ One codebase, two warehouses; the migration path to Snowflake is proven.
- ✅ The silent `NUMBER(38,0)` truncation would have corrupted distance and HRV with no error: caught only by parity testing.
- ➖ Gaps-and-islands SQL is longer than `range_agg`. Worth it for portability.
