import pandas as pd

from src.utils.logger import get_logger


logger = get_logger("DataTransformer")


class DataTransformer:

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    # --------------------------------------------------
    # Clean text
    # --------------------------------------------------

    def clean_text(self):

        logger.info("Cleaning text fields")

        self.df["Description"] = (
            self.df["Description"]
            .fillna("Unknown Product")
            .astype(str)
            .str.strip()
        )

        self.df["Country"] = (
            self.df["Country"]
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------
    # Create cancellation flag
    # --------------------------------------------------

    def add_cancelled_flag(self):

        logger.info("Creating cancellation flag")

        self.df["is_cancelled"] = (
            self.df["InvoiceNo"]
            .astype(str)
            .str.startswith("C")
        )

    # --------------------------------------------------
    # Calculate sales amount
    # --------------------------------------------------

    def calculate_sales_amount(self):

        logger.info("Calculating sales amount")

        self.df["sales_amount"] = (
            self.df["Quantity"] *
            self.df["UnitPrice"]
        )

    # --------------------------------------------------
    # Standardize data types
    # --------------------------------------------------

    def standardize_types(self):

        logger.info("Standardizing data types")

        self.df["InvoiceNo"] = (
            self.df["InvoiceNo"]
            .astype(str)
            .str.strip()
        )

        self.df["StockCode"] = (
            self.df["StockCode"]
            .astype(str)
            .str.strip()
        )

        self.df["Country"] = (
            self.df["Country"]
            .astype(str)
            .str.strip()
        )

    # --------------------------------------------------
    # Rename columns
    # --------------------------------------------------

    def standardize_columns(self):

        logger.info("Standardizing column names")

        self.df = self.df.rename(
            columns={
                "InvoiceNo": "invoice_no",
                "StockCode": "stock_code",
                "Description": "description",
                "Quantity": "quantity",
                "InvoiceDate": "invoice_date",
                "UnitPrice": "unit_price",
                "CustomerID": "customer_id",
                "Country": "country",
            }
        )

    # --------------------------------------------------
    # Reorder columns
    # --------------------------------------------------

    def reorder_columns(self):

        columns = [
            "invoice_no",
            "stock_code",
            "description",
            "quantity",
            "invoice_date",
            "unit_price",
            "customer_id",
            "country",
            "is_cancelled",
            "sales_amount",
        ]

        self.df = self.df[columns]

    # --------------------------------------------------
    # Main transformation pipeline
    # --------------------------------------------------

    def transform(self):

        logger.info("========== TRANSFORMATION STARTED ==========")

        self.clean_text()

        self.add_cancelled_flag()

        self.calculate_sales_amount()

        self.standardize_types()

        self.standardize_columns()

        self.reorder_columns()

        logger.info(
            f"Transformation completed. "
            f"Rows: {len(self.df):,}"
        )

        logger.info("========== TRANSFORMATION COMPLETED ==========")

        return self.df