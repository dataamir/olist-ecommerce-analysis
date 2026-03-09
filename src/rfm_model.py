"""
rfm_model.py
------------
RFM (Recency, Frequency, Monetary) customer segmentation.

RFM is a simple but powerful way to group customers based on
their purchasing behavior. I learned about it in class and
wanted to apply it to real data.

- Recency:   How recently did they buy? (lower = better)
- Frequency: How many times did they buy?
- Monetary:  How much did they spend in total?
"""

import pandas as pd
import numpy as np
from datetime import datetime


def build_rfm(master_df, snapshot_date=None):
    """
    Build the RFM table from the master dataset.
    One row per unique customer.
    
    Parameters
    ----------
    master_df     : pd.DataFrame — master table with order data
    snapshot_date : datetime, optional
        The "today" date for recency calculation.
        Defaults to 1 day after the last order in the dataset.
    
    Returns
    -------
    pd.DataFrame with columns: customer_unique_id, Recency, Frequency, Monetary
    """
    # Use the day after the last order as our reference point
    if snapshot_date is None:
        last_order = master_df['order_purchase_timestamp'].max()
        snapshot_date = last_order + pd.Timedelta(days=1)
    
    print(f"  RFM snapshot date: {snapshot_date.date()}")
    
    rfm = master_df.groupby('customer_unique_id').agg(
        Recency   = ('order_purchase_timestamp', lambda x: (snapshot_date - x.max()).days),
        Frequency = ('order_id',                 'nunique'),
        Monetary  = ('total_value',              'sum')
    ).reset_index()
    
    rfm['Monetary'] = rfm['Monetary'].round(2)
    
    print(f"  Customers in RFM: {len(rfm):,}")
    print(f"  Avg Recency:   {rfm['Recency'].mean():.0f} days")
    print(f"  Avg Frequency: {rfm['Frequency'].mean():.2f} orders")
    print(f"  Avg Monetary:  R${rfm['Monetary'].mean():.2f}")
    
    return rfm


def score_rfm(rfm_df):
    """
    Add R, F, M scores from 1 to 5 using quintile buckets.
    
    For Recency: lower days = better = score 5
    For Frequency & Monetary: higher = better = score 5
    
    Parameters
    ----------
    rfm_df : pd.DataFrame — output of build_rfm()
    
    Returns
    -------
    pd.DataFrame with R, F, M, RFM_Score columns added
    """
    df = rfm_df.copy()
    
    # Recency: 1 = bought ages ago, 5 = bought very recently
    df['R'] = pd.qcut(df['Recency'], q=5, labels=[5, 4, 3, 2, 1])
    
    # Frequency: 1 = bought rarely, 5 = bought many times
    # duplicates='drop' handles cases where most customers have same frequency
    df['F'] = pd.qcut(df['Frequency'].rank(method='first'), q=5, labels=[1, 2, 3, 4, 5])
    
    # Monetary: 1 = low spend, 5 = high spend
    df['M'] = pd.qcut(df['Monetary'], q=5, labels=[1, 2, 3, 4, 5])
    
    # Total score out of 15
    df['R'] = df['R'].astype(int)
    df['F'] = df['F'].astype(int)
    df['M'] = df['M'].astype(int)
    df['RFM_Score'] = df['R'] + df['F'] + df['M']
    
    return df


def label_segments(rfm_scored_df):
    """
    Assign a human-readable segment label based on RFM scores.
    
    Segment rules (I tried to keep these simple but meaningful):
    - Champions  : RFM >= 13 — best customers, buy often, spend most
    - Loyal      : RFM 10-12 — solid repeat buyers
    - Recent     : R >= 4    — bought recently but not yet frequent
    - At Risk    : RFM 6-9   — used to buy but slowing down
    - Lost       : RFM < 6   — haven't bought in a long time, low value
    
    Parameters
    ----------
    rfm_scored_df : pd.DataFrame — output of score_rfm()
    
    Returns
    -------
    pd.DataFrame with 'Segment' column added
    """
    df = rfm_scored_df.copy()
    
    def get_segment(row):
        if row['RFM_Score'] >= 13:
            return 'Champions'
        elif row['RFM_Score'] >= 10:
            return 'Loyal'
        elif row['R'] >= 4:
            return 'Recent'
        elif row['RFM_Score'] >= 6:
            return 'At Risk'
        else:
            return 'Lost'
    
    df['Segment'] = df.apply(get_segment, axis=1)
    
    # Print a summary of the segments
    summary = df.groupby('Segment').agg(
        count       = ('Segment', 'count'),
        avg_recency = ('Recency', 'mean'),
        avg_freq    = ('Frequency', 'mean'),
        avg_spend   = ('Monetary', 'mean')
    ).round(1)
    
    print("\n  Segment Summary:")
    print(summary.to_string())
    
    return df


def run_full_rfm(master_df):
    """
    Convenience function — runs all 3 steps in one go.
    
    Returns
    -------
    pd.DataFrame — complete RFM table with scores and segment labels
    """
    print("Building RFM table...")
    rfm = build_rfm(master_df)
    
    print("\nScoring customers...")
    rfm = score_rfm(rfm)
    
    print("\nLabelling segments...")
    rfm = label_segments(rfm)
    
    return rfm
