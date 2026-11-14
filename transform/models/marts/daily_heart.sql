-- 🥇 One row per day: heart health indicators (daily averages across sources).
-- Portable SQL: "avg(case when ...)" instead of Postgres-only "avg(...) filter (where ...)".

select
    local_date as heart_date,
    round(avg(case when record_type = 'RestingHeartRate' then value_numeric end), 1) as resting_hr_bpm,
    round(avg(case when record_type = 'HeartRateVariabilitySDNN' then value_numeric end), 1) as hrv_sdnn_ms,
    round(avg(case when record_type = 'WalkingHeartRateAverage' then value_numeric end), 1) as walking_hr_bpm,
    sum(case when record_type = 'HeartRate' then 1 else 0 end) as heart_rate_samples
from {{ ref('int_apple_health__records_deduplicated') }}
where record_type in ('RestingHeartRate', 'HeartRateVariabilitySDNN', 'WalkingHeartRateAverage', 'HeartRate')
group by 1
