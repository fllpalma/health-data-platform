-- 🥇 One row per night (dated by the morning you wake up).
-- Overlapping sources: per night, use the source that recorded the most sleep (same idea as ADR 0004).
-- Overlapping records WITHIN a source: measure time actually covered (merge overlaps), don't add up records.
--   Found by the in_range test: summing inflated in-bed time by 10.5% (58 nights > 24 h).
-- Portable SQL (Postgres + Snowflake): overlaps are merged with the classic "gaps and islands" technique
-- (window functions only), replacing the Postgres-only range_agg used before Phase 2b.

with segments as (

    select
        sleep_date,
        source_name,
        stage_group,
        start_at_local,
        end_at_local
    from {{ ref('int_apple_health__sleep_segments') }}
    where stage_group in ('asleep', 'awake', 'in_bed')

),

with_previous_end as (

    -- For each segment: the latest end time among all EARLIER segments (same night/source/stage group)
    select
        *,
        max(end_at_local) over (
            partition by sleep_date, source_name, stage_group
            order by start_at_local, end_at_local
            rows between unbounded preceding and 1 preceding
        ) as previous_max_end
    from segments

),

islands as (

    -- A new "island" starts when a segment begins after everything before it has ended (a gap)
    select
        *,
        sum(case when previous_max_end is null or start_at_local > previous_max_end then 1 else 0 end) over (
            partition by sleep_date, source_name, stage_group
            order by start_at_local, end_at_local
            rows between unbounded preceding and current row
        ) as island_id
    from with_previous_end

),

merged as (

    -- One row per island = one continuous stretch of time, overlaps removed
    select
        sleep_date,
        source_name,
        stage_group,
        island_id,
        min(start_at_local) as island_start,
        max(end_at_local) as island_end
    from islands
    group by 1, 2, 3, 4

),

covered_minutes as (

    select
        sleep_date,
        source_name,
        stage_group,
        cast(
            sum({{ dbt.datediff("island_start", "island_end", "second") }}) as {{ dbt.type_numeric() }}
        ) / 60.0 as minutes,
        min(island_start) as first_start,
        max(island_end) as last_end
    from merged
    group by 1, 2, 3

),

stages as (

    -- Stage detail (Core/Deep/REM): a breakdown only, summed per stage
    select
        sleep_date,
        source_name,
        sum(case when stage = 'AsleepCore' then minutes end) as core_minutes,
        sum(case when stage = 'AsleepDeep' then minutes end) as deep_minutes,
        sum(case when stage = 'AsleepREM' then minutes end) as rem_minutes
    from {{ ref('int_apple_health__sleep_segments') }}
    group by 1, 2

),

per_source as (

    select
        c.sleep_date,
        c.source_name,
        max(case when c.stage_group = 'asleep' then c.minutes end) as asleep_minutes,
        max(case when c.stage_group = 'awake' then c.minutes end) as awake_minutes,
        max(case when c.stage_group = 'in_bed' then c.minutes end) as in_bed_minutes,
        max(case when c.stage_group = 'asleep' then c.first_start end) as fell_asleep_at,
        max(case when c.stage_group = 'asleep' then c.last_end end) as woke_up_at
    from covered_minutes as c
    group by 1, 2

),

ranked as (

    select
        p.*,
        s.core_minutes,
        s.deep_minutes,
        s.rem_minutes,
        row_number() over (
            partition by p.sleep_date
            order by coalesce(p.asleep_minutes, 0) desc, coalesce(p.in_bed_minutes, 0) desc
        ) as source_rank,
        max(p.in_bed_minutes) over (partition by p.sleep_date) as best_in_bed_minutes
    from per_source as p
    left join stages as s on p.sleep_date = s.sleep_date and p.source_name = s.source_name

)

select
    sleep_date,
    round(asleep_minutes) as asleep_minutes,
    round(asleep_minutes / 60.0, 2) as asleep_hours,
    round(core_minutes) as core_minutes,
    round(deep_minutes) as deep_minutes,
    round(rem_minutes) as rem_minutes,
    round(awake_minutes) as awake_minutes,
    -- in-bed time may come from another source (e.g. iPhone)
    round(best_in_bed_minutes) as in_bed_minutes,
    fell_asleep_at,
    woke_up_at,
    (core_minutes is not null or deep_minutes is not null or rem_minutes is not null) as has_stages
from ranked
where source_rank = 1
