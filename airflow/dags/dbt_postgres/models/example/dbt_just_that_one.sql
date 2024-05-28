-- Use the `ref` function to select from other models

select *
from {{ ref('dbt_device_information') }}
where owner = 'Cyril Yellowlea'
