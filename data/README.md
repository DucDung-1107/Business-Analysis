# Data provenance and handling

## v1 static base data

`data/raw/Bank Customer Churn Prediction.csv` is the supplied Kaggle-base extract for this project. It must remain immutable and is excluded from Git along with processed customer-level records. Its source-file name and SHA-256 hash are recorded in the reviewed preprocessing manifest; this lets the team verify they used the same input without committing the records.

Run the v1 pipeline from the repository root:

```bash
churn preprocess --config configs/preprocess_v1.json
```

The pipeline validates the source schema, duplicate customer key, missingness, categories and numerical bounds. It writes:

- `data/processed/kaggle_churn_v1/customers_clean.csv` — static candidate attributes plus `source_type=kaggle_base`.
- `data/processed/kaggle_churn_v1/labels_clean.csv` — the `churn` label keyed by `customer_id`, intentionally separate from attributes.
- `data/processed/kaggle_churn_v1/manifest.json` and `reports/data_quality/preprocess_v1_manifest.json` — identical provenance hashes and quality audit.

The reviewed manifest currently identifies data version `v1-90f6625c31bd-baeb8804`. Regenerate it whenever the source file or preprocessing configuration changes; review and commit the manifest with the code/configuration change.

## v2 derived behavioural augmentation

`data/processed/kaggle_churn_v2/` is a distinct derived version, never an edit to v1. It contains outcome-independent simulated behaviour, RFM features and an analyst-ready augmented table without `churn`. Recreate it with:

```bash
churn segment-v2 --config configs/segmentation_v2.json
```

Read `data/processed/kaggle_churn_v2/README.md` before use. Its outputs are illustrative, staff-only and not evidence of real customer behaviour. The final decision document is `docs/segmentation_v2_business_decision.md`.

## Important limitations

The available base extract is a static labelled table. It contains no observation timestamps, prediction point, label window, campaign treatment, CLV or retention cost. Therefore its label must be reported as a historical/static churn outcome, not a validated next-quarter target. No synthetic behavioural extension is created in v1.

Kaggle dataset licence/terms and the exact source URL have not yet been documented in this repository. That provenance item is **BLOCKED** pending the course-approved source record; do not claim licence review is complete.
