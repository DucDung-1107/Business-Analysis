# `kaggle_churn_v1` — cleaned static Kaggle base

## Purpose and scope

This is **version 1 of the base data only**. It contains the cleaned static Kaggle extract and its separate static churn label. It does not contain synthetic behaviour, RFM features, cluster assignments or any augmentation. Those derived outputs begin in `../kaggle_churn_v2/`.

## Lineage

| Item | Value |
| --- | --- |
| Data version | `v1-90f6625c31bd-baeb8804` |
| Preprocessor | `kaggle-static-preprocess-v1` |
| Source type | `kaggle_base` |
| Time status | static snapshot; no observation/prediction/label window |

Review `manifest.json` for source/config/output hashes and the cleaning audit. The raw input is immutable and not committed to Git.

## Files and grain

| File | Grain | Contents | Permitted use |
| --- | --- | --- | --- |
| `customers_clean.csv` | one row/customer | validated static profile attributes plus `source_type=kaggle_base` | base profile input; staff-only |
| `labels_clean.csv` | one row/customer | `customer_id`, static `churn` only | outcome evaluation after modelling/segmentation; never a feature |
| `manifest.json` | one JSON document | hashes, cleaning checks and source provenance | review/version control |

## Cleaning rules

Run `churn preprocess --config configs/preprocess_v1.json`. The pipeline preserves customer IDs as strings, standardises country/gender, parses numeric fields and fails on schema changes, missing values, duplicate IDs or out-of-range values. It performs neither imputation nor row deletion. The `churn` field is separated before any future augmentation.

## Limitations and handoff

The static label is not a next-quarter outcome: the source provides no timestamps, observation window or prospective label window. Kaggle URL/licence evidence remains BLOCKED. Create a new version directory rather than editing this version if the source or cleaning assumptions change.

`kaggle_churn_v2` is a derived, illustrative behavioural augmentation that references this immutable base version. It must not overwrite or be added to v1.
