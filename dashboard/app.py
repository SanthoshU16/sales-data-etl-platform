import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

load_dotenv(BASE_DIR / ".env")


# ============================================================
# DATABASE CONNECTION
# ============================================================

@st.cache_resource
def get_engine():
    database_url = (
        f"postgresql+psycopg2://"
        f"{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )

    return create_engine(database_url)


# ============================================================
# QUERY HELPER
# ============================================================

@st.cache_data
def run_query(query, params=None):
    engine = get_engine()

    with engine.connect() as connection:
        return pd.read_sql(
            text(query),
            connection,
            params=params
        )


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Sales Analytics Dashboard",
    page_icon="📊",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("📊 Sales Analytics Dashboard")

st.caption(
    "UCI Online Retail — PostgreSQL Data Warehouse"
)

st.divider()


# ============================================================
# SIDEBAR FILTERS
# ============================================================

st.sidebar.header("🔎 Filters")


# -----------------------------
# Year Filter
# -----------------------------

year_query = """
SELECT DISTINCT year
FROM warehouse.dim_date
ORDER BY year;
"""

years_df = run_query(year_query)

year_options = ["All"] + years_df["year"].astype(str).tolist()

selected_year = st.sidebar.selectbox(
    "📅 Year",
    year_options
)


# -----------------------------
# Country Filter
# -----------------------------

country_query = """
SELECT country_name
FROM warehouse.dim_country
ORDER BY country_name;
"""

countries_df = run_query(country_query)

country_options = (
    ["All"] +
    countries_df["country_name"].tolist()
)

selected_country = st.sidebar.selectbox(
    "🌍 Country",
    country_options
)


# -----------------------------
# Transaction Status Filter
# -----------------------------

status_options = [
    "All",
    "Normal",
    "Cancelled"
]

selected_status = st.sidebar.selectbox(
    "🔄 Transaction Status",
    status_options
)


# ============================================================
# BUILD FILTER CONDITIONS
# ============================================================

filter_conditions = []

params = {}


# -----------------------------
# Year condition
# -----------------------------

if selected_year != "All":

    filter_conditions.append(
        "d.year = :year"
    )

    params["year"] = int(selected_year)


# -----------------------------
# Country condition
# -----------------------------

if selected_country != "All":

    filter_conditions.append(
        "c.country_name = :country"
    )

    params["country"] = selected_country


# -----------------------------
# Transaction status condition
# -----------------------------

if selected_status == "Normal":

    filter_conditions.append(
        "f.is_cancelled = FALSE"
    )

elif selected_status == "Cancelled":

    filter_conditions.append(
        "f.is_cancelled = TRUE"
    )


# -----------------------------
# Final WHERE condition
# -----------------------------

if filter_conditions:

    filter_sql = " AND ".join(filter_conditions)

else:

    filter_sql = "TRUE"


# ============================================================
# KPI QUERIES
# ============================================================

kpi_query = f"""
SELECT

    COUNT(DISTINCT f.invoice_no) AS total_orders,

    ROUND(
        SUM(f.sales_amount),
        2
    ) AS total_sales,

    ROUND(
        SUM(f.sales_amount)
        / NULLIF(
            COUNT(DISTINCT f.invoice_no),
            0
        ),
        2
    ) AS average_order_value

FROM warehouse.fact_sales f

JOIN warehouse.dim_date d
    ON f.date_key = d.date_key

JOIN warehouse.dim_country c
    ON f.country_key = c.country_key

WHERE {filter_sql};
"""


# ============================================================
# CANCELLATION KPI
# ============================================================

cancellation_query = f"""
SELECT

    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN f.is_cancelled = TRUE
                THEN 1
                ELSE 0
            END
        )
        / NULLIF(COUNT(*), 0),
        2
    ) AS cancellation_rate

FROM warehouse.fact_sales f

JOIN warehouse.dim_date d
    ON f.date_key = d.date_key

JOIN warehouse.dim_country c
    ON f.country_key = c.country_key

WHERE {filter_sql};
"""


# ============================================================
# LOAD KPI DATA
# ============================================================

kpi = run_query(
    kpi_query,
    params
).iloc[0]


cancellation = run_query(
    cancellation_query,
    params
).iloc[0]


# ============================================================
# KPI CARDS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


# -----------------------------
# Revenue
# -----------------------------

with col1:

    total_sales = kpi["total_sales"]

    if pd.isna(total_sales):
        total_sales = 0

    st.metric(
        "💰 Total Revenue",
        f"£{total_sales:,.2f}"
    )


# -----------------------------
# Orders
# -----------------------------

with col2:

    total_orders = kpi["total_orders"]

    if pd.isna(total_orders):
        total_orders = 0

    st.metric(
        "🛒 Total Orders",
        f"{int(total_orders):,}"
    )


# -----------------------------
# Average Order Value
# -----------------------------

with col3:

    average_order_value = kpi["average_order_value"]

    if pd.isna(average_order_value):
        average_order_value = 0

    st.metric(
        "📦 Average Order Value",
        f"£{average_order_value:,.2f}"
    )


# -----------------------------
# Cancellation Rate
# -----------------------------

with col4:

    cancellation_rate = cancellation[
        "cancellation_rate"
    ]

    if pd.isna(cancellation_rate):
        cancellation_rate = 0

    st.metric(
        "❌ Cancellation Rate",
        f"{cancellation_rate:.2f}%"
    )


st.divider()


# ============================================================
# MONTHLY SALES TREND
# ============================================================

monthly_sales_query = f"""
SELECT

    d.year,

    d.month,

    ROUND(
        SUM(f.sales_amount),
        2
    ) AS total_sales

FROM warehouse.fact_sales f

JOIN warehouse.dim_date d
    ON f.date_key = d.date_key

JOIN warehouse.dim_country c
    ON f.country_key = c.country_key

WHERE {filter_sql}

GROUP BY

    d.year,

    d.month

ORDER BY

    d.year,

    d.month;
"""


monthly_sales = run_query(
    monthly_sales_query,
    params
)


if not monthly_sales.empty:

    monthly_sales["period"] = (
        monthly_sales["year"].astype(str)
        + "-"
        + monthly_sales["month"]
        .astype(str)
        .str.zfill(2)
    )


    st.subheader("📈 Monthly Sales Trend")


    st.line_chart(
        monthly_sales.set_index("period")[
            "total_sales"
        ]
    )

else:

    st.subheader("📈 Monthly Sales Trend")

    st.info(
        "No sales data available for the selected filters."
    )


# ============================================================
# TOP PRODUCTS
# ============================================================

top_products_query = f"""
SELECT

    p.stock_code,

    p.description,

    ROUND(
        SUM(f.sales_amount),
        2
    ) AS total_sales

FROM warehouse.fact_sales f

JOIN warehouse.dim_product p
    ON f.product_key = p.product_key

JOIN warehouse.dim_date d
    ON f.date_key = d.date_key

JOIN warehouse.dim_country c
    ON f.country_key = c.country_key

WHERE {filter_sql}

GROUP BY

    p.stock_code,

    p.description

ORDER BY

    total_sales DESC

LIMIT 10;
"""


top_products = run_query(
    top_products_query,
    params
)


# ============================================================
# SALES BY COUNTRY
# ============================================================

country_sales_query = f"""
SELECT

    c.country_name,

    ROUND(
        SUM(f.sales_amount),
        2
    ) AS total_sales

FROM warehouse.fact_sales f

JOIN warehouse.dim_country c
    ON f.country_key = c.country_key

JOIN warehouse.dim_date d
    ON f.date_key = d.date_key

WHERE {filter_sql}

GROUP BY

    c.country_name

ORDER BY

    total_sales DESC

LIMIT 10;
"""


country_sales = run_query(
    country_sales_query,
    params
)


# ============================================================
# PRODUCT + COUNTRY CHARTS
# ============================================================

col1, col2 = st.columns(2)


# -----------------------------
# Top Products
# -----------------------------

with col1:

    st.subheader("🏆 Top 10 Products")

    if not top_products.empty:

        product_chart = top_products[
            ["description", "total_sales"]
        ].copy()

        product_chart = product_chart.set_index(
            "description"
        )

        st.bar_chart(product_chart)

    else:

        st.info(
            "No product data available."
        )


# -----------------------------
# Top Countries
# -----------------------------

with col2:

    st.subheader("🌍 Top 10 Countries")

    if not country_sales.empty:

        country_chart = country_sales[
            ["country_name", "total_sales"]
        ].copy()

        country_chart = country_chart.set_index(
            "country_name"
        )

        st.bar_chart(country_chart)

    else:

        st.info(
            "No country data available."
        )


# ============================================================
# TOP CUSTOMERS
# ============================================================

top_customers_query = f"""
SELECT

    cst.customer_id,

    ROUND(
        SUM(f.sales_amount),
        2
    ) AS total_sales

FROM warehouse.fact_sales f

JOIN warehouse.dim_customer cst
    ON f.customer_key = cst.customer_key

JOIN warehouse.dim_date d
    ON f.date_key = d.date_key

JOIN warehouse.dim_country c
    ON f.country_key = c.country_key

WHERE {filter_sql}

GROUP BY

    cst.customer_id

ORDER BY

    total_sales DESC

LIMIT 10;
"""


top_customers = run_query(
    top_customers_query,
    params
)


# ============================================================
# CUSTOMER CHART
# ============================================================

st.subheader("👤 Top 10 Customers")


if not top_customers.empty:

    customer_chart = top_customers[
        ["customer_id", "total_sales"]
    ].copy()

    customer_chart["customer_id"] = (
        customer_chart["customer_id"]
        .astype(str)
    )

    customer_chart = customer_chart.set_index(
        "customer_id"
    )

    st.bar_chart(customer_chart)

else:

    st.info(
        "No customer data available."
    )


# ============================================================
# CANCELLATION ANALYSIS
# ============================================================

cancellation_chart_query = f"""
SELECT

    CASE
        WHEN f.is_cancelled = TRUE
        THEN 'Cancelled'
        ELSE 'Normal'
    END AS transaction_status,

    COUNT(*) AS transaction_count

FROM warehouse.fact_sales f

JOIN warehouse.dim_date d
    ON f.date_key = d.date_key

JOIN warehouse.dim_country c
    ON f.country_key = c.country_key

WHERE
    (
        {filter_sql}
    )

GROUP BY

    f.is_cancelled

ORDER BY

    f.is_cancelled;
"""


cancellation_data = run_query(
    cancellation_chart_query,
    params
)


# ============================================================
# CANCELLATION CHART
# ============================================================

st.subheader("❌ Transaction Status")


if not cancellation_data.empty:

    cancellation_chart = cancellation_data[
        [
            "transaction_status",
            "transaction_count"
        ]
    ].set_index(
        "transaction_status"
    )

    st.bar_chart(
        cancellation_chart
    )

else:

    st.info(
        "No transaction status data available."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Sales Data ETL Pipeline & Analytics Platform | "
    "Python • Pandas • PostgreSQL • SQL • Streamlit"
)