-- models/marts/lifetime_risk.sql
-- =============================================================================
-- Mart model for lifetime risk of maternal death.
-- Indicator: SH.MMR.RISK.ZS
-- Unit: probability of dying from maternal causes (%)
-- Source: World Bank API
-- =============================================================================

SELECT
    year,
    country_code,
    country_name,
    region,
    indicator_value AS lifetime_risk
FROM {{ ref('stg_health') }}
WHERE indicator_code = 'SH.MMR.RISK.ZS'
ORDER BY country_code, year