-- 🥇 One row per night (dated by the morning you wake up).
-- Overlapping sources: per night, use the source that recorded the most sleep (same idea as ADR 0004).
-- Overlapping records WITHIN a source: measure time actually covered (merge overlaps), don't add up records.
--   Found by the in_range test: summing inflated in-bed time by 10.5% (58 nights > 24 h).
--   ⚠️ Dialect: range_agg/tsrange are Postgres-specific; Snowflake (Phase 2b) needs a different approach.

with covered as (

    -- Merge overlapping segments into one continuous coverage per night, source and stage group
    select sleep_date, source_name, stage_group,
           range_agg(tsrange(start_at_local, end_at_local)) as coverage
    from {{ ref('int_apple_health__sleep_segments') }}
    where stage_group in ('asleep', 'awake', 'in_bed')
    group by 1, 2, 3

),

covered_minutes as (

    select sleep_date, source_name, stage_group,
           sum(extract(epoch from (upper(piece) - lower(piece))) / 60.0) as minutes,
           min(lower(piece)) as first_start,
           max(upper(piece)) as last_end
    from covered, unnest(coverage) as piece
    group by 1, 2, 3

),

stages as (

    -- Stage detail (Core/Deep/REM): a breakdown only, summed per stage
    select sleep_date, source_name,
           sum(minutes) filter (where stage = 'AsleepCore') as core_minutes,
           sum(minutes) filter (where stage = 'AsleepDeep') as deep_minutes,
           sum(minutes) filter (where stage = 'AsleepREM') as rem_minutes
    from {{ ref('int_apple_health__sleep_segments') }}
    group by 1, 2

),

per_source as (

    select
        c.sleep_date,
        c.source_name,
        max(c.minutes) filter (where c.stage_group = 'asleep') as asleep_minutes,
        max(c.minutes) filter (where c.stage_group = 'awake') as awake_minutes,
        max(c.minutes) filter (where c.stage_group = 'in_bed') as in_bed_minutes,
        max(c.first_start) filter (where c.stage_group = 'asleep') as fell_asleep_at,
        max(c.last_end) filter (where c.stage_group = 'asleep') as woke_up_at
    from covered_minutes c
    group by 1, 2

),

ranked as (

    select
        p.*,
        s.core_minutes, s.deep_minutes, s.rem_minutes,
        row_number() over (
            partition by p.sleep_date
            order by coalesce(p.asleep_minutes, 0) desc, coalesce(p.in_bed_minutes, 0) desc
        ) as source_rank,
        max(p.in_bed_minutes) over (partition by p.sleep_date) as best_in_bed_minutes
    from per_source p
    left join stages s using (sleep_date, source_name)

)

select
    sleep_date,
    round(asleep_minutes) as asleep_minutes,
    round(asleep_minutes / 60.0, 2) as asleep_hours,
    round(core_minutes) as core_minutes,
    round(deep_minutes) as deep_minutes,
    round(rem_minutes) as rem_minutes,
    round(awake_minutes) as awake_minutes,
    round(best_in_bed_minutes) as in_bed_minutes,   -- in-bed time may come from another source (e.g. iPhone)
    fell_asleep_at,
    woke_up_at,
    (core_minutes is not null or deep_minutes is not null or rem_minutes is not null) as has_stages
from ranked
where source_rank = 1
