-- Singular test: the silver filter promises a non-negative fare.
-- total_amount is not asserted: adjustments and refunds legitimately push it below zero.
select *
from {{ ref('slv_trips') }}
where fare_amount < 0
