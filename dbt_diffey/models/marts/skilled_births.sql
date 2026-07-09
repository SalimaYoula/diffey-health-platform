-- models/marts/skilled_births.sql
-- =============================================================================
-- Mart model for births attended by skilled health staff.
-- Indicator: SH.STA.BRTC.ZS
-- Unit: percentage of total births (%)
-- Source: World Bank API
-- =============================================================================

SELECT
    year,
    country_code,
    country_name,
    region,
    indicator_value AS skilled_births
FROM {{ ref('stg_health') }}
WHERE indicator_code = 'SH.STA.BRTC.ZS'
ORDER BY country_code, year