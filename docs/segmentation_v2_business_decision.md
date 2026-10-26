# Segmentation v2 business decision brief

> **Illustrative / synthetic extension.** Clusters use outcome-independent simulated behavioural records because the supplied base data has no observed behaviour. Static `churn` is joined only after cluster assignment. This is not prospective churn prediction, causal evidence, or measured retention value.

## Executive decision

- **Decision now:** approve a measurement-design and data-collection phase, not live customer targeting or financial-return claims.
- **First pilot hypothesis:** `segment_02 — Low-activity customers` has the highest descriptive static-label rate among the illustrative groups. Test its segment-specific treatment only with consented, randomized treatment/control eligibility.
- **Coverage hypothesis:** `segment_02 — Low-activity customers` has the largest descriptive static-label exposure count. Use it for a separate, capacity-gated coverage experiment after the first pilot's safety and economics review.
- **Operating boundary:** CRM capacity, budget, value-per-retained-customer, treatment uplift and contact permissions are not in the source. The accountable owner must set those constraints before randomization; no segment should receive a blanket incentive.

## Method selection

- Data version: `v1-90f6625c31bd-baeb8804`.
- Selected method: `kmeans`, k=2; selection score=0.883, silhouette=0.191, stability ARI=0.979, Davies–Bouldin=1.920.
- Compared methods: K-Means, diagonal-covariance Gaussian Mixture and Ward hierarchical clustering, over the predeclared k range. Selection weighs separation (40%), subsample-label stability (30%), Davies–Bouldin (20%) and Calinski–Harabasz (10%), after rejecting undersized clusters. Rejected methods remain in the comparison table and figure.
- Cluster analysis is exploratory. Metrics assess geometric structure in simulated features; they do not validate commercial usefulness.

## Method comparison

| method | n_clusters | silhouette | stability_ari | davies_bouldin | calinski_harabasz | selection_score | method_status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| agglomerative_ward | 3 | 0.165 | 0.585 | 2.087 | 321.612 | 0.483 | eligible candidate |
| gaussian_mixture | 2 | 0.262 | 0.635 | 2.119 | 216.512 | 0.650 | eligible candidate |
| kmeans | 2 | 0.191 | 0.979 | 1.920 | 491.061 | 0.883 | eligible candidate |

## Segment decision register

Each finding below follows the project insight contract. Counts/rates describe the supplied static label cross-tab, while behaviour is synthetic.

### segment_02 — Low-activity customers

1. **Finding:** This segment contains 4,981 customers (49.8%) and has a historical/static churn-label rate of 26.6%.
2. **Evidence:** 1,324/4,981 labels are `churn=1`; 95% Wilson CI 25.4%–27.8%; overall source rate 20.4%.
3. **Confidence:** Counts are exact for this 10,000-row static extract; uncertainty intervals cover the label rate only. Behavioural inputs and personas are simulated, and no sampling frame or time horizon is available.
4. **Interpretation:** Observed in the synthetic behavioural extension: mean monthly transactions 2.8, mean monthly spend 81.5, mean logins 3.5, monthly inflow 3093.2, failed payments 0.06, and unresolved-case share 9.7%. This is a descriptive association, not evidence that behaviour causes churn.
5. **Business impact:** Pilot priority 1 uses the descriptive label rate; scale-exposure rank 1 reflects 1,324 historical labels. Neither is revenue, CLV, expected saves or ROI; those inputs are unavailable.
6. **Recommended action:** Test a low-cost reactivation journey focused on relevant digital-bank features, not blanket discounts.
7. **Execution:** Owner: CRM Lifecycle Team. Randomize eligible customers within segment to treatment/control; begin with a capacity-limited pilot and pre-register eligibility.
8. **Success measure:** Incremental 90-day active-month rate and retention versus randomized control. Guardrails: Opt-outs, contact frequency and complaint rate. Stop if guardrails worsen beyond a pre-specified tolerance; scale only if confidence intervals support positive incremental retention and unit economics pass break-even.

### segment_01 — High-engagement, higher-spend customers

1. **Finding:** This segment contains 5,019 customers (50.2%) and has a historical/static churn-label rate of 14.2%.
2. **Evidence:** 713/5,019 labels are `churn=1`; 95% Wilson CI 13.3%–15.2%; overall source rate 20.4%.
3. **Confidence:** Counts are exact for this 10,000-row static extract; uncertainty intervals cover the label rate only. Behavioural inputs and personas are simulated, and no sampling frame or time horizon is available.
4. **Interpretation:** Observed in the synthetic behavioural extension: mean monthly transactions 4.4, mean monthly spend 131.4, mean logins 5.8, monthly inflow 7430.8, failed payments 0.04, and unresolved-case share 6.7%. This is a descriptive association, not evidence that behaviour causes churn.
5. **Business impact:** Pilot priority 2 uses the descriptive label rate; scale-exposure rank 2 reflects 713 historical labels. Neither is revenue, CLV, expected saves or ROI; those inputs are unavailable.
6. **Recommended action:** Test proactive value review or product-fit support; reserve incentives for experimentally eligible customers.
7. **Execution:** Owner: Retention + Product. Randomize eligible customers within segment to treatment/control; begin with a capacity-limited pilot and pre-register eligibility.
8. **Success measure:** Incremental retention and product-fit completion versus randomized control. Guardrails: Incentive cost per retained customer and contact fatigue. Stop if guardrails worsen beyond a pre-specified tolerance; scale only if confidence intervals support positive incremental retention and unit economics pass break-even.

## Financial decision boundary

No CLV, margin, outreach cost, incentive cost, operating cost or treatment uplift is present. Therefore no expected business value is calculated. Before a pilot is funded, estimate `required_uplift = (outreach_cost + incentive_cost + operating_cost) / (eligible_customers × value_per_retained_customer)` separately for conservative, base and optimistic assumptions approved by Finance. Do not substitute model accuracy, segment churn rate or a churn score for treatment uplift.

## 30/60/90-day proposal

- **0–30 days:** validate source licence, obtain observed behavioural/event history, agree eligibility and cost/CLV definitions, and pre-register a retention experiment.
- **31–60 days:** run a capacity-limited randomized pilot within the two highest-priority segments; monitor opt-outs, complaints, costs and data-quality failures weekly.
- **61–90 days:** evaluate incremental retention with confidence intervals and unit economics; stop, iterate or scale according to the registered rule. Replace synthetic behaviours before any operational targeting.
