-- models/marts/maternal_mortality.sql
-- =============================================================================
-- Mart model for maternal mortality ratio.
-- Indicator: SH.STA.MMRT
-- Unit: deaths per 100,000 live births
-- Source: World Bank API
-- =============================================================================

SELECT
    year,
    country_code,
    country_name,
    region,
    indicator_value AS maternal_mortality_ratio
FROM {{ ref('stg_health') }}
WHERE indicator_code = 'SH.STA.MMRT'
ORDER BY country_code, year