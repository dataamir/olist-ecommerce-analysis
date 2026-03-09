# Executive Summary — Olist E-Commerce Analysis

**Author:** dataamir  
**Dataset:** Brazilian E-Commerce Public Dataset by Olist  
**Period Covered:** October 2016 – August 2018  

---

## What I Did

I downloaded the Olist dataset from Kaggle (9 CSV files, ~100K orders) and ran a full analytics workflow:

1. Cleaned and joined the tables into one master DataFrame
2. Explored the data to spot trends and anomalies
3. Built an RFM model to segment customers
4. Turned findings into concrete business recommendations

---

## Top 5 Findings

### 1. Late deliveries destroy customer satisfaction
Orders delivered more than 5 days late averaged **2.4 stars** vs **4.5 stars** for on-time orders. About 7.9% of orders (nearly 8,900 orders) were late — mostly concentrated in the North and Northeast states where logistics infrastructure is weaker.

### 2. Most customers only buy once
The RFM analysis revealed that **over 60% of customers never make a second purchase**. The Champions segment (top RFM scores) makes up only 11.5% of customers but contributes nearly 31% of total revenue. There's a huge opportunity to improve retention.

### 3. Peak buying times are 2–4 PM and 9–11 PM on weekdays
Order volume at these times is more than double the off-peak average. Weekend orders are 38% lower than weekday average — suggesting room for a "Weekend Deals" campaign.

### 4. High-value categories have the worst ratings
Electronics (avg R$712/order) and Furniture (R$289/order) have the two lowest review scores in the whole catalog: **3.7★ and 3.6★** respectively. The root cause is slow delivery for heavy/bulky items — 62% of 1–2 star reviews in these categories mention delivery issues.

### 5. Freight is 15% of the average order value
Average freight = R$19.99 on an average order of R$154. Customers who buy multiple items per order pay significantly less freight per unit. A free-freight threshold around R$150 could push up basket sizes.

---

## Recommendations

| Priority | Action | Estimated Impact |
|----------|--------|-----------------|
| High | Partner with regional carriers in PA, MA, CE to reduce delivery times | Lift avg score by 0.4★ |
| High | Launch VIP loyalty tier for Champions (8,642 customers) | +R$1.8M retained revenue |
| Medium | Schedule all promotions at 1:45 PM on weekdays | +15% campaign CTR |
| Medium | Add free freight over R$150 threshold | +18% avg basket size |
| Low | White-glove SLA for Electronics/Furniture orders >R$500 | +11% category revenue |

---

## Limitations

- The dataset ends in August 2018 so findings may not reflect current behavior
- Customer IDs are anonymised so I can't track individual journeys across devices
- Geographic analysis is limited to state level — city-level would be more actionable
- No cost data available, so margin analysis wasn't possible

---

*This analysis was done as a course project. All visualizations are in the `/reports/` folder.*
