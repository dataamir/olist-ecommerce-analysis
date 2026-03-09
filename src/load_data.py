"""
load_data.py
------------
Functions to load all the Olist CSV files and join them into
one big master table for analysis.

I put these in a separate file so I don't have to copy-paste
the same loading code into every notebook.
"""

import os
import pandas as pd


# The 9 CSV files that come with the Olist dataset
OLIST_FILES = {
    'orders':       'olist_orders_dataset.csv',
    'order_items':  'olist_order_items_dataset.csv',
    'products':     'olist_products_dataset.csv',
    'customers':    'olist_customers_dataset.csv',
    'sellers':      'olist_sellers_dataset.csv',
    'reviews':      'olist_order_reviews_dataset.csv',
    'payments':     'olist_order_payments_dataset.csv',
    'geolocation':  'olist_geolocation_dataset.csv',
    'categories':   'product_category_name_translation.csv',
}


def load_all_tables(data_path='./data/raw/'):
    """
    Reads all 9 CSV files into a dictionary of DataFrames.
    
    Parameters
    ----------
    data_path : str
        Folder where the Kaggle CSVs are saved.
    
    Returns
    -------
    dict of {str: pd.DataFrame}
    
    Example
    -------
    tables = load_all_tables('./data/raw/')
    orders = tables['orders']
    """
    tables = {}
    
    for name, filename in OLIST_FILES.items():
        filepath = os.path.join(data_path, filename)
        
        if not os.path.exists(filepath):
            print(f"  [!] Missing: {filename} — skipping")
            continue
        
        tables[name] = pd.read_csv(filepath)
        print(f"  ✓  Loaded '{name}' → {tables[name].shape[0]:,} rows")
    
    return tables


def build_master_table(tables):
    """
    Joins the main tables together into one wide DataFrame
    that's easy to run analysis on.
    
    I join orders → items → customers → products → reviews → categories.
    Geolocation is left out here because it's huge and I only need
    city/state which is already in the customers table.
    
    Parameters
    ----------
    tables : dict
        Output from load_all_tables()
    
    Returns
    -------
    pd.DataFrame
        One row per order-item with all the info attached.
    """
    # Start from orders — this is the core table
    master = tables['orders'].copy()
    
    # Attach the items (what was actually bought)
    master = master.merge(tables['order_items'], on='order_id', how='left')
    
    # Attach customer info (city, state)
    master = master.merge(tables['customers'], on='customer_id', how='left')
    
    # Attach product details
    master = master.merge(tables['products'], on='product_id', how='left')
    
    # Attach reviews — just the score column, I don't need the text for now
    reviews_slim = tables['reviews'][['order_id', 'review_score']].drop_duplicates('order_id')
    master = master.merge(reviews_slim, on='order_id', how='left')
    
    # Translate category names from Portuguese to English
    master = master.merge(tables['categories'], on='product_category_name', how='left')
    
    print(f"\nMaster table built: {master.shape[0]:,} rows × {master.shape[1]} columns")
    return master


def load_from_sqlite(db_path='./data/olist.db', query=None):
    """
    Load data from a SQLite database instead of CSVs.
    Useful after you've already loaded the data once with save_to_sqlite().
    
    Parameters
    ----------
    db_path : str
    query   : str, optional SQL query. Defaults to loading the full orders table.
    
    Returns
    -------
    pd.DataFrame
    """
    import sqlite3
    
    if query is None:
        query = "SELECT * FROM orders LIMIT 1000"
    
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def save_to_sqlite(tables, db_path='./data/olist.db'):
    """
    Save all loaded DataFrames into a SQLite database file.
    Only need to run this once — then you can query it with SQL.
    
    Parameters
    ----------
    tables  : dict of DataFrames
    db_path : str — where to save the .db file
    """
    import sqlite3
    
    conn = sqlite3.connect(db_path)
    for name, df in tables.items():
        df.to_sql(name, conn, if_exists='replace', index=False)
        print(f"  ✓  Saved '{name}' to SQLite")
    conn.close()
    print(f"\nDatabase saved to: {db_path}")
