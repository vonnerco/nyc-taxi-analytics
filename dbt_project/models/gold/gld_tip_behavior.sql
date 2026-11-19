-- Chart 4: does distance change tipping? Grain: one row per distance bucket.
-- tip_pct is fare-weighted (sum tips / sum fares), not the average of per-trip percentages:
-- averaging percentages would over-weight the many short cheap trips.
{{ config(materialized='table') }}

with bucketed as (

    select
        case
            when trip_distance_mi < 1  then '0-1 mi'
            when trip_distance_mi < 3  then '1-3 mi'
            when trip_distance_mi < 5  then '3-5 mi'
            when trip_distance_mi < 10 then '5-10 mi'
            else '10+ mi'
        end              as distance_bucket,
        trip_distance_mi,
        tip_amount,
        fare_amount
    from {{ ref('slv_trips') }}
    where fare_amount > 0

)

select
    distance_bucket,
    round(100.0 * sum(tip_amount) / sum(fare_amount), 2) as tip_pct
from bucketed
group by distance_bucket
order by min(trip_distance_mi)
