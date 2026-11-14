-- Resolve OVERLAPPING sources (iPhone + Watch counting the same walk) for cumulative metrics.
-- Method (ADR 0004): per hour, total each source separately, then keep the HIGHEST source total.
-- Adding sources together double-counts (+28% on steps in profiling).

{% set cumulative_types = [
    'StepCount',
    'DistanceWalkingRunning',
    'ActiveEnergyBurned',
    'AppleExerciseTime',
    'FlightsClimbed',
] %}

with records as (

    select
        record_type,
        source_name,
        start_at_local,
        value_numeric,
        unit
    from {{ ref('int_apple_health__records_deduplicated') }}
    where record_type in ({{ "'" ~ cumulative_types | join("', '") ~ "'" }})

),

per_source_hour as (

    select
        record_type,
        unit,
        date_trunc('hour', start_at_local) as hour_local,
        source_name,
        sum(value_numeric) as source_total
    from records
    group by 1, 2, 3, 4

),

best_source_per_hour as (

    select
        record_type,
        unit,
        hour_local,
        max(source_total) as value,
        count(*) as sources_in_hour   -- >1 means overlap was resolved here
    from per_source_hour
    group by 1, 2, 3

)

select
    record_type || '|' || hour_local::text as activity_hour_id,
    record_type,
    hour_local,
    hour_local::date as local_date,
    value,
    unit,
    sources_in_hour
from best_source_per_hour
