-- 🥇 One row per day: de-duplicated activity totals.

with hourly as (

    select
        local_date,
        record_type,
        value
    from {{ ref('int_apple_health__activity_hourly') }}

),

stand as (

    -- Stand hours: count of hours marked "Stood" (category record, not cumulative)
    -- distinct clock hours: 2 sources (e.g. old + new Watch) report the same hour (1,395 duplicates found)
    select
        local_date,
        count(distinct date_trunc('hour', start_at_local)) as stand_hours
    from {{ ref('int_apple_health__records_deduplicated') }}
    where record_type = 'AppleStandHour' and value_category = 'Stood'
    group by 1

),

daily as (

    select
        local_date,
        -- Portable SQL: "sum(case when ...)" instead of Postgres-only "sum(...) filter (where ...)"
        sum(case when record_type = 'StepCount' then value end) as steps,
        sum(case when record_type = 'DistanceWalkingRunning' then value end) as distance_km,
        sum(case when record_type = 'ActiveEnergyBurned' then value end) as active_energy_kcal,
        sum(case when record_type = 'AppleExerciseTime' then value end) as exercise_minutes,
        sum(case when record_type = 'FlightsClimbed' then value end) as flights_climbed
    from hourly
    group by 1

)

select
    daily.local_date as activity_date,
    round(daily.steps)::integer as steps,
    round(daily.distance_km, 2) as distance_km,
    round(daily.active_energy_kcal) as active_energy_kcal,
    round(daily.exercise_minutes) as exercise_minutes,
    round(daily.flights_climbed)::integer as flights_climbed,
    stand.stand_hours
from daily
left join stand on daily.local_date = stand.local_date
