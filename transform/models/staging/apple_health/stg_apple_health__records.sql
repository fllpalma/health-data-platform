-- Staging: clean names + real data types. No business logic (no dedupe, no aggregation).
-- 🍽️ Prep station 1: wash and cut every ingredient the same way.

with source as (

    select * from {{ source('apple_health', 'records') }}

),

cleaned as (

    select
        -- Stable ID built from the record's content (dlt's own _dlt_id changes on every load)
        md5(concat_ws('|', type, source_name, start_date, end_date, creation_date, value)) as record_id,

        -- What: "HKQuantityTypeIdentifierStepCount" -> "StepCount"
        regexp_replace(type, '^HK(Quantity|Category|DataType)TypeIdentifier', '') as record_type,
        case
            when type like 'HKQuantityTypeIdentifier%' then 'quantity'
            when type like 'HKCategoryTypeIdentifier%' then 'category'
            else 'other'
        end as value_kind,

        -- Value: numbers for quantities; readable labels for categories
        case when type like 'HKQuantityTypeIdentifier%' then value::numeric end as value_numeric,
        case
            when type like 'HKCategoryTypeIdentifier%'
                then replace(value, 'HKCategoryValue' || regexp_replace(type, '^HKCategoryTypeIdentifier', ''), '')
        end as value_category,
        unit,

        -- When: absolute moment (UTC-aware) AND wall-clock time where you were (for daily grouping)
        start_date::timestamptz as start_at,
        end_date::timestamptz as end_at,
        left(start_date, 19)::timestamp as start_at_local,
        left(end_date, 19)::timestamp as end_at_local,
        left(start_date, 10)::date as local_date,
        creation_date::timestamptz as created_at,

        -- Who/what recorded it
        source_name,
        source_version,
        device,
        metadata,

        export_date::timestamptz as exported_at

    from source

)

select * from cleaned
