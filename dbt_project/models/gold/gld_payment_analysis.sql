-- Charts 5-6: payment mix and behaviour. One row per payment type label.
-- tip_pct is fare-weighted; cash trips record no tip, so their 0.00 is a TLC
-- property, not a rider statement.
{{ config(materialized='table') }}

select
    payment_type,
    count(*)                                                         as trip_count,
    round(100.0 * count(*) / sum(count(*)) over (), 2)               as trip_share_pct,
    round(avg(fare_amount), 2)                                       as avg_fare,
    round(100.0 * sum(tip_amount) / nullif(sum(fare_amount), 0), 2)  as tip_pct
from {{ ref('slv_trips') }}
group by payment_type
order by trip_count desc
