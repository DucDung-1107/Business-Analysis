# Segmentation v2 methodology and governance

## Purpose and disclosure

This is an exploratory customer-segmentation demonstration built from static base version `data/processed/kaggle_churn_v1/`, with the derived extension written to `data/processed/kaggle_churn_v2/`. The base extract has no observed transaction, login, complaint or channel history. `segment-v2` first generates a **seeded synthetic behavioural extension**, then clusters only its RFM/behavioural features.

The extension never receives or reads `churn`; cluster assignments are frozen before the separate static label table is joined. The resulting personas, churn cross-tabs and strategies must be labelled **Illustrative / synthetic extension**. They do not demonstrate actual digital-bank behaviour, next-quarter churn, causal drivers, treatment uplift, profitability or production suitability.

## Reproduction

```bash
churn preprocess --config configs/preprocess_v1.json
churn segment-v2 --config configs/segmentation_v2.json
```

The run uses an explicit seed, fixed feature list, documented transformations, and writes its selected candidate plus source hashes to `reports/segmentation/v2/segmentation_manifest.json`. The final decision brief is also written to `docs/segmentation_v2_business_decision.md`.

## Feature and leakage policy

The generator takes only cleaned profile attributes (`active_member`, products, age, salary and credit score) and a seed. It generates three simulated period-index records per customer, with correlated transactions, spend, logins, complaints and channel counts. The sequence is not a real time series.

The segmenter accepts only these derived behavioural/RFM variables:

| Feature | Meaning | Transformation |
| --- | --- | --- |
| avg_monthly_transactions | simulated monthly frequency | log1p, 1st/99th-percentile clipping, standardization |
| avg_monthly_spend | simulated monthly monetary activity; source currency unspecified | log1p, clipping, standardization |
| avg_monthly_logins | simulated monthly logins | log1p, clipping, standardization |
| complaints_per_month | simulated service-friction proxy | log1p, clipping, standardization |
| digital_transaction_share | simulated mobile share of transactions | clipping, standardization |
| active_month_ratio | share of simulated periods with activity | clipping, standardization |
| recency_periods | simulated periods since last activity | clipping, standardization |
| avg_transaction_value | simulated amount per transaction | log1p, clipping, standardization |

`customer_id`, demographic fields, `source_type`, and particularly `churn` are excluded. Winsorisation bounds and fitted scaler metadata are recorded in the manifest. This is appropriate for one exploratory cohort, not a live inference deployment artifact.

## Persona scenarios and multiple decision lenses

After synthetic RFM construction, V2 creates a separate `synthetic_persona_scenarios_v2.csv`. It maps simulated low activity, digital self-service and service-contact signals to testable journey scenarios. It never receives `churn`. The fields are not customer statements, pain points, preferences or causal churn reasons; they simply ensure that proposed A/B treatments are concrete and reproducible.

The final persona document also presents three observed-static overlays created before labels are joined: recorded active-member status, product count, and zero/positive-balance terciles. These are not learned clusters. They give the team relationship, product-depth and financial-context views for capacity planning and heterogeneous-treatment-effect analysis. Recorded country and gender appear only as aggregate descriptive/fairness fields and must not determine an offer or eligibility.

## Candidate comparison and selection

The pipeline evaluates all combinations of k=2–6 and the following predeclared algorithms on the same fixed-seed, label-free random evaluation sample (default 2,000 customers) of the transformed cohort:

1. K-Means (`n_init=20`, fixed seed)
2. Gaussian Mixture with diagonal covariance (`n_init=3`, fixed seed)
3. Ward agglomerative clustering

Candidates with a cluster below 5% of the evaluation sample are rejected. Eligible candidates receive a reproducible composite rank: silhouette 40%, subsample adjusted-Rand stability 30%, inverse Davies–Bouldin 20%, and Calinski–Harabasz 10%. Silhouette is calculated on the same fixed-seed 1,000-customer subsample for every candidate to prevent the metric itself exhausting memory. This is a design choice rather than an objective truth; the report retains all metrics and the best eligible candidate for each method. Stability repeatedly refits on a 75% subsample and compares memberships with the evaluation-sample solution using ARI. The winning K-Means/GMM is then refit on the full cohort. If Ward wins, full-cohort membership uses nearest sample-derived centroids; this approximation is documented in the manifest.

The selected method is chosen before joining labels. Segment IDs are canonicalised by descending engagement/spend rank, not by raw estimator label. Neutral persona names describe feature profiles and never imply a protected characteristic or a customer need.

## Decision use and safeguards

The output report contains one eight-field decision register entry per segment: finding, evidence, confidence, interpretation, business boundary, recommended action, execution and success rule. It shows two distinct descriptive views: **pilot priority** ranks static-label rate for a small, cautious test; **scale-exposure rank** ranks static label counts for a coverage view. Neither is predicted future churn, causal opportunity or financial exposure.

Each proposed intervention must be tested through an eligible-customer, within-segment randomized treatment/control pilot. Finance must supply value per retained customer, outreach/incentive/operating costs and approved conservative/base/optimistic uplift assumptions before any financial scenario is shown. The break-even formula is:

```text
required_uplift = (outreach_cost + incentive_cost + operating_cost)
                  / (eligible_customers × value_per_retained_customer)
```

Do not use a cluster churn rate, a classifier metric or a score as treatment uplift. Customer-level assignments must remain staff-only and access-controlled; public material should use aggregate profiles.

`segment_assignments.csv` is deliberately ignored by Git because it is a customer-level staff artifact. The manifest, aggregate method comparison, personas, cross-tab, strategy, report and figures are safe review artifacts; review and commit them together with the code/configuration change.

## Acceptance checks

- Exactly one assignment per source customer; labels are absent from clustering inputs.
- All three algorithms and every k candidate appear in `method_comparison.csv`.
- Each selected cluster meets the minimum-size rule.
- Each persona has count, share and behavioural profile; static-label rates have 95% Wilson intervals.
- Figures provide method comparison, profile heatmap and churn cross-tab with textual caveat in titles.
- Results retain the synthetic, static-label and no-financial-data limitations.

## Current blockers

- The original assignment PDF and Kaggle URL/licence are not in the workspace.
- No real behavioural history, CLV, cost, intervention or prospective label window is available.
- Therefore G3 prospective validity, G5 financial strategy validation, G7 deployment and G8 live monitoring remain out of scope/BLOCKED for this module.
