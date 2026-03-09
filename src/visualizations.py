"""
visualizations.py
-----------------
Reusable chart functions for the Olist analysis.

I made these so I don't have to write the same matplotlib
boilerplate in every notebook. Each function takes a DataFrame
and returns a matplotlib figure.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns


# Consistent color palette across all charts
COLORS = {
    'primary':   '#2563a8',
    'danger':    '#c8401a',
    'success':   '#1a6b3c',
    'warning':   '#d4a017',
    'muted':     '#6b6860',
    'light':     '#f5f2eb',
}

# Apply a clean style globally
plt.rcParams.update({
    'font.family':       'DejaVu Sans',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'axes.grid':         True,
    'grid.alpha':        0.3,
    'grid.linestyle':    '--',
    'figure.facecolor':  'white',
    'axes.facecolor':    'white',
})


def plot_monthly_revenue(master_df, figsize=(12, 5)):
    """
    Line chart showing revenue trend over time.
    Highlights the November 2017 Black Friday spike.
    """
    monthly = (
        master_df.groupby('order_month')['total_value']
        .sum()
        .reset_index()
    )
    monthly['order_month_str'] = monthly['order_month'].astype(str)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    ax.plot(monthly['order_month_str'], monthly['total_value'] / 1000,
            color=COLORS['primary'], linewidth=2.5, marker='o', markersize=4)
    
    ax.fill_between(range(len(monthly)), monthly['total_value'] / 1000,
                    alpha=0.1, color=COLORS['primary'])
    
    # Label the Black Friday peak
    peak_idx = monthly['total_value'].idxmax()
    peak_val = monthly['total_value'].iloc[peak_idx] / 1000
    ax.annotate(
        f"Black Friday\nR${peak_val:.0f}K",
        xy=(peak_idx, peak_val),
        xytext=(peak_idx - 2, peak_val + 50),
        arrowprops=dict(arrowstyle='->', color=COLORS['danger']),
        color=COLORS['danger'],
        fontsize=9,
    )
    
    ax.set_title("Monthly Revenue (R$ thousands)", fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("")
    ax.set_ylabel("Revenue (R$ 000s)")
    ax.set_xticks(range(0, len(monthly), 2))
    ax.set_xticklabels(monthly['order_month_str'].iloc[::2], rotation=45, ha='right', fontsize=8)
    
    plt.tight_layout()
    return fig


def plot_review_vs_delay(master_df, figsize=(9, 5)):
    """
    Shows how review score drops as delivery gets later.
    This is one of the most interesting findings in the analysis.
    """
    # Bucket delivery delays into groups
    df = master_df.dropna(subset=['delay_days', 'review_score']).copy()
    
    bins   = [-999, -7, -3, 0, 3, 7, 14, 999]
    labels = ['7+ days early', '3-7 days early', 'On time ±3d',
              '1-3 days late', '4-7 days late', '8-14 days late', '14+ days late']
    
    df['delay_bucket'] = pd.cut(df['delay_days'], bins=bins, labels=labels)
    
    avg_score = df.groupby('delay_bucket', observed=True)['review_score'].mean()
    
    fig, ax = plt.subplots(figsize=figsize)
    
    bars = ax.bar(range(len(avg_score)), avg_score.values, color=[
        COLORS['success'] if v >= 4.0 else COLORS['warning'] if v >= 3.5 else COLORS['danger']
        for v in avg_score.values
    ], edgecolor='white', linewidth=0.5, width=0.6)
    
    # Add value labels on bars
    for bar, val in zip(bars, avg_score.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.03,
                f'{val:.2f}★', ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    ax.set_xticks(range(len(avg_score)))
    ax.set_xticklabels(avg_score.index, rotation=30, ha='right', fontsize=9)
    ax.set_ylim(2, 5.2)
    ax.set_ylabel("Average Review Score")
    ax.set_title("Review Score vs. Delivery Timeliness", fontsize=13, fontweight='bold', pad=15)
    ax.axhline(y=avg_score.values.mean(), linestyle='--', color=COLORS['muted'],
               alpha=0.6, label=f"Overall avg: {avg_score.values.mean():.2f}")
    ax.legend(fontsize=9)
    
    plt.tight_layout()
    return fig


def plot_rfm_segments(rfm_df, figsize=(10, 5)):
    """
    Side-by-side donut + bar chart showing RFM segment breakdown.
    """
    seg_counts = rfm_df['Segment'].value_counts()
    seg_value  = rfm_df.groupby('Segment')['Monetary'].mean().reindex(seg_counts.index)
    
    seg_colors = {
        'Champions': COLORS['danger'],
        'Loyal':     COLORS['primary'],
        'Recent':    COLORS['warning'],
        'At Risk':   COLORS['success'],
        'Lost':      COLORS['muted'],
    }
    colors = [seg_colors.get(s, '#aaa') for s in seg_counts.index]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # Donut chart — customer count
    wedges, texts, autotexts = ax1.pie(
        seg_counts.values, labels=seg_counts.index,
        autopct='%1.1f%%', colors=colors,
        startangle=90, pctdistance=0.78,
        wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2)
    )
    for t in autotexts:
        t.set_fontsize(8)
    ax1.set_title("Customer Count by Segment", fontsize=11, fontweight='bold')
    
    # Bar chart — avg spend per segment
    bars = ax2.bar(seg_value.index, seg_value.values,
                   color=[seg_colors.get(s, '#aaa') for s in seg_value.index],
                   edgecolor='white', linewidth=0.5)
    
    for bar, val in zip(bars, seg_value.values):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                 f'R${val:.0f}', ha='center', va='bottom', fontsize=9)
    
    ax2.set_ylabel("Avg Monetary Value (BRL)")
    ax2.set_title("Avg Spend by Segment", fontsize=11, fontweight='bold')
    ax2.tick_params(axis='x', rotation=20)
    
    plt.tight_layout()
    return fig


def plot_order_heatmap(master_df, figsize=(13, 4)):
    """
    Heatmap of order volume by day of week and hour of day.
    Good way to see when customers are most active.
    """
    df = master_df.dropna(subset=['order_purchase_timestamp']).copy()
    df['hour']    = df['order_purchase_timestamp'].dt.hour
    df['weekday'] = df['order_purchase_timestamp'].dt.day_name()
    
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    pivot = df.pivot_table(index='weekday', columns='hour',
                           values='order_id', aggfunc='count')
    pivot = pivot.reindex(day_order)
    
    fig, ax = plt.subplots(figsize=figsize)
    
    sns.heatmap(pivot, ax=ax, cmap='YlOrRd', linewidths=0.3,
                linecolor='white', cbar_kws={'label': 'Order Count'}, annot=False)
    
    ax.set_title("Order Volume Heatmap — Day × Hour", fontsize=13, fontweight='bold', pad=15)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("")
    ax.tick_params(axis='x', rotation=0, labelsize=8)
    
    plt.tight_layout()
    return fig


def plot_top_categories(master_df, top_n=10, figsize=(10, 6)):
    """
    Horizontal bar chart of top categories by revenue.
    """
    cat_col = 'product_category_name_english'
    if cat_col not in master_df.columns:
        cat_col = 'product_category_name'
    
    top_cats = (
        master_df.dropna(subset=[cat_col])
        .groupby(cat_col)['total_value']
        .sum()
        .nlargest(top_n)
        .sort_values()
    )
    
    fig, ax = plt.subplots(figsize=figsize)
    
    bars = ax.barh(top_cats.index, top_cats.values / 1000,
                   color=COLORS['primary'], edgecolor='white', linewidth=0.5)
    
    for bar, val in zip(bars, top_cats.values / 1000):
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                f'R${val:.0f}K', va='center', fontsize=8)
    
    ax.set_xlabel("Total Revenue (R$ thousands)")
    ax.set_title(f"Top {top_n} Categories by Revenue", fontsize=13, fontweight='bold', pad=15)
    
    plt.tight_layout()
    return fig
