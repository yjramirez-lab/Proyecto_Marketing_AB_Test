with leads as (
    select * from {{ ref('stg_leads') }}
),

aggregated as (
    select
        test_variant,
        count(distinct lead_id) as total_users,
        sum(is_converted) as total_conversions,
        
        -- Calculamos la tasa de conversión global por variante desde la Capa Mart
        round(avg(is_converted) * 100, 2) as conversion_rate_pct
    from leads
    group by 1
)

select * from aggregated
order by test_variant
