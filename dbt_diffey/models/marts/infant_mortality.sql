-- models/marts/infant_mortality.sql
-- =============================================================================
-- Mart model for infant mortality rate.
-- Indicator: SP.DYN.IMRT.IN
-- Unit: deaths per 1,000 live births
-- Source: World Bank API
-- =============================================================================

SELECT
    year,
    country_code,
    country_name,
    region,
    indicator_value AS infant_mortality_rate
FROM {{ ref('stg_health') }}
WHERE indicator_code = 'SP.DYN.IMRT.IN'
ORDER BY country_code, year