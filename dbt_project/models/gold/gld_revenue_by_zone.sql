-- Chart 2: where the money is picked up. Grain: one row per pickup zone.
-- Top-10 slicing belongs to the chart, not the model, so the grain stays total-per-zone.
{{ config(materialized='table') }}

select
    pickup_zone,
    round(sum(total_amount), 2) as total_revenue
from {{ ref('slv_trips') }}
where pickup_zone is not null
group by pickup_zone
order by total_revenue desc
