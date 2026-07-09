"""
extract.py
==========
Module responsible for extracting maternal and child health indicators
from the World Bank API for West African countries and global comparisons.

Data source: World Bank Open Data API (no authentication required)
API docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/898581

Author: Salima Youla
Date: 07/2026
"""

import os
from typing import Optional

import pandas as pd
import requests


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# World Bank API base URL
BASE_URL = "https://api.worldbank.org/v2"

# Countries — West Africa + global comparisons
COUNTRIES = {
    "GN": "Guinée",
    "SN": "Sénégal",
    "ML": "Mali",
    "CI": "Côte d'Ivoire",
    "BF": "Burkina Faso",
    "GH": "Ghana",
    "NG": "Nigeria",
    "MR": "Mauritanie",
    "FR": "France",
    "GB": "Royaume-Uni",
    "US": "États-Unis",
    "WLD": "Monde"
}

# Health indicators to extract
INDICATORS = {
    "SH.STA.MMRT":    "Maternal Mortality Ratio (per 100k live births)",
    "SP.DYN.IMRT.IN": "Infant Mortality Rate (per 1k live births)",
    "SH.STA.ANVC.ZS": "Pregnant women receiving prenatal care (%)",
    "SH.STA.BRTC.ZS": "Births Attended by Skilled Health Staff (%)",
    "SH.MMR.RISK.ZS":  "Lifetime Risk of Maternal Death (%)"
}

# Time range
START_YEAR = 2000
END_YEAR = 2023

OUTPUT_PATH = "/mnt/e/diffey_platform/data/raw/health_indicators.parquet"
# ---------------------------------------------------------------------------
# Functions
# ---------------------------------------------------------------------------

def _fetch_indicator(
    country_code: str,
    indicator_code: str,
    start_year: int,
    end_year: int
) -> list[dict]:
    """
    Fetch a single indicator for a single country from the World Bank API.

    Args:
        country_code (str): ISO country code (e.g. 'GN' for Guinea).
        indicator_code (str): World Bank indicator code (e.g. 'SH.STA.MMRT').
        start_year (int): Start year of the data range.
        end_year (int): End year of the data range.

    Returns:
        list[dict]: List of records with year and value for the indicator.
                    Returns empty list if the API call fails.
    """
    url = (
        f"{BASE_URL}/country/{country_code}/indicator/{indicator_code}"
        f"?format=json&per_page=100&mrv={end_year - start_year + 1}"
    )

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()

        # World Bank API returns [metadata, data] — we need index 1
        if not data or len(data) < 2 or not data[1]:
            print(f"   No data for {country_code} — {indicator_code}")
            return []

        records = []
        for item in data[1]:
            # Skip years with no reported value
            if item["value"] is None:
                continue

            records.append({
                "year":             int(item["date"]),
                "country_code":     country_code,
                "country_name":     COUNTRIES[country_code],
                "indicator_code":   indicator_code,
                "indicator_name":   INDICATORS[indicator_code],
                "value":            float(item["value"])
            })

        return records

    except requests.exceptions.RequestException as e:
        print(f"   API error for {country_code} — {indicator_code}: {e}")
        return []


def extract_data() -> str:
    """
    Extract all health indicators for all countries from the World Bank API.

    Iterates over all combinations of countries and indicators defined
    in the module constants, fetches data from the World Bank API,
    and saves the result as a Parquet file.

    Returns:
        str: Absolute path to the saved Parquet file.
    """
    print("Starting data extraction from World Bank API...")
    print(f"Countries  : {list(COUNTRIES.keys())}")
    print(f"Indicators : {list(INDICATORS.keys())}")
    print(f"Period     : {START_YEAR} — {END_YEAR}")

    all_records = []

    for country_code, country_name in COUNTRIES.items():
        print(f"\nExtracting data for {country_name} ({country_code})...")

        for indicator_code in INDICATORS:
            records = _fetch_indicator(
                country_code,
                indicator_code,
                START_YEAR,
                END_YEAR
            )
            all_records.extend(records)
            print(f"   {indicator_code} — {len(records)} records")

    # Build final DataFrame
    df = pd.DataFrame(all_records)

    print(f"\nTotal records extracted: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    # Save as Parquet
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_parquet(OUTPUT_PATH, index=False, engine="pyarrow", version="2.6")

    print(f"Data saved to: {OUTPUT_PATH}")
    return OUTPUT_PATH


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    extract_data()