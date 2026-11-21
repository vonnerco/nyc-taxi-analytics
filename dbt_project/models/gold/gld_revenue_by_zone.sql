-- Chart 3: where the money is picked up. Grain: one row per pickup zone.
-- Top-N slicing belongs to the chart, not the model, so the grain stays
-- total-per-zone while the chart can rank by revenue, average fare or trips.
{{ config(materialized='table') }}

select
    pickup_zone,
    count(*)                     as trip_count,
    round(sum(total_amount), 2)  as total_revenue,
    round(avg(fare_amount), 2)   as avg_fare
from {{ ref('slv_trips') }}
where pickup_zone is not null
group by pickup_zone
order by total_revenue desc
