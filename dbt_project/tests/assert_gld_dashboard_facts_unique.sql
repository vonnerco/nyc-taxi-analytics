select
    pickup_date,
    pickup_hour,
    dow_iso,
    pickup_zone,
    payment_type,
    distance_bucket,
    count(*) as row_count
from {{ ref('gld_dashboard_facts') }}
group by 1, 2, 3, 4, 5, 6
having count(*) > 1