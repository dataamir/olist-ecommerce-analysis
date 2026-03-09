"""
db_connect.py
-------------
dataamir — Olist E-Commerce Analysis

Utility functions for connecting to different databases.
Supports SQLite (local), PostgreSQL, and querying via SQLAlchemy.

Usage example:
    from src.db_connect import get_sqlite_engine, load_all_to_db, query

    engine = get_sqlite_engine()
    load_all_to_db(engine, tables_dict)
    df = query(engine, "SELECT * FROM orders LIMIT 10")
"""

import pandas as pd
import os
import sqlite3


# ── SQLite (local, no setup needed) ──────────────────────────────────────────
def get_sqlite_engine(db_path: str = './data/olist.db'):
    """
    Get a connection to a local SQLite database.
    Creates the .db file if it doesn't exist.
    """
    from sqlalchemy import create_engine
    engine = create_engine(f'sqlite:///{db_path}')
    print(f'Connected to SQLite: {db_path}')
    return engine


# ── PostgreSQL (local or cloud) ───────────────────────────────────────────────
def get_postgres_engine(
    host:     str = 'localhost',
    port:     int = 5432,
    dbname:   str = 'olist_db',
    user:     str = 'postgres',
    password: str = None,
    ssl:      bool = False,
):
    """
    Connect to a PostgreSQL database.
    For cloud databases (Supabase, RDS etc.) set ssl=True.

    Better practice: store credentials in a .env file and load with python-dotenv.
    """
    from sqlalchemy import create_engine

    if password is None:
        # try to get from environment variable
        password = os.getenv('DB_PASSWORD', '')

    conn_str = f'postgresql://{user}:{password}@{host}:{port}/{dbname}'
    kwargs   = {'connect_args': {'sslmode': 'require'}} if ssl else {}

    engine = create_engine(conn_str, **kwargs)
    print(f'Connected to PostgreSQL: {host}:{port}/{dbname}')
    return engine


# ── Load CSVs into DB ─────────────────────────────────────────────────────────
def load_all_to_db(engine, tables: dict, if_exists: str = 'replace'):
    """
    Write all DataFrames in the tables dict to the database.
    Default if_exists='replace' drops and recreates each table.
    Use if_exists='append' to add rows to existing tables.
    """
    for name, df in tables.items():
        df.to_sql(name, engine, if_exists=if_exists, index=False, chunksize=5000)
        print(f'  {name:20s} -> {len(df):,} rows written')
    print('Done loading tables.')


# ── Run a query and return a DataFrame ────────────────────────────────────────
def query(engine, sql: str) -> pd.DataFrame:
    """Execute SQL and return results as a pandas DataFrame."""
    return pd.read_sql(sql, engine)


# ── Useful pre-built queries ──────────────────────────────────────────────────
QUERIES = {

    'revenue_by_state': """
        SELECT
            c.customer_state                    AS state,
            COUNT(DISTINCT o.order_id)          AS total_orders,
            ROUND(SUM(i.price + i.freight_value), 2) AS total_revenue,
            ROUND(AVG(r.review_score), 2)       AS avg_score
        FROM   orders       o
        JOIN   customers    c  ON o.customer_id  = c.customer_id
        JOIN   order_items  i  ON o.order_id     = i.order_id
        LEFT JOIN reviews   r  ON o.order_id     = r.order_id
        WHERE  o.order_status = 'delivered'
        GROUP  BY c.customer_state
        ORDER  BY total_revenue DESC
    """,

    'top_categories': """
        SELECT
            ct.product_category_name_english    AS category,
            COUNT(*)                            AS units_sold,
            ROUND(AVG(i.price), 2)              AS avg_price,
            ROUND(AVG(r.review_score), 2)       AS avg_score
        FROM   order_items  i
        JOIN   products     p  ON i.product_id  = p.product_id
        JOIN   categories   ct ON p.product_category_name = ct.product_category_name
        LEFT JOIN reviews   r  ON i.order_id    = r.order_id
        GROUP  BY ct.product_category_name_english
        ORDER  BY units_sold DESC
        LIMIT  20
    """,

    'late_delivery_rate': """
        SELECT
            c.customer_state,
            COUNT(*)                            AS total_orders,
            SUM(CASE WHEN o.order_delivered_customer_date
                          > o.order_estimated_delivery_date
                     THEN 1 ELSE 0 END)         AS late_orders,
            ROUND(100.0 * SUM(CASE WHEN o.order_delivered_customer_date
                                       > o.order_estimated_delivery_date
                                  THEN 1 ELSE 0 END) / COUNT(*), 1) AS late_pct
        FROM   orders    o
        JOIN   customers c ON o.customer_id = c.customer_id
        WHERE  o.order_status = 'delivered'
          AND  o.order_delivered_customer_date IS NOT NULL
        GROUP  BY c.customer_state
        ORDER  BY late_pct DESC
    """,
}


# ── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('db_connect.py — quick demo\n')

    # demo with SQLite
    engine = get_sqlite_engine('./data/olist.db')

    print('\nAvailable pre-built queries:')
    for name in QUERIES:
        print(f'  {name}')

    print('\nTo run a query:')
    print('  df = query(engine, QUERIES["revenue_by_state"])')
    print('  print(df.head())')
