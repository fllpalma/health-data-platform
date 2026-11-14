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
        sum(value) filter (where record_type = 'StepCount') as steps,
        sum(value) filter (where record_type = 'DistanceWalkingRunning') as distance_km,
        sum(value) filter (where record_type = 'ActiveEnergyBurned') as active_energy_kcal,
        sum(value) filter (where record_type = 'AppleExerciseTime') as exercise_minutes,
        sum(value) filter (where record_type = 'FlightsClimbed') as flights_climbed
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
