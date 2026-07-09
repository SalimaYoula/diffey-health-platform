"""
app.py
======
Streamlit interactive dashboard for the Diffey Health Data Platform.

Displays maternal and child health indicators for West African countries
and global comparisons, powered by World Bank data processed with dbt.

Author: Salima Youla
Date: 07/2026
"""

import duckdb
import pandas as pd
import plotly.express as px
import pycountry
import streamlit as st


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DB_PATH = "/mnt/e/diffey_platform/data/diffey.duckdb"

WEST_AFRICA_COUNTRIES = [
    "Guinée", "Sénégal", "Mali", "Côte d'Ivoire",
    "Burkina Faso", "Ghana", "Nigeria", "Mauritanie"
]

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Diffey Health Platform",
    page_icon="🤱",
    layout="wide"
)

# ---------------------------------------------------------------------------
# Database Connection
# ---------------------------------------------------------------------------

@st.cache_resource
def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Create and cache a DuckDB connection.

    Returns:
        duckdb.DuckDBPyConnection: Active DuckDB connection.
    """
    return duckdb.connect(DB_PATH)


con = get_connection()


# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------

def _alpha2_to_alpha3(code: str) -> str:
    """
    Convert ISO Alpha-2 country code to Alpha-3 for Plotly maps.

    Args:
        code (str): ISO Alpha-2 country code (e.g. 'GN').

    Returns:
        str: ISO Alpha-3 country code (e.g. 'GIN').
    """
    if code == "WLD":
        return "WLD"
    country = pycountry.countries.get(alpha_2=code)
    return country.alpha_3 if country else code

# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------

@st.cache_data
def load_maternal_mortality(_con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """
    Load maternal mortality data from DuckDB and add Alpha-3 country codes.

    Args:
        _con: Active DuckDB connection (prefixed with _ to skip hashing).

    Returns:
        pd.DataFrame: Maternal mortality data with iso_alpha3 column.
    """
    df = _con.execute("SELECT * FROM maternal_mortality").df()
    df["iso_alpha3"] = df["country_code"].apply(_alpha2_to_alpha3)
    return df


@st.cache_data
def load_indicator(_con: duckdb.DuckDBPyConnection, table: str) -> pd.DataFrame:
    """
    Load any health indicator table from DuckDB.

    Args:
        _con: Active DuckDB connection.
        table (str): Table name (e.g. 'infant_mortality').

    Returns:
        pd.DataFrame: Health indicator data.
    """
    return _con.execute(f"SELECT * FROM {table}").df()

# ---------------------------------------------------------------------------
# Load Data
# ---------------------------------------------------------------------------

df_maternal    = load_maternal_mortality(con)
df_infant      = load_indicator(con, "infant_mortality")
df_prenatal    = load_indicator(con, "prenatal_care")
df_skilled     = load_indicator(con, "skilled_births")
df_lifetime    = load_indicator(con, "lifetime_risk")

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

st.sidebar.title("Diffey Health Platform")
st.sidebar.markdown("*Devenir mère, un don du ciel*")
st.sidebar.markdown("---")
st.sidebar.markdown("**About Diffey**")
st.sidebar.markdown("[Follow us on Facebook](https://www.facebook.com/Diffeyy)")
st.sidebar.markdown("diffeey@gmail.com")

page = st.sidebar.selectbox(
    "Navigation",
    ["Overview", "West Africa Focus", "Global Comparison"]
)

if page == "Overview":
    st.sidebar.markdown("---")
    selected_country = st.sidebar.selectbox(
        "Select a country",
        options=df_maternal["country_name"].unique().tolist(),
        index=0
    )
    selected_code = df_maternal[
        df_maternal["country_name"] == selected_country
    ]["country_code"].values[0]

st.sidebar.markdown("---")
st.sidebar.markdown("**Data source:** World Bank Open Data")
st.sidebar.markdown("**Period:** 2000 — 2023")
st.sidebar.markdown("**Countries:** 12 (8 West Africa + 4 global)")

# ---------------------------------------------------------------------------
# Global Variables
# ---------------------------------------------------------------------------

# Latest year available across all indicators
latest_year = df_maternal["year"].max()

# ---------------------------------------------------------------------------
# Page 1 — Overview
# ---------------------------------------------------------------------------

if page == "Overview":
    st.title("Maternal & Child Health in West Africa")
    st.markdown("*Data-driven insights to support Diffey's mission*")
    st.markdown("---")

    selected_value = df_maternal[
        (df_maternal["country_code"] == selected_code) &
        (df_maternal["year"] == latest_year)
    ]["maternal_mortality_ratio"].values[0]

    france = df_maternal[
        (df_maternal["country_code"] == "FR") &
        (df_maternal["year"] == latest_year)
    ]["maternal_mortality_ratio"].values[0]

    world = df_maternal[
        (df_maternal["country_code"] == "WLD") &
        (df_maternal["year"] == latest_year)
    ]["maternal_mortality_ratio"].values[0]

    ratio = round(selected_value / france, 0)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label=f"{selected_country} Maternal Mortality",
            value=f"{int(selected_value)}",
            help="Deaths per 100,000 live births"
        )
    with col2:
        st.metric(
            label="France Maternal Mortality",
            value=f"{int(france)}",
            help="Deaths per 100,000 live births"
        )
    with col3:
        st.metric(
            label="World Average",
            value=f"{int(world)}",
            help="Deaths per 100,000 live births"
        )
    with col4:
        st.metric(
            label=f"{selected_country} vs France",
            value=f"{int(ratio)}x more risk",
            help=f"How many times more likely to die in {selected_country} vs France"
        )

    st.markdown("---")

    # World map
    st.subheader("Global Maternal Mortality Map")

    df_map = df_maternal[df_maternal["year"] == latest_year]
    df_map = df_map[df_map["country_code"] != "WLD"]

    fig_map = px.choropleth(
        df_map,
        locations="iso_alpha3",
        color="maternal_mortality_ratio",
        hover_name="country_name",
        color_continuous_scale="Reds",
        title=f"Maternal Mortality Ratio — {latest_year}",
        labels={"maternal_mortality_ratio": "Deaths per 100k births"}
    )

    fig_map.update_layout(height=500)
    st.plotly_chart(fig_map, width="stretch")

# ---------------------------------------------------------------------------
# Page 2 — West Africa Focus
# ---------------------------------------------------------------------------

elif page == "West Africa Focus":
    st.title("West Africa — Maternal Health Evolution")
    st.markdown("---")

    # Filter West Africa only
    df_wa = df_maternal[df_maternal["region"] == "West Africa"]

    # Evolution over time
    st.subheader("Maternal Mortality Trend (2000 — 2023)")

    fig_line = px.line(
        df_wa,
        x="year",
        y="maternal_mortality_ratio",
        color="country_name",
        title="Maternal Mortality Ratio by Country",
        labels={
            "maternal_mortality_ratio": "Deaths per 100k births",
            "year": "Year",
            "country_name": "Country"
        },
        markers=True
    )

    fig_line.update_layout(height=500)
    st.plotly_chart(fig_line, width="stretch")

    st.markdown("---")

    # Latest year comparison bar chart
    st.subheader(f"Country Comparison — {latest_year}")

    df_wa_latest = df_wa[df_wa["year"] == latest_year].sort_values(
        "maternal_mortality_ratio", ascending=True
    )

    fig_bar = px.bar(
        df_wa_latest,
        x="maternal_mortality_ratio",
        y="country_name",
        orientation="h",
        color="maternal_mortality_ratio",
        color_continuous_scale="Reds",
        title=f"Maternal Mortality Ratio — West Africa {latest_year}",
        labels={
            "maternal_mortality_ratio": "Deaths per 100k births",
            "country_name": "Country"
        }
    )

    fig_bar.update_layout(height=400)
    st.plotly_chart(fig_bar, width="stretch")


# ---------------------------------------------------------------------------
# Page 3 — Global Comparison
# ---------------------------------------------------------------------------

elif page == "Global Comparison":
    st.title("Global Comparison — West Africa vs World")
    st.markdown("---")

    # Lifetime risk — the most impactful KPI
    st.subheader("Lifetime Risk of Maternal Death (%)")
    st.markdown("""
    > **How to read this:** This indicator shows the probability that a woman 
    will die from maternal causes during her lifetime.
    """)

    df_risk_latest = df_lifetime[
        (df_lifetime["year"] == df_lifetime["year"].max()) &
        (df_lifetime["country_code"] != "WLD")
    ].sort_values("lifetime_risk", ascending=False)

    fig_risk = px.bar(
    df_risk_latest,
    x="country_name",
    y="lifetime_risk",
    color="lifetime_risk",
    color_continuous_scale="Reds",
    title="Lifetime Risk of Maternal Death — 2023",
    labels={
        "lifetime_risk": "Probability (%)",
        "country_name": "Country"
    }
)

    fig_risk.update_layout(height=450)
    st.plotly_chart(fig_risk, width="stretch")

    st.markdown("---")

    # All indicators comparison
    st.subheader("All Indicators — West Africa vs Global")

    col1, col2 = st.columns(2)

    with col1:
         # pre_natal care
        st.markdown("**Prenatal Care Coverage (%) — Evolution**")

        fig_pre = px.line(
            df_prenatal[df_prenatal["region"] != "World"],
            x="year",
            y="prenatal_care",
            color="country_name",
            markers=True,
            labels={
                "prenatal_care": "Coverage (%)",
                "year": "Year",
                "country_name": "Country"
            }
        )
        fig_pre.update_layout(height=400)
        st.plotly_chart(fig_pre, width="stretch")
        

    with col2:
        # Skilled births
        st.markdown("**Births Attended by Skilled Staff (%)**")
        most_recent_sk = df_skilled.groupby("country_code")["year"].max().min()
        df_sk = df_skilled[
            df_skilled["year"] == most_recent_sk
        ].sort_values("skilled_births", ascending=True)



        fig_sk = px.bar(
            df_sk,
            x="skilled_births",
            y="country_name",
            orientation="h",
            color="region",
            color_discrete_map={
                "West Africa": "red",
                "Global Comparison": "steelblue",
                "World": "gray"
            },
            labels={
                "skilled_births": "Coverage (%)",
                "country_name": "Country"
            }
        )
        st.plotly_chart(fig_sk, width="stretch")

    st.caption("Note: Some countries may have missing data due to limited reporting to the World Bank.")