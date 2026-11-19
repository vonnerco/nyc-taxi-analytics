-- Singular test: silver must never contain a trip outside the 1-180 minute window.
select *
from {{ ref('slv_trips') }}
where duration_min < 1
   or duration_min > 180
