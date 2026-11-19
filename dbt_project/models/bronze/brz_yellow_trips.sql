-- Pass-through of the pinned quarter. No cleaning here: bronze mirrors the
-- source so a reviewer can always diff it against the parquet.
select *
from {{ source('raw', 'yellow_trips') }}
{% if var('row_limit', 0) > 0 %}
limit {{ var('row_limit') }}
{% endif %}
