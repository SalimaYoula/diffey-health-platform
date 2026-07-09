-- tests/test_maternal_mortality_range.sql
-- =============================================================================
-- Custom test: maternal mortality ratio must be between 0 and 1500.
-- Values outside this range indicate data quality issues.
-- Max observed value in dataset: 1168 (source: World Bank 2000-2023)
-- =============================================================================

SELECT *
FROM {{ ref('maternal_mortality') }}
WHERE maternal_mortality_ratio < 0
   OR maternal_mortality_ratio > 1500