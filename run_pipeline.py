import os
from pathlib import Path

from dotenv import load_dotenv

from src.loading.warehouse_loader import WarehouseLoader
from src.extraction.excel_reader import ExcelReader
from src.extraction.profiler import profile_dataframe
from src.validation.validator import DataValidator
from src.transformation.transformer import DataTransformer


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / os.getenv(
    "DATA_FILE"
)

PROCESSED_DIR = (
    BASE_DIR / "data" / "processed"
)

ERROR_DIR = (
    BASE_DIR / "data" / "errors"
)

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)

ERROR_DIR.mkdir(
    parents=True,
    exist_ok=True
)

PROCESSED_FILE = (
    PROCESSED_DIR / "sales_processed.csv"
)

ERROR_FILE = (
    ERROR_DIR / "validation_errors.csv"
)


# --------------------------------------------------
# Main ETL pipeline
# --------------------------------------------------

def main():

    print("\n")
    print("=" * 55)
    print("        SALES DATA ETL PIPELINE")
    print("=" * 55)

    # --------------------------------------------------
    # 1. EXTRACTION
    # --------------------------------------------------

    print("\n[1/5] Extracting data...")

    reader = ExcelReader(DATA_FILE)

    df = reader.extract()

    profile_dataframe(df)

    # --------------------------------------------------
    # 2. VALIDATION
    # --------------------------------------------------

    print("\n[2/5] Validating data...")

    validator = DataValidator(df)

    validated_df = validator.validate()

    validator.save_errors(ERROR_FILE)

    # --------------------------------------------------
    # 3. TRANSFORMATION
    # --------------------------------------------------

    print("\n[3/5] Transforming data...")

    transformer = DataTransformer(validated_df)

    transformed_df = transformer.transform()

    # --------------------------------------------------
    # 4. SAVE PROCESSED DATA
    # --------------------------------------------------

    print("\n[4/5] Saving processed data...")

    transformed_df.to_csv(
        PROCESSED_FILE,
        index=False
    )

    # --------------------------------------------------
    # 5. LOAD INTO DATA WAREHOUSE
    # --------------------------------------------------

    print("\n[5/5] Loading data into PostgreSQL warehouse...")

    loader = WarehouseLoader(PROCESSED_FILE)

    loader.run()

    # --------------------------------------------------
    # Pipeline completed
    # --------------------------------------------------

    print("\n")
    print("=" * 55)
    print("           PIPELINE COMPLETED")
    print("=" * 55)

    print(
        f"Processed rows: "
        f"{len(transformed_df):,}"
    )

    print(
        f"Processed file:\n"
        f"{PROCESSED_FILE}"
    )

    if ERROR_FILE.exists():

        print(
            f"Validation errors:\n"
            f"{ERROR_FILE}"
        )

    print("=" * 55)
    print()


if __name__ == "__main__":
    main()