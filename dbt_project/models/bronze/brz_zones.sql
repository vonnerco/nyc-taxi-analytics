-- Pass-through of the zone lookup; silver does the typing.
select *
from {{ source('raw', 'zones') }}
