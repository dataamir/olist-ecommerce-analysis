# 🛒 Brazilian E-Commerce — Business Insights & Executive Report

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.0-150458?logo=pandas&logoColor=white)
![Jupyter](https://img.shields.io/badge/Jupyter-Notebook-orange?logo=jupyter&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![Dataset](https://img.shields.io/badge/Dataset-Olist%20Kaggle-20BEFF?logo=kaggle&logoColor=white)

> **Course Project** | Data Analytics | Author: [@dataamir](https://github.com/dataamir)

---

## 📌 Project Overview

This is my end-to-end data analytics project using the **Brazilian E-Commerce Public Dataset by Olist** (available on Kaggle). The goal was to go through a full analytics cycle — from raw data to actual business recommendations — the kind of work a data analyst would do at a real company.

I worked through:
- Cleaning and joining 9 relational CSV tables
- Exploratory data analysis (EDA) to find patterns
- Customer segmentation using RFM scoring
- Building visualizations that tell a clear story
- Writing up business insights a decision-maker could act on

---

## 📁 Project Structure

```
olist-ecommerce-analysis/
│
├── notebooks/
│   ├── 01_data_loading_and_cleaning.ipynb
│   ├── 02_eda_and_visualizations.ipynb
│   ├── 03_customer_segmentation.ipynb
│   └── 04_business_insights.ipynb
│
├── src/
│   ├── load_data.py
│   ├── clean_data.py
│   ├── rfm_model.py
│   └── visualizations.py
│
├── data/
│   ├── raw/          ← CSVs from Kaggle (not in git)
│   └── processed/    ← cleaned outputs
│
├── reports/
│   └── executive_summary.md
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 📊 Dataset

**Source:** [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)

| File | Rows |
|------|------|
| olist_orders_dataset.csv | 99,441 |
| olist_order_items_dataset.csv | 112,650 |
| olist_customers_dataset.csv | 99,441 |
| olist_products_dataset.csv | 32,951 |
| olist_sellers_dataset.csv | 3,095 |
| olist_order_reviews_dataset.csv | 99,224 |
| olist_order_payments_dataset.csv | 103,886 |

**Download the data:**
```bash
pip install kaggle
kaggle datasets download -d olistbr/brazilian-ecommerce -p ./data/raw --unzip
```

---

## 🔧 How to Run

```bash
git clone https://github.com/dataamir/olist-ecommerce-analysis.git
cd olist-ecommerce-analysis
pip install -r requirements.txt
jupyter notebook
```
Run notebooks 01 → 04 in order.

---

## 📈 Key Findings

**1. Late deliveries destroy review scores** — Orders 5+ days late averaged 2.4★ vs 4.5★ for on-time. ~7.9% of orders were late, mostly in North/Northeast Brazil.

**2. Credit cards dominate (73.9%) but Boleto is still used by 19%** — both payment methods must stay supported.

**3. Peak purchase time is 2–4 PM and 9–11 PM on weekdays** — best window for promotions.

**4. High-value categories (Electronics, Furniture) have the worst ratings** — slow delivery for heavy items is the main complaint.

**5. 60%+ of customers never return** — RFM analysis reveals a serious retention gap.

---

## 🧠 Methodology

- **Cleaning:** datetime parsing, null handling, outlier capping at p99
- **Feature Engineering:** delivery_days, delay_days, is_late, order_hour, total_value
- **RFM Segmentation:** scored customers on Recency, Frequency, Monetary → labelled segments (Champions / Loyal / At Risk / Lost)

---

## 🛠️ Stack

Python · Pandas · NumPy · Matplotlib · Seaborn · Plotly · Scikit-learn · SQLAlchemy · Jupyter

---

*Made as part of a Data Analytics course project.*
