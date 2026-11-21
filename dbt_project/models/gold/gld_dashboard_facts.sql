-- Shared gold fact cube for the interactive dashboard.
-- Grain: one row per pickup date x hour x ISO weekday x pickup zone x payment
-- type x distance bucket. The app filters and rolls this cube to the selected
-- grain so every chart and KPI responds to the same filters.
{{ config(materialized='table') }}

with trips as (

    select
        pickup_date,
        cast(pickup_hour as smallint) as pickup_hour,
        cast(date_part('isodow', pickup_date) as smallint) as dow_iso,
        pickup_zone,
        payment_type,
        case
            when trip_distance_mi < 1  then '0-1 mi'
            when trip_distance_mi < 3  then '1-3 mi'
            when trip_distance_mi < 5  then '3-5 mi'
            when trip_distance_mi < 10 then '5-10 mi'
            else '10+ mi'
        end as distance_bucket,
        total_amount,
        fare_amount,
        tip_amount
    from {{ ref('slv_trips') }}

)

select
    pickup_date,
    pickup_hour,
    dow_iso,
    pickup_zone,
    payment_type,
    distance_bucket,
    count(*)          as trip_count,
    sum(total_amount) as total_revenue,
    sum(fare_amount)  as fare_amount,
    sum(tip_amount)   as tip_amount
from trips
group by 1, 2, 3, 4, 5, 6