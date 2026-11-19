-- Chart 1: demand curve. Grain: one row per pickup hour of day (24 rows).
{{ config(materialized='table') }}

select
    pickup_hour,
    count(*) as trip_count
from {{ ref('slv_trips') }}
group by pickup_hour
order by pickup_hour
