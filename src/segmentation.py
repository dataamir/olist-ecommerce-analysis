"""
segmentation.py
---------------
RFM (Recency, Frequency, Monetary) customer segmentation.
Takes the master table and outputs a scored + labelled segment table.

Usage:
    from src.segmentation import build_rfm
    rfm = build_rfm(master)
"""

import pandas as pd
import numpy as np
from datetime import datetime


# ─────────────────────────────────────────
# RFM CALCULATION
# ─────────────────────────────────────────
def build_rfm(master: pd.DataFrame, snapshot_date: datetime = None) -> pd.DataFrame:
    """
    Compute RFM scores for each unique customer.

    Parameters
    ----------
    master : pd.DataFrame
        Master analytical table (output of pipeline.py)
    snapshot_date : datetime, optional
        Reference date for recency calculation.
        Defaults to 1 day after the last order in the dataset.

    Returns
    -------
    pd.DataFrame
        RFM table with Recency, Frequency, Monetary, scores, and segment label.
    """
    if snapshot_date is None:
        snapshot_date = master["order_purchase_timestamp"].max() + pd.Timedelta(days=1)

    rfm = (
        master.groupby("customer_unique_id")
        .agg(
            Recency  =("order_purchase_timestamp", lambda x: (snapshot_date - x.max()).days),
            Frequency=("order_id",                 "nunique"),
            Monetary =("total_value",              "sum"),
        )
        .reset_index()
    )

    # ── Quintile scoring (1 = worst, 5 = best) ───────
    rfm["R"] = pd.qcut(rfm["Recency"],   q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"),
                       q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm["M"] = pd.qcut(rfm["Monetary"],  q=5, labels=[1, 2, 3, 4, 5]).astype(int)

    rfm["RFM_Score"] = rfm["R"] + rfm["F"] + rfm["M"]

    # ── Segment labels ────────────────────────────────
    rfm["Segment"] = rfm.apply(_label_segment, axis=1)

    return rfm


def _label_segment(row) -> str:
    score, r, f = row["RFM_Score"], row["R"], row["F"]
    if score >= 13:              return "Champions"
    elif score >= 10:            return "Loyal"
    elif r >= 4:                 return "Recent"
    elif score >= 6:             return "At Risk"
    else:                        return "Lost"


# ─────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────
def segment_summary(rfm: pd.DataFrame) -> pd.DataFrame:
    """Print and return a summary table per segment."""
    summary = (
        rfm.groupby("Segment")
        .agg(
            Customers =("customer_unique_id", "count"),
            Avg_Recency  =("Recency",   "mean"),
            Avg_Frequency=("Frequency", "mean"),
            Avg_Monetary =("Monetary",  "mean"),
        )
        .round(1)
        .sort_values("Avg_Monetary", ascending=False)
    )
    print("\n── RFM Segment Summary ─────────────────────")
    print(summary.to_string())
    return summary


# ─────────────────────────────────────────
# OPTIONAL: K-MEANS CLUSTERING
# ─────────────────────────────────────────
def kmeans_segments(rfm: pd.DataFrame, n_clusters: int = 4) -> pd.DataFrame:
    """
    Alternative: use K-Means instead of quintile scoring.
    Adds a 'Cluster' column to the rfm DataFrame.
    """
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import KMeans

    features = rfm[["Recency", "Frequency", "Monetary"]].copy()
    scaler   = StandardScaler()
    scaled   = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm["Cluster"] = kmeans.fit_predict(scaled)
    return rfm
