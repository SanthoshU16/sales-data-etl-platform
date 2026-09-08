from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.database.connection import get_engine
from src.utils.logger import get_logger


logger = get_logger("WarehouseLoader")


class WarehouseLoader:

    def __init__(self, processed_file):
        self.processed_file = Path(processed_file)
        self.engine = get_engine()

    # --------------------------------------------------
    # 1. LOAD PROCESSED DATA
    # --------------------------------------------------

    def load_data(self):
        """Read the processed CSV file."""

        logger.info(
            f"Loading processed file: {self.processed_file}"
        )

        if not self.processed_file.exists():
            raise FileNotFoundError(
                f"Processed file not found: {self.processed_file}"
            )

        df = pd.read_csv(self.processed_file)

        logger.info(
            f"Processed data loaded: {len(df):,} rows"
        )

        return df

    # --------------------------------------------------
    # 2. CLEAR EXISTING WAREHOUSE DATA
    # --------------------------------------------------

    def clear_warehouse(self):
        """
        Clear existing warehouse data before loading.

        This makes the ETL pipeline repeatable.
        """

        logger.info("Clearing existing warehouse data")

        with self.engine.begin() as connection:

            connection.execute(
                text(
                    """
                    TRUNCATE TABLE
                        warehouse.fact_sales,
                        warehouse.dim_customer,
                        warehouse.dim_product,
                        warehouse.dim_country,
                        warehouse.dim_date
                    RESTART IDENTITY CASCADE;
                    """
                )
            )

        logger.info("Existing warehouse data cleared")

    # --------------------------------------------------
    # 3. LOAD CUSTOMER DIMENSION
    # --------------------------------------------------

    def load_customers(self, df):
        """Load unique customers into dim_customer."""

        logger.info("Loading dim_customer")

        customers = (
            df[["customer_id"]]
            .dropna()
            .drop_duplicates()
            .copy()
        )

        customers["customer_id"] = (
            customers["customer_id"]
            .astype(int)
        )

        customers.to_sql(
            "dim_customer",
            self.engine,
            schema="warehouse",
            if_exists="append",
            index=False,
            method="multi"
        )

        logger.info(
            f"Customers loaded: {len(customers):,}"
        )

    # --------------------------------------------------
    # 4. LOAD PRODUCT DIMENSION
    # --------------------------------------------------

    def load_products(self, df):
        """Load unique products into dim_product."""

        logger.info("Loading dim_product")

        products = (
            df[["stock_code", "description"]]
            .drop_duplicates(subset=["stock_code"])
            .copy()
        )

        products.to_sql(
            "dim_product",
            self.engine,
            schema="warehouse",
            if_exists="append",
            index=False,
            method="multi"
        )

        logger.info(
            f"Products loaded: {len(products):,}"
        )

    # --------------------------------------------------
    # 5. LOAD COUNTRY DIMENSION
    # --------------------------------------------------

    def load_countries(self, df):
        """Load unique countries into dim_country."""

        logger.info("Loading dim_country")

        countries = (
            df[["country"]]
            .drop_duplicates()
            .copy()
        )

        countries = countries.rename(
            columns={
                "country": "country_name"
            }
        )

        countries.to_sql(
            "dim_country",
            self.engine,
            schema="warehouse",
            if_exists="append",
            index=False,
            method="multi"
        )

        logger.info(
            f"Countries loaded: {len(countries):,}"
        )

    # --------------------------------------------------
    # 6. LOAD DATE DIMENSION
    # --------------------------------------------------

    def load_dates(self, df):
        """Create and load date dimension."""

        logger.info("Loading dim_date")

        dates = (
            pd.to_datetime(
                df["invoice_date"]
            )
            .dt.normalize()
            .drop_duplicates()
        )

        date_df = pd.DataFrame({
            "full_date": dates
        })

        date_df["date_key"] = (
            date_df["full_date"]
            .dt.strftime("%Y%m%d")
            .astype(int)
        )

        date_df["day"] = (
            date_df["full_date"].dt.day
        )

        date_df["month"] = (
            date_df["full_date"].dt.month
        )

        date_df["month_name"] = (
            date_df["full_date"]
            .dt.month_name()
        )

        date_df["quarter"] = (
            date_df["full_date"].dt.quarter
        )

        date_df["year"] = (
            date_df["full_date"].dt.year
        )

        date_df["week"] = (
            date_df["full_date"]
            .dt.isocalendar()
            .week
            .astype(int)
        )

        date_df = date_df[
            [
                "date_key",
                "full_date",
                "day",
                "month",
                "month_name",
                "quarter",
                "year",
                "week",
            ]
        ]

        date_df.to_sql(
            "dim_date",
            self.engine,
            schema="warehouse",
            if_exists="append",
            index=False,
            method="multi"
        )

        logger.info(
            f"Dates loaded: {len(date_df):,}"
        )

    # --------------------------------------------------
    # 7. GET DIMENSION KEYS
    # --------------------------------------------------

    def get_dimension_keys(self):
        """Retrieve surrogate keys from PostgreSQL."""

        logger.info("Retrieving dimension keys")

        with self.engine.connect() as connection:

            customers = pd.read_sql(
                text(
                    """
                    SELECT
                        customer_key,
                        customer_id
                    FROM warehouse.dim_customer
                    """
                ),
                connection
            )

            products = pd.read_sql(
                text(
                    """
                    SELECT
                        product_key,
                        stock_code
                    FROM warehouse.dim_product
                    """
                ),
                connection
            )

            countries = pd.read_sql(
                text(
                    """
                    SELECT
                        country_key,
                        country_name
                    FROM warehouse.dim_country
                    """
                ),
                connection
            )

            dates = pd.read_sql(
                text(
                    """
                    SELECT
                        date_key,
                        full_date
                    FROM warehouse.dim_date
                    """
                ),
                connection
            )

        return (
            customers,
            products,
            countries,
            dates
        )

    # --------------------------------------------------
    # 8. BUILD FACT TABLE
    # --------------------------------------------------

    def load_fact_sales(self, df):
        """Build and load the fact_sales table."""

        logger.info("Preparing fact_sales")

        (
            customers,
            products,
            countries,
            dates,
        ) = self.get_dimension_keys()

        # ----------------------------------------------
        # Standardize dimension key data types
        # ----------------------------------------------

        customers["customer_id"] = (
            customers["customer_id"]
            .astype(int)
        )

        products["stock_code"] = (
            products["stock_code"]
            .astype(str)
        )

        countries["country_name"] = (
            countries["country_name"]
            .astype(str)
        )

        dates["full_date"] = pd.to_datetime(
            dates["full_date"]
        )

        # ----------------------------------------------
        # Standardize fact data types
        # ----------------------------------------------

        df["stock_code"] = (
            df["stock_code"]
            .astype(str)
        )

        df["country"] = (
            df["country"]
            .astype(str)
        )

        df["full_date"] = (
            pd.to_datetime(
                df["invoice_date"]
            )
            .dt.normalize()
        )

        # ----------------------------------------------
        # Product key lookup
        # ----------------------------------------------

        df = df.merge(
            products,
            on="stock_code",
            how="left"
        )

        # ----------------------------------------------
        # Customer key lookup
        # ----------------------------------------------

        df = df.merge(
            customers,
            on="customer_id",
            how="left"
        )

        # ----------------------------------------------
        # Country key lookup
        # ----------------------------------------------

        df = df.merge(
            countries,
            left_on="country",
            right_on="country_name",
            how="left"
        )

        # ----------------------------------------------
        # Date key lookup
        # ----------------------------------------------

        df = df.merge(
            dates,
            on="full_date",
            how="left"
        )

        # ----------------------------------------------
        # Validate foreign keys
        # ----------------------------------------------

        missing_products = df["product_key"].isna().sum()
        missing_dates = df["date_key"].isna().sum()
        missing_countries = df["country_key"].isna().sum()

        logger.info(
            f"Missing product keys: {missing_products:,}"
        )

        logger.info(
            f"Missing date keys: {missing_dates:,}"
        )

        logger.info(
            f"Missing country keys: {missing_countries:,}"
        )

        if missing_products > 0:
            raise ValueError(
                "Some products could not be mapped "
                "to dim_product."
            )

        if missing_dates > 0:
            raise ValueError(
                "Some dates could not be mapped "
                "to dim_date."
            )

        if missing_countries > 0:
            raise ValueError(
                "Some countries could not be mapped "
                "to dim_country."
            )

        # ----------------------------------------------
        # Select fact table columns
        # ----------------------------------------------

        fact_sales = df[
            [
                "invoice_no",
                "product_key",
                "customer_key",
                "date_key",
                "country_key",
                "quantity",
                "unit_price",
                "sales_amount",
                "is_cancelled",
            ]
        ].copy()

        logger.info(
            f"Fact records prepared: "
            f"{len(fact_sales):,}"
        )

        # ----------------------------------------------
        # Load fact table in chunks
        # ----------------------------------------------

        fact_sales.to_sql(
            "fact_sales",
            self.engine,
            schema="warehouse",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=5000
        )

        logger.info(
            f"Fact sales loaded: "
            f"{len(fact_sales):,}"
        )

    # --------------------------------------------------
    # 9. RUN COMPLETE WAREHOUSE LOAD
    # --------------------------------------------------

    def run(self):
        """Run the complete warehouse loading process."""

        logger.info(
            "========== WAREHOUSE LOAD STARTED =========="
        )

        try:

            df = self.load_data()

            # Make pipeline repeatable
            self.clear_warehouse()

            # Load dimensions
            self.load_customers(df)

            self.load_products(df)

            self.load_countries(df)

            self.load_dates(df)

            # Load fact table
            self.load_fact_sales(df)

            logger.info(
                "========== WAREHOUSE LOAD COMPLETED =========="
            )

        except Exception as error:

            logger.error(
                f"Warehouse load failed: {error}"
            )

            raise