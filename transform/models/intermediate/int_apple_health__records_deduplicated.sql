-- Remove EXACT duplicates: the same record written twice by a sync (852 found in profiling).
-- Identical content -> identical record_id; keep the earliest-created copy.
-- Columns are listed explicitly (portable SQL: Postgres has no "select * exclude").

with ranked as (

    select
        *,
        row_number() over (partition by record_id order by created_at) as copy_number
    from {{ ref('stg_apple_health__records') }}

)

select
    record_id,
    record_type,
    value_kind,
    value_numeric,
    value_category,
    unit,
    start_at,
    end_at,
    start_at_local,
    end_at_local,
    local_date,
    created_at,
    source_name,
    source_version,
    device,
    metadata,
    exported_at
from ranked
where copy_number = 1
