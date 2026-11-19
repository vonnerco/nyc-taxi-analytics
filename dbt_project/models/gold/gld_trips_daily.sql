-- Chart 1a: trip volume over time at day grain. One row per pickup date.
{{ config(materialized='table') }}

select
    pickup_date,
    count(*)                    as trip_count,
    round(sum(total_amount), 2) as revenue
from {{ ref('slv_trips') }}
group by pickup_date
order by pickup_date
