-- One cleaned trip per row: typed, bounded, de-duplicated, zone-enriched.
-- Every exclusion here is deliberate; see README "Trade-offs".
{{ config(materialized='table') }}

with source as (

    select * from {{ ref('brz_yellow_trips') }}

),

typed as (

    select
        cast(VendorID as smallint)                 as vendor_id,
        cast(tpep_pickup_datetime as timestamp)    as pickup_at,
        cast(tpep_dropoff_datetime as timestamp)   as dropoff_at,
        cast(passenger_count as tinyint)           as passenger_count,
        cast(trip_distance as double)              as trip_distance_mi,
        cast(PULocationID as integer)              as pickup_zone_id,
        cast(DOLocationID as integer)              as dropoff_zone_id,
        cast(payment_type as smallint)             as payment_type_id,
        cast(fare_amount as double)                as fare_amount,
        cast(tip_amount as double)                 as tip_amount,
        cast(total_amount as double)               as total_amount,
        date_diff(
            'minute',
            cast(tpep_pickup_datetime as timestamp),
            cast(tpep_dropoff_datetime as timestamp)
        )                                          as duration_min
    from source

),

filtered as (

    select *
    from typed
    where pickup_at is not null
      and dropoff_at is not null
      and pickup_zone_id is not null
      and dropoff_zone_id is not null
      and duration_min between 1 and 180
      and trip_distance_mi between 0.1 and 100
      and fare_amount >= 0
      -- Null is not invalid: TLC's Flex Fare records (payment_type 0) carry no
      -- passenger count. Excluding them would silently drop a whole payment type.
      and (passenger_count between 1 and 6 or passenger_count is null)
      -- Pinned quarter: the monthly files carry a handful of stray timestamps.
      and pickup_at >= timestamp '2024-01-01 00:00:00'
      and pickup_at <  timestamp '2024-04-01 00:00:00'

),

deduped as (

    select *
    from filtered
    qualify row_number() over (
        partition by vendor_id, pickup_at, dropoff_at,
                     pickup_zone_id, dropoff_zone_id, total_amount
        order by pickup_at
    ) = 1

)

select
    d.vendor_id,
    d.pickup_at,
    d.dropoff_at,
    d.passenger_count,
    d.trip_distance_mi,
    d.pickup_zone_id,
    d.dropoff_zone_id,
    d.payment_type_id,
    case d.payment_type_id
        when 0 then 'Flex Fare'
        when 1 then 'Credit card'
        when 2 then 'Cash'
        when 3 then 'No charge'
        when 4 then 'Dispute'
        when 5 then 'Unknown'
        when 6 then 'Voided trip'
        else 'Other'
    end                                            as payment_type,
    d.fare_amount,
    d.tip_amount,
    d.total_amount,
    d.duration_min,
    case when d.fare_amount > 0
         then round(100.0 * d.tip_amount / d.fare_amount, 2)
    end                                            as tip_pct,
    case when d.duration_min > 0
         then round(d.trip_distance_mi * 60.0 / d.duration_min, 2)
    end                                            as avg_speed_mph,
    cast(d.pickup_at as date)                      as pickup_date,
    extract(hour from d.pickup_at)                 as pickup_hour,
    z.zone                                         as pickup_zone,
    z.borough                                      as pickup_borough
from deduped d
left join {{ ref('slv_zones') }} z
    on d.pickup_zone_id = z.location_id
