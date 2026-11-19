-- Chart 1b: trip volume over time at week grain. One row per ISO week start (Monday).
{{ config(materialized='table') }}

select
    date_trunc('week', pickup_date) as week_start,
    count(*)                        as trip_count,
    round(sum(total_amount), 2)     as revenue
from {{ ref('slv_trips') }}
group by week_start
order by week_start
