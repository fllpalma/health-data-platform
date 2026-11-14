-- 🥇 One row per day: heart health indicators (daily averages across sources).

select
    local_date as heart_date,
    round(avg(value_numeric) filter (where record_type = 'RestingHeartRate'), 1) as resting_hr_bpm,
    round(avg(value_numeric) filter (where record_type = 'HeartRateVariabilitySDNN'), 1) as hrv_sdnn_ms,
    round(avg(value_numeric) filter (where record_type = 'WalkingHeartRateAverage'), 1) as walking_hr_bpm,
    count(*) filter (where record_type = 'HeartRate') as heart_rate_samples
from {{ ref('int_apple_health__records_deduplicated') }}
where record_type in ('RestingHeartRate', 'HeartRateVariabilitySDNN', 'WalkingHeartRateAverage', 'HeartRate')
group by 1
