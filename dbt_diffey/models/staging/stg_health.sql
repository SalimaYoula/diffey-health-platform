-- models/staging/stg_health.sql
-- =============================================================================
-- Staging model for World Bank maternal and child health indicators.
-- Reads raw Parquet data and applies basic cleaning:
--   - filters out null values
--   - filters years 2000 to 2023
--   - renames value to indicator_value
--   - adds region classification
-- =============================================================================

SELECT
    year,
    country_code,
    country_name,
    indicator_code,
    indicator_name,
    value AS indicator_value,
    CASE
        WHEN country_code IN ('GN', 'SN', 'ML', 'CI', 'BF', 'GH', 'NG', 'MR') THEN 'West Africa'
        WHEN country_code IN ('FR', 'GB', 'US')                                  THEN 'Global Comparison'
        WHEN country_code = 'WLD'                                                 THEN 'World'
    END AS region
FROM read_parquet('/mnt/e/diffey_platform/data/raw/health_indicators.parquet')
WHERE value IS NOT NULL
  AND year BETWEEN 2000 AND 2023