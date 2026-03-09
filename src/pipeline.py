"""
pipeline.py
-----------
dataamir — Olist E-Commerce Analysis

This script runs the full data pipeline end-to-end:
  1. Loads all CSV files from data/raw/
  2. Cleans and joins them into one master table
  3. Runs RFM segmentation
  4. Saves processed outputs to data/processed/

Run from the project root:
    python src/pipeline.py
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


# ── Config ──────────────────────────────────────────────────────────────────
RAW_PATH  = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw')
PROC_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed')
os.makedirs(PROC_PATH, exist_ok=True)


# ── Step 1: Load ─────────────────────────────────────────────────────────────
def load_tables(raw_path: str) -> dict:
    """Load all 9 Olist CSV files into a dictionary of DataFrames."""
    file_map = {
        'orders':      'olist_orders_dataset.csv',
        'order_items': 'olist_order_items_dataset.csv',
        'products':    'olist_products_dataset.csv',
        'customers':   'olist_customers_dataset.csv',
        'sellers':     'olist_sellers_dataset.csv',
        'reviews':     'olist_order_reviews_dataset.csv',
        'payments':    'olist_order_payments_dataset.csv',
        'geolocation': 'olist_geolocation_dataset.csv',
        'categories':  'product_category_name_translation.csv',
    }

    tables = {}
    for name, filename in file_map.items():
        path = os.path.join(raw_path, filename)
        tables[name] = pd.read_csv(path)
        print(f'  loaded {name:20s} ({tables[name].shape[0]:,} rows)')

    return tables


# ── Step 2: Clean ─────────────────────────────────────────────────────────────
def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """Parse dates, keep delivered orders only, drop nulls & duplicates."""
    date_cols = [
        'order_purchase_timestamp',
        'order_approved_at',
        'order_delivered_carrier_date',
        'order_delivered_customer_date',
        'order_estimated_delivery_date',
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col])

    df = df[df['order_status'] == 'delivered']
    df = df.dropna(subset=['order_delivered_customer_date'])
    df = df.drop_duplicates(subset='order_id')
    return df


def clean_items(df: pd.DataFrame) -> pd.DataFrame:
    """Remove zero-price rows and extreme price outliers (>99th pct)."""
    df = df[df['price'] > 0]
    p99 = df['price'].quantile(0.99)
    df = df[df['price'] <= p99]
    return df


# ── Step 3: Build master table ────────────────────────────────────────────────
def build_master(tables: dict) -> pd.DataFrame:
    """Join all tables and engineer key features."""
    orders = clean_orders(tables['orders'].copy())
    items  = clean_items(tables['order_items'].copy())

    master = (
        orders
        .merge(items,                                           on='order_id',              how='left')
        .merge(tables['customers'],                             on='customer_id',            how='left')
        .merge(tables['products'],                              on='product_id',             how='left')
        .merge(tables['reviews'][['order_id', 'review_score']], on='order_id',             how='left')
        .merge(tables['categories'],                            on='product_category_name', how='left')
    )

    # derived features
    master['total_value']     = master['price'] + master['freight_value']
    master['delivery_days']   = (master['order_delivered_customer_date']
                                 - master['order_purchase_timestamp']).dt.days
    master['delay_days']      = (master['order_delivered_customer_date']
                                 - master['order_estimated_delivery_date']).dt.days
    master['is_late']         = master['delay_days'] > 0
    master['order_month']     = master['order_purchase_timestamp'].dt.to_period('M')
    master['order_hour']      = master['order_purchase_timestamp'].dt.hour
    master['order_dayofweek'] = master['order_purchase_timestamp'].dt.day_name()
    master['order_year']      = master['order_purchase_timestamp'].dt.year

    return master


# ── Step 4: RFM Segmentation ──────────────────────────────────────────────────
def run_rfm(master: pd.DataFrame) -> pd.DataFrame:
    """Compute RFM scores and assign segment labels."""
    snapshot = datetime(2018, 10, 17)

    rfm = (
        master
        .groupby('customer_unique_id')
        .agg(
            Recency   = ('order_purchase_timestamp', lambda x: (snapshot - x.max()).days),
            Frequency = ('order_id',                 'nunique'),
            Monetary  = ('total_value',              'sum'),
        )
        .reset_index()
    )

    rfm['R'] = pd.qcut(rfm['Recency'],                           q=5, labels=[5,4,3,2,1])
    rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'),    q=5, labels=[1,2,3,4,5])
    rfm['M'] = pd.qcut(rfm['Monetary'],                          q=5, labels=[1,2,3,4,5])

    for col in ['R', 'F', 'M']:
        rfm[col] = rfm[col].astype(int)

    rfm['RFM_Score'] = rfm['R'] + rfm['F'] + rfm['M']

    def label(row):
        if row['RFM_Score'] >= 13:  return 'Champions'
        if row['RFM_Score'] >= 10:  return 'Loyal'
        if row['R'] >= 4:           return 'Recent'
        if row['RFM_Score'] >= 6:   return 'At Risk'
        return 'Lost'

    rfm['Segment'] = rfm.apply(label, axis=1)
    return rfm


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print('\n========= OLIST PIPELINE — dataamir =========\n')

    print('[1/4] Loading raw CSV files...')
    tables = load_tables(RAW_PATH)

    print('\n[2/4] Building master table...')
    master = build_master(tables)
    print(f'      Master table: {master.shape}')

    print('\n[3/4] Running RFM segmentation...')
    rfm = run_rfm(master)
    print(f'      RFM table: {rfm.shape}')
    print(rfm['Segment'].value_counts().to_string())

    print('\n[4/4] Saving outputs...')
    master.to_csv(os.path.join(PROC_PATH, 'master_table.csv'), index=False)
    rfm.to_csv(os.path.join(PROC_PATH, 'rfm_segments.csv'), index=False)
    print('      Saved master_table.csv and rfm_segments.csv')

    print('\n✓ Pipeline complete!\n')
    print(f'  Total orders     : {master["order_id"].nunique():,}')
    print(f'  Total revenue    : R$ {master["total_value"].sum():,.2f}')
    print(f'  Late deliveries  : {master["is_late"].sum():,} ({master["is_late"].mean()*100:.1f}%)')
    print(f'  Avg review score : {master["review_score"].mean():.2f}')


if __name__ == '__main__':
    main()
