"""
rfm.py
------
RFM (Recency, Frequency, Monetary) segmentation module.
Accepts a master DataFrame and returns a scored + labelled RFM table.

Author: dataamir
"""

import pandas as pd
from datetime import datetime


SEGMENT_LABELS = {
    'Champions':  'High value, bought recently, buy often',
    'Loyal':      'Regular buyers with solid spend',
    'Recent':     'New or returned recently — not yet high spenders',
    'At Risk':    'Good history but have not bought recently',
    'Lost':       'Low recency, frequency, and spend — likely churned',
}


def compute_rfm(master: pd.DataFrame, snapshot_date=None) -> pd.DataFrame:
    """
    Compute RFM scores for each unique customer.

    Parameters
    ----------
    master : pd.DataFrame
        The joined master table from pipeline.py
    snapshot_date : datetime, optional
        Reference date for recency. Defaults to day after last order.

    Returns
    -------
    pd.DataFrame
        One row per customer_unique_id with R/F/M scores and segment label.
    """
    if snapshot_date is None:
        snapshot_date = master['order_purchase_timestamp'].max() + pd.Timedelta(days=1)

    rfm = master.groupby('customer_unique_id').agg(
        Recency   = ('order_purchase_timestamp', lambda x: (snapshot_date - x.max()).days),
        Frequency = ('order_id',                 'nunique'),
        Monetary  = ('total_item_value',          'sum')
    ).reset_index()

    # Score each dimension 1–5 using quintiles
    rfm['R_score'] = pd.qcut(rfm['Recency'], q=5, labels=[5,4,3,2,1])
    rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), q=5, labels=[1,2,3,4,5])
    rfm['M_score'] = pd.qcut(rfm['Monetary'], q=5, labels=[1,2,3,4,5])

    rfm['RFM_total'] = (
        rfm['R_score'].astype(int) +
        rfm['F_score'].astype(int) +
        rfm['M_score'].astype(int)
    )

    rfm['Segment'] = rfm.apply(_assign_segment, axis=1)
    return rfm


def _assign_segment(row) -> str:
    r     = int(row['R_score'])
    score = row['RFM_total']
    if score >= 13:   return 'Champions'
    elif score >= 10: return 'Loyal'
    elif r >= 4:      return 'Recent'
    elif score >= 6:  return 'At Risk'
    else:             return 'Lost'


def segment_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    """Print and return a summary table of each segment's key metrics."""
    summary = (
        rfm.groupby('Segment')
        .agg(
            customers     = ('customer_unique_id', 'count'),
            avg_recency   = ('Recency',   'mean'),
            avg_frequency = ('Frequency', 'mean'),
            avg_monetary  = ('Monetary',  'mean'),
        )
        .round(1)
        .reset_index()
    )
    summary['pct_customers'] = (summary['customers'] / summary['customers'].sum() * 100).round(1)
    return summary
