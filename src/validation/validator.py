from pathlib import Path

import pandas as pd

from src.utils.logger import get_logger


logger = get_logger("DataValidator")


class DataValidator:

    REQUIRED_COLUMNS = [
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "Country",
    ]

    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

        # Store invalid records as a DataFrame
        self.error_records = pd.DataFrame()

        # Data quality metrics
        self.report = {
            "input_rows": len(self.df),
            "missing_invoice_no": 0,
            "missing_stock_code": 0,
            "missing_description": 0,
            "missing_customer_id": 0,
            "missing_country": 0,
            "zero_quantity": 0,
            "negative_quantity": 0,
            "negative_unit_price": 0,
            "invalid_invoice_date": 0,
            "duplicate_rows": 0,
            "duplicate_rows_removed": 0,
            "cancelled_transactions": 0,
        }

    def validate_columns(self):
        logger.info("Checking required columns")

        missing_columns = [
            column
            for column in self.REQUIRED_COLUMNS
            if column not in self.df.columns
        ]

        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            raise ValueError(
                f"Missing required columns: {missing_columns}"
            )

        logger.info("All required columns are present")

    def check_missing_values(self):
        logger.info("Checking missing values")

        self.report["missing_invoice_no"] = (
            self.df["InvoiceNo"].isna().sum()
        )

        self.report["missing_stock_code"] = (
            self.df["StockCode"].isna().sum()
        )

        self.report["missing_description"] = (
            self.df["Description"].isna().sum()
        )

        self.report["missing_customer_id"] = (
            self.df["CustomerID"].isna().sum()
        )

        self.report["missing_country"] = (
            self.df["Country"].isna().sum()
        )

    def check_quantity(self):
        logger.info("Checking quantity values")

        self.report["zero_quantity"] = (
            self.df["Quantity"] == 0
        ).sum()

        self.report["negative_quantity"] = (
            self.df["Quantity"] < 0
        ).sum()

    def check_unit_price(self):
        logger.info("Checking unit prices")

        self.report["negative_unit_price"] = (
            self.df["UnitPrice"] < 0
        ).sum()

    def check_invoice_date(self):
        logger.info("Checking invoice dates")

        converted_dates = pd.to_datetime(
            self.df["InvoiceDate"],
            errors="coerce"
        )

        self.report["invalid_invoice_date"] = (
            converted_dates.isna().sum()
        )

        self.df["InvoiceDate"] = converted_dates

    def check_duplicates(self):
        logger.info("Checking duplicate records")

        self.report["duplicate_rows"] = (
            self.df.duplicated().sum()
        )

    def check_cancellations(self):
        logger.info("Checking cancelled transactions")

        cancelled = (
            self.df["InvoiceNo"]
            .astype(str)
            .str.startswith("C")
        )

        self.report["cancelled_transactions"] = (
            cancelled.sum()
        )

    def collect_errors(self):
        logger.info("Collecting invalid records")

        error_mask = (
            self.df["InvoiceNo"].isna()
            | self.df["StockCode"].isna()
            | self.df["Country"].isna()
            | (self.df["Quantity"] == 0)
            | (self.df["UnitPrice"] < 0)
            | self.df["InvoiceDate"].isna()
        )

        errors = self.df[error_mask].copy()

        if not errors.empty:

            errors["error_reason"] = ""

            errors.loc[
                errors["InvoiceNo"].isna(),
                "error_reason"
            ] += "Missing InvoiceNo; "

            errors.loc[
                errors["StockCode"].isna(),
                "error_reason"
            ] += "Missing StockCode; "

            errors.loc[
                errors["Country"].isna(),
                "error_reason"
            ] += "Missing Country; "

            errors.loc[
                errors["Quantity"] == 0,
                "error_reason"
            ] += "Zero Quantity; "

            errors.loc[
                errors["UnitPrice"] < 0,
                "error_reason"
            ] += "Negative UnitPrice; "

            errors.loc[
                errors["InvoiceDate"].isna(),
                "error_reason"
            ] += "Invalid InvoiceDate; "

            self.error_records = errors

        logger.info(
            f"Invalid records identified: {len(errors):,}"
        )

    def remove_invalid_records(self):
        logger.info("Removing invalid records")

        before = len(self.df)

        valid_mask = (
            self.df["InvoiceNo"].notna()
            & self.df["StockCode"].notna()
            & self.df["Country"].notna()
            & (self.df["Quantity"] != 0)
            & (self.df["UnitPrice"] >= 0)
            & self.df["InvoiceDate"].notna()
        )

        self.df = self.df[valid_mask].copy()

        after = len(self.df)

        removed = before - after

        logger.info(f"Rows removed: {removed:,}")
        logger.info(f"Valid rows remaining: {after:,}")

    def remove_duplicates(self):
        logger.info("Starting duplicate analysis")

        before = len(self.df)

        duplicate_count = self.df.duplicated().sum()

        logger.info(
            f"Duplicate rows detected after validation: "
            f"{duplicate_count:,}"
        )

        if duplicate_count > 0:
            self.df = self.df.drop_duplicates().copy()

        after = len(self.df)

        removed = before - after

        self.report["duplicate_rows_removed"] = removed

        logger.info(
            f"Exact duplicate rows removed: {removed:,}"
        )

        logger.info(
            f"Rows remaining after deduplication: {after:,}"
        )

    def save_errors(self, output_path):
        if self.error_records.empty:
            logger.info("No validation errors to save")
            return

        errors_df = self.error_records.copy()

        output_path = Path(output_path)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        errors_df.to_csv(
            output_path,
            index=False
        )

        logger.info(
            f"Validation errors saved to {output_path}"
        )

    def print_report(self):

        final_rows = len(self.df)

        removed_invalid = (
            self.report["input_rows"]
            - final_rows
            - self.report["duplicate_rows_removed"]
        )

        print("\n")
        print("=" * 55)
        print("              DATA QUALITY REPORT")
        print("=" * 55)

        print(
            f"Input rows:                  "
            f"{self.report['input_rows']:,}"
        )

        print(
            f"Missing InvoiceNo:           "
            f"{self.report['missing_invoice_no']:,}"
        )

        print(
            f"Missing StockCode:           "
            f"{self.report['missing_stock_code']:,}"
        )

        print(
            f"Missing Description:         "
            f"{self.report['missing_description']:,}"
        )

        print(
            f"Missing CustomerID:          "
            f"{self.report['missing_customer_id']:,}"
        )

        print(
            f"Missing Country:             "
            f"{self.report['missing_country']:,}"
        )

        print(
            f"Zero Quantity:               "
            f"{self.report['zero_quantity']:,}"
        )

        print(
            f"Negative Quantity:           "
            f"{self.report['negative_quantity']:,}"
        )

        print(
            f"Negative UnitPrice:          "
            f"{self.report['negative_unit_price']:,}"
        )

        print(
            f"Invalid InvoiceDate:         "
            f"{self.report['invalid_invoice_date']:,}"
        )

        print(
            f"Duplicate rows detected:     "
            f"{self.report['duplicate_rows']:,}"
        )

        print(
            f"Duplicate rows removed:      "
            f"{self.report['duplicate_rows_removed']:,}"
        )

        print(
            f"Cancelled transactions:      "
            f"{self.report['cancelled_transactions']:,}"
        )

        print(
            f"Invalid rows removed:        "
            f"{removed_invalid:,}"
        )

        print(
            f"Final valid rows:            "
            f"{final_rows:,}"
        )

        print("=" * 55)
        print()

    def validate(self):

        logger.info(
            "========== VALIDATION STARTED =========="
        )

        self.validate_columns()

        self.check_missing_values()

        self.check_quantity()

        self.check_unit_price()

        self.check_invoice_date()

        self.check_duplicates()

        self.check_cancellations()

        self.collect_errors()

        self.remove_invalid_records()

        self.remove_duplicates()

        self.print_report()

        logger.info(
            "========== VALIDATION COMPLETED =========="
        )

        return self.df