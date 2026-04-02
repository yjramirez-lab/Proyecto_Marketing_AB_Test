with raw_data as (
    -- DuckDB puede leer CSVs directamente
    select * from read_csv_auto('../raw_leads.csv')
),

cleaned as (
    select
        lead_id,
        cast(timestamp as timestamp) as event_timestamp,
        
        -- Renombrar variante y mantener sólo las válidas
        variante as test_variant,
        
        -- Imputar valores nulos en dispositivo
        case 
            when dispositivo is null or dispositivo = '' then 'unknown'
            else dispositivo 
        end as device_type,
        
        fuente as traffic_source,
        cast(conversion as integer) as is_converted
        
    from raw_data
    
    -- Filtros vitales de Data Quality
    where variante in ('A', 'B')
      and cast(timestamp as timestamp) >= '2020-01-01'
      and cast(timestamp as timestamp) <= '2030-12-31'
)

, deduplicated as (
    select
        *,
        row_number() over (partition by lead_id order by event_timestamp desc) as rn
    from cleaned
)

select
    lead_id,
    event_timestamp,
    test_variant,
    device_type,
    traffic_source,
    is_converted
from deduplicated
where rn = 1
