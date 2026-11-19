-- Singular test: slv_trips must never emit a pickup outside the pinned quarter.
-- Locks the contract the gold models are built on: widening the silver window
-- without updating this test (and README) fails here first.
select *
from {{ ref('slv_trips') }}
where pickup_at < timestamp '2024-01-01 00:00:00'
   or pickup_at >= timestamp '2024-04-01 00:00:00'
