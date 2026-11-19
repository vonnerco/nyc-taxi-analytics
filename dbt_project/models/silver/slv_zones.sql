-- One row per taxi zone, typed and de-duplicated.
{{ config(materialized='table') }}

select
    cast(LocationID as integer) as location_id,
    trim(Borough)               as borough,
    trim(Zone)                  as zone,
    trim(service_zone)          as service_zone
from {{ ref('brz_zones') }}
qualify row_number() over (partition by cast(LocationID as integer) order by Zone) = 1
