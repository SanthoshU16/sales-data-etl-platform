from pathlib import Path

import pandas as pd

from src.utils.logger import get_logger


logger = get_logger("ExcelReader")


class ExcelReader:

    def __init__(self, file_path: str):

        self.file_path = Path(file_path)

    def validate_file(self):

        if not self.file_path.exists():

            raise FileNotFoundError(
                f"Source file not found: {self.file_path}"
            )

        if self.file_path.suffix.lower() != ".xlsx":

            raise ValueError(
                "Expected an .xlsx file"
            )

    def extract(self) -> pd.DataFrame:

        logger.info(
            f"Starting extraction: {self.file_path.name}"
        )

        self.validate_file()

        try:

            df = pd.read_excel(
                self.file_path,
                engine="openpyxl"
            )

        except Exception as error:

            logger.error(
                f"Failed to read Excel file: {error}"
            )

            raise

        logger.info(
            f"Successfully extracted {len(df):,} rows"
        )

        logger.info(
            f"Columns detected: {list(df.columns)}"
        )

        return df