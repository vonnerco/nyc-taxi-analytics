-- KPI strip: the three headline numbers, one row, no app-side aggregation.
{{ config(materialized='table') }}

select
    count(*)                                                       as trips,
    round(sum(total_amount), 2)                                    as total_revenue,
    round(100.0 * sum(tip_amount) / nullif(sum(fare_amount), 0), 2) as tip_pct
from {{ ref('slv_trips') }}
