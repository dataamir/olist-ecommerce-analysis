"""
db.py
-----
Database connection helpers for the Olist analytics project.
Supports SQLite (local dev) and PostgreSQL (production).
"""

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()


def get_sqlite_engine(db_path: str = "./data/olist.db"):
    """Return a SQLAlchemy engine connected to a local SQLite database."""
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    print(f"[db] Connected to SQLite: {db_path}")
    return engine


def get_postgres_engine():
    """
    Return a SQLAlchemy engine connected to PostgreSQL.
    Reads DATABASE_URL from .env file.

    Expected .env format:
        DATABASE_URL=postgresql://user:password@localhost:5432/olist_db
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise EnvironmentError(
            "DATABASE_URL not set. Add it to your .env file.\n"
            "Example: DATABASE_URL=postgresql://user:pass@localhost:5432/olist_db"
        )
    engine = create_engine(db_url, echo=False)
    print("[db] Connected to PostgreSQL")
    return engine


def load_csv_to_db(tables: dict, engine, if_exists: str = "replace", chunksize: int = 5000):
    """
    Load a dict of {table_name: DataFrame} into the connected database.

    Args:
        tables    : dict of {str: pd.DataFrame}
        engine    : SQLAlchemy engine
        if_exists : 'replace' | 'append' | 'fail'
        chunksize : rows per insert batch
    """
    for name, df in tables.items():
        df.to_sql(name, engine, if_exists=if_exists, index=False, chunksize=chunksize)
        print(f"  [ok] Loaded '{name}' ({len(df):,} rows)")
    print("[db] All tables loaded successfully.")


def query(sql: str, engine) -> pd.DataFrame:
    """Run a SQL query and return results as a DataFrame."""
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


def list_tables(engine) -> list:
    """Return list of table names in the connected database."""
    with engine.connect() as conn:
        if "sqlite" in str(engine.url):
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        else:
            result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
        return [row[0] for row in result]
