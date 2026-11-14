-- Sleep records with the NIGHT they belong to and a simple stage group.
-- Night rule: sleep starting between 18:00 day D-1 and 18:00 day D belongs to day D
-- (the morning you wake up). Shifting by +6h does exactly that.
--
-- Data-quality rule (found by the in_range test on daily_sleep):
--   one sleep app writes "in bed" records lasting 16-24+ hours (100 records, app glitch).
--   In-bed records longer than 16 h are treated as implausible and excluded here.
--   Raw data (bronze) is untouched, so this rule can be changed at any time.

{% set max_plausible_in_bed_hours = 16 %}

with segments as (

    select
        record_id,
        source_name,
        (start_at_local + interval '6 hours')::date as sleep_date,
        value_category as stage,
        case
            when
                value_category in ('AsleepCore', 'AsleepDeep', 'AsleepREM', 'AsleepUnspecified', 'Asleep')
                then 'asleep'
            when value_category = 'Awake' then 'awake'
            when value_category = 'InBed' then 'in_bed'
            else 'other'
        end as stage_group,
        start_at_local,
        end_at_local,
        extract(epoch from (end_at - start_at)) / 60.0 as minutes
    from {{ ref('int_apple_health__records_deduplicated') }}
    where record_type = 'SleepAnalysis'

)

select * from segments
where not (stage_group = 'in_bed' and minutes > {{ max_plausible_in_bed_hours }} * 60)
