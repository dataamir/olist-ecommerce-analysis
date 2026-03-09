"""
cleaning.py
-----------
Data cleaning utilities for the Olist e-commerce dataset.
Each function is stateless and returns a cleaned copy of the input DataFrame.
"""

import pandas as pd
import numpy as np


# ── Datetime columns present in the orders table ──────────────────────────────
ORDER_DATE_COLS = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the orders table:
      - Parse all datetime columns
      - Drop cancelled orders
      - Drop rows missing actual delivery date
      - Remove duplicate order_ids
    """
    df = df.copy()

    # Parse dates
    for col in ORDER_DATE_COLS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    # Keep only delivered orders for analysis
    df = df[df["order_status"] == "delivered"]

    # Drop orders where we don't know when they arrived
    df = df.dropna(subset=["order_delivered_customer_date"])

    # Remove any duplicate order rows
    df = df.drop_duplicates(subset="order_id")

    print(f"[clean_orders] {len(df):,} delivered orders retained.")
    return df.reset_index(drop=True)


def clean_order_items(df: pd.DataFrame, price_quantile: float = 0.99) -> pd.DataFrame:
    """
    Clean the order_items table:
      - Remove extreme price outliers (above given quantile)
      - Fill missing freight_value with 0
      - Drop rows with null price
    """
    df = df.copy()

    df = df.dropna(subset=["price"])
    df["freight_value"] = df["freight_value"].fillna(0.0)

    upper_bound = df["price"].quantile(price_quantile)
    before = len(df)
    df = df[df["price"] <= upper_bound]
    removed = before - len(df)

    print(f"[clean_order_items] Removed {removed:,} price outliers (>{upper_bound:.2f} BRL). "
          f"{len(df):,} rows retained.")
    return df.reset_index(drop=True)


def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the products table:
      - Fill missing category names with 'unknown'
      - Fill missing numeric dimensions with median
    """
    df = df.copy()

    df["product_category_name"] = df["product_category_name"].fillna("unknown")

    numeric_cols = [
        "product_name_lenght", "product_description_lenght",
        "product_photos_qty", "product_weight_g",
        "product_length_cm", "product_height_cm", "product_width_cm",
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    print(f"[clean_products] {len(df):,} products cleaned.")
    return df.reset_index(drop=True)


def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the reviews table:
      - Keep one review per order (latest if duplicated)
      - Ensure review_score is 1–5 integer
    """
    df = df.copy()

    # Parse review creation date if present
    if "review_creation_date" in df.columns:
        df["review_creation_date"] = pd.to_datetime(df["review_creation_date"], errors="coerce")
        df = df.sort_values("review_creation_date", ascending=False)

    # One review per order
    df = df.drop_duplicates(subset="order_id", keep="first")

    # Clamp scores to valid range
    df["review_score"] = df["review_score"].clip(1, 5).astype(int)

    print(f"[clean_reviews] {len(df):,} reviews retained (one per order).")
    return df.reset_index(drop=True)


def null_report(df: pd.DataFrame, label: str = "") -> pd.DataFrame:
    """Print and return a summary of null values per column."""
    nulls = df.isnull().sum()
    pct   = (nulls / len(df) * 100).round(2)
    report = pd.DataFrame({"nulls": nulls, "pct": pct})
    report = report[report["nulls"] > 0].sort_values("pct", ascending=False)
    if label:
        print(f"\n── Null report: {label} ──")
    print(report.to_string() if not report.empty else "  No nulls found.")
    return report
