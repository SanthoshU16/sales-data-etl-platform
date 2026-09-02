import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


def get_database_url():
    return (
        f"postgresql+psycopg2://"
        f"{os.getenv('POSTGRES_USER')}:"
        f"{os.getenv('POSTGRES_PASSWORD')}@"
        f"{os.getenv('POSTGRES_HOST')}:"
        f"{os.getenv('POSTGRES_PORT')}/"
        f"{os.getenv('POSTGRES_DB')}"
    )


def get_engine():
    return create_engine(get_database_url())


def test_connection():
    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("Database connection successful!")
        print("Result:", result.scalar())


if __name__ == "__main__":
    test_connection()