-- models/marts/prenatal_care.sql
-- =============================================================================
-- Mart model for pregnant women receiving prenatal care.
-- Indicator: SH.STA.ANVC.ZS
-- Unit: percentage of pregnant women (%)
-- Source: World Bank API
-- =============================================================================

SELECT
    year,
    country_code,
    country_name,
    region,
    indicator_value AS prenatal_care
FROM {{ ref('stg_health') }}
WHERE indicator_code = 'SH.STA.ANVC.ZS'
ORDER BY country_code, year