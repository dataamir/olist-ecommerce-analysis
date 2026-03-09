"""
clean_data.py
-------------
All the cleaning and preprocessing steps for the Olist dataset.

I kept running into the same issues in each notebook
(wrong types, missing values, etc.) so I moved the fixes here.
"""

import pandas as pd
import numpy as np


# Date columns that need to be parsed from strings
ORDER_DATE_COLS = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date',
]


def clean_orders(orders_df):
    """
    Clean the orders table:
    - Parse date strings into datetime objects
    - Remove cancelled orders (can't analyze incomplete purchases)
    - Remove rows where the delivery date is missing
    - Drop duplicate order IDs
    
    Parameters
    ----------
    orders_df : pd.DataFrame — raw orders table
    
    Returns
    -------
    pd.DataFrame — cleaned orders
    """
    df = orders_df.copy()
    
    # Fix date columns — they come in as strings
    for col in ORDER_DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    print(f"  Before cleaning: {len(df):,} orders")
    
    # Remove cancelled orders
    df = df[df['order_status'] != 'canceled']
    
    # Keep only delivered orders for delivery time analysis
    # (still keep 'shipped' for general order counts)
    delivered_mask = df['order_delivered_customer_date'].notna()
    df_delivered = df[delivered_mask].copy()
    
    # Drop duplicate order IDs just in case
    df = df.drop_duplicates(subset='order_id')
    df_delivered = df_delivered.drop_duplicates(subset='order_id')
    
    print(f"  After cleaning:  {len(df):,} orders ({len(df_delivered):,} delivered)")
    return df, df_delivered


def clean_order_items(items_df, price_cap_percentile=0.99):
    """
    Clean the order items table.
    - Remove rows with missing price
    - Cap extreme price outliers (probably data entry errors)
    
    Parameters
    ----------
    items_df             : pd.DataFrame
    price_cap_percentile : float — remove prices above this percentile
    
    Returns
    -------
    pd.DataFrame
    """
    df = items_df.copy()
    
    # Remove missing prices
    df = df.dropna(subset=['price'])
    
    # Cap outliers — anything above the 99th percentile is suspicious
    price_cap = df['price'].quantile(price_cap_percentile)
    outliers_removed = (df['price'] > price_cap).sum()
    df = df[df['price'] <= price_cap]
    
    print(f"  Items: removed {outliers_removed} price outliers (above R${price_cap:.2f})")
    return df


def add_features(master_df):
    """
    Add derived columns that I need for the analysis.
    
    Adds:
    - total_value       : price + freight
    - delivery_days     : how many days from purchase to delivery
    - delay_days        : how many days late vs the estimate (negative = early)
    - is_late           : True if delivered after estimated date
    - order_month       : year-month period
    - order_hour        : hour of day (0-23)
    - order_dayofweek   : name of day (Monday, Tuesday, etc.)
    - order_year        : year
    
    Parameters
    ----------
    master_df : pd.DataFrame — the joined master table
    
    Returns
    -------
    pd.DataFrame with new columns added
    """
    df = master_df.copy()
    
    # Revenue
    df['total_value'] = df['price'] + df['freight_value']
    
    # Delivery time calculations
    purchase = df['order_purchase_timestamp']
    delivered = df['order_delivered_customer_date']
    estimated = df['order_estimated_delivery_date']
    
    df['delivery_days'] = (delivered - purchase).dt.days
    df['delay_days']    = (delivered - estimated).dt.days
    df['is_late']       = df['delay_days'] > 0
    
    # Time features — useful for spotting trends
    df['order_month']     = df['order_purchase_timestamp'].dt.to_period('M')
    df['order_year']      = df['order_purchase_timestamp'].dt.year
    df['order_hour']      = df['order_purchase_timestamp'].dt.hour
    df['order_dayofweek'] = df['order_purchase_timestamp'].dt.day_name()
    
    print(f"  Added features: total_value, delivery_days, delay_days, is_late, time columns")
    print(f"  Late deliveries: {df['is_late'].sum():,} ({df['is_late'].mean()*100:.1f}% of orders)")
    
    return df


def get_null_report(df):
    """
    Quick summary of missing values in a DataFrame.
    Only shows columns that actually have nulls.
    """
    null_counts = df.isnull().sum()
    null_pct    = (df.isnull().mean() * 100).round(2)
    
    report = pd.DataFrame({
        'missing_count': null_counts,
        'missing_pct':   null_pct
    })
    
    report = report[report['missing_count'] > 0].sort_values('missing_pct', ascending=False)
    
    if len(report) == 0:
        print("  No missing values found!")
    else:
        print(f"  Found missing values in {len(report)} columns:")
        print(report.to_string())
    
    return report
