-- A record can't end before it starts. Returns offending rows; the test passes when it returns none.
select
    record_id,
    record_type,
    start_at,
    end_at
from {{ ref('stg_apple_health__records') }}
where end_at < start_at
