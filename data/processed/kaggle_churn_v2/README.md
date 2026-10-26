# `kaggle_churn_v2` — illustrative behavioural augmentation derived from v1

## Purpose and lineage

This is the **derived augmentation version**, created from the immutable base `../kaggle_churn_v1/`. It contains no new observed banking events. Its six-period behaviour, RFM, trend and service-friction variables are generated reproducibly for the segmentation demonstration because v1 has no transaction, login, complaint or channel data.

| Item | Value |
| --- | --- |
| Parent/base version | `kaggle_churn_v1`, `v1-90f6625c31bd-baeb8804` |
| Augmentation version | `synthetic-behavior-v2` |
| Seed | `20261026` |
| Simulated periods | 3 (`period_index`; not dates) |
| Behaviour provenance | `synthetic_behavior` |
| Target policy | `churn` is never read by the generator and is absent from all v2 CSVs |

## Files and grain

| File | Grain | Contents | Use |
| --- | --- | --- | --- |
| `synthetic_behavior_v2.csv` | customer × simulated period | transactions, spend, logins, complaints and channel allocation | audit of generated behaviour |
| `behavioral_rfm_features_v2.csv` | one row/customer | activity, recency, frequency, monetary and channel-share features | clustering input |
| `synthetic_persona_scenarios_v2.csv` | one row/customer | simulated pain signal, need-to-test and journey | A/B journey-design input; not a customer statement |
| `customers_augmented_behavioral_v2.csv` | one row/customer | v1 static profile attributes + v2 RFM features + provenance fields; **no `churn`** | staff-only analyst table |
| `augmentation_manifest_v2.json` | one JSON document | generation assumptions, source separation, output hashes | review/version control |

## How it is generated

Run from repository root:

```bash
churn segment-v2 --config configs/segmentation_v2.json
```

The generator uses only v1 profile fields (`active_member`, products, age, salary and credit score) and the configured seed. It generates correlated simulated activity and validates channel-count totals. The `churn` label is not an argument, is not joined during generation, and is excluded from the augmented customer table.

The V2 persona-scenario table is generated only from the synthetic RFM/complaint signals. Its `pain`, `need` and journey fields are scenario-design labels for A/B testing, not surveyed needs, observed complaint reasons or reasons for churn. Read `docs/data_dictionary_v2.md` before using it.

The segmenter transforms RFM features using predeclared `log1p` transformations where appropriate, 1st/99th-percentile clipping, and standardisation. Exact bounds and selected method are in `reports/segmentation/v2/segmentation_manifest.json`.

## Critical limitations

- Simulated periods are not a real timeline and cannot validate next-quarter churn.
- Synthetic behaviour does not evidence customer demand, operating behaviour or causal churn drivers.
- Any post-cluster static churn cross-tab is descriptive only, never a risk estimate or treatment-effect estimate.
- Customer-level CSVs are Git-ignored. Only this README and the reviewed manifest are version-controlled.

Create `kaggle_churn_v3` if real behavioural history, new augmentation assumptions, or a different parent data version is used. Never overwrite v2 with changed assumptions.
