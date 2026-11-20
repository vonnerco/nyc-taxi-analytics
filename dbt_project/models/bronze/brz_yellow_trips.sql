-- Pass-through of the pinned quarter. No cleaning here: bronze mirrors the
-- source so a reviewer can always diff it against the parquet. No filter, no
-- cap, no cast: the row set is exactly what the TLC published.
select *
from {{ source('raw', 'yellow_trips') }}
