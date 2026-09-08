import pandas as pd

from src.utils.logger import get_logger


logger = get_logger("DataProfiler")


def profile_dataframe(df: pd.DataFrame):

    logger.info("Starting data profiling")

    print("\n========== DATA PROFILE ==========\n")

    print(f"Rows: {len(df):,}")

    print(f"Columns: {len(df.columns)}")

    print("\nColumn names:")

    for column in df.columns:

        print(f" - {column}")

    print("\nData types:")

    print(df.dtypes)

    print("\nMissing values:")

    missing = df.isnull().sum()

    print(missing)

    print("\nDuplicate rows:")

    print(df.duplicated().sum())

    print("\n==================================\n")