-- Chart 2: weekly seasonality. Grain: one row per ISO weekday (1 = Monday).
-- Kept as its own gold model so the app never aggregates; the bar reads it whole.
{{ config(materialized='table') }}

select
    cast(date_part('isodow', pickup_date) as integer) as dow_iso,
    dayname(pickup_date)                              as day_name,
    count(*)                                          as trip_count
from {{ ref('slv_trips') }}
group by 1, 2
order by 1
