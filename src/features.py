"""
features.py
-----------
Feature engineering for the Olist e-commerce master table.
All functions accept and return DataFrames — easy to chain.
"""

import pandas as pd
import numpy as np


def build_master_table(tables: dict) -> pd.DataFrame:
    """
    Join all Olist tables into a single analytical master DataFrame.

    Args:
        tables: dict returned by pipeline.load_all_csvs()

    Returns:
        master DataFrame with ~42 columns
    """
    orders      = tables["orders"]
    items       = tables["order_items"]
    customers   = tables["customers"]
    products    = tables["products"]
    reviews     = tables["reviews"][["order_id", "review_score"]]
    categories  = tables["categories"]

    master = (
        orders
        .merge(items,       on="order_id",                how="left")
        .merge(customers,   on="customer_id",             how="left")
        .merge(products,    on="product_id",              how="left")
        .merge(reviews,     on="order_id",                how="left")
        .merge(categories,  on="product_category_name",   how="left")
    )

    print(f"[build_master_table] Shape: {master.shape}")
    return master


def add_time_features(df: pd.DataFrame,
                      ts_col: str = "order_purchase_timestamp") -> pd.DataFrame:
    """Add calendar-based features from the purchase timestamp."""
    df = df.copy()
    ts = df[ts_col]

    df["order_year"]       = ts.dt.year
    df["order_month"]      = ts.dt.to_period("M")
    df["order_month_num"]  = ts.dt.month
    df["order_quarter"]    = ts.dt.quarter
    df["order_week"]       = ts.dt.isocalendar().week.astype(int)
    df["order_dayofweek"]  = ts.dt.day_name()
    df["order_hour"]       = ts.dt.hour
    df["is_weekend"]       = ts.dt.dayofweek >= 5

    return df


def add_delivery_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute delivery and delay metrics.
    Requires columns: order_purchase_timestamp,
                      order_delivered_customer_date,
                      order_estimated_delivery_date
    """
    df = df.copy()

    df["delivery_days"] = (
        df["order_delivered_customer_date"] - df["order_purchase_timestamp"]
    ).dt.days

    df["delay_days"] = (
        df["order_delivered_customer_date"] - df["order_estimated_delivery_date"]
    ).dt.days

    df["is_late"]       = df["delay_days"] > 0
    df["is_very_late"]  = df["delay_days"] > 5   # 5+ days late = likely to get bad review

    # Delivery speed buckets
    bins   = [0, 3, 7, 12, 18, 25, 35, np.inf]
    labels = ["1-3d", "4-7d", "8-12d", "13-18d", "19-25d", "26-35d", "36d+"]
    df["delivery_bucket"] = pd.cut(df["delivery_days"], bins=bins, labels=labels, right=True)

    return df


def add_value_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add revenue/value-related columns."""
    df = df.copy()
    df["total_value"]       = df["price"] + df["freight_value"]
    df["freight_ratio"]     = (df["freight_value"] / df["total_value"]).round(4)
    return df


def add_all_features(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience: apply all feature engineering in one call."""
    df = add_time_features(df)
    df = add_delivery_features(df)
    df = add_value_features(df)
    return df
