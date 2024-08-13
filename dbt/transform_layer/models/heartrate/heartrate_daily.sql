-- Use the `ref` function to select from other models --

{{
  config(
    materialized='incremental',
    unique_key='date'
  )
}}



with daily_agg as (
    select 
        date,
        max(heartrate) as max_heartrate
    from
        {{ source("heartrate_bronze", "heartrate_data") }}
    group by
        "date"
)

select distinct
    date,
    max_heartrate
from
    daily_agg
