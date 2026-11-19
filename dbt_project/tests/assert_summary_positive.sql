-- Singular test: the single-row KPI table must be populated and positive.
select *
from {{ ref('gld_trip_summary') }}
where trips <= 0
   or total_revenue <= 0
