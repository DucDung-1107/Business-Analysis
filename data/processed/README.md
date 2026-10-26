# Processed-data versions

Each direct child of this folder is one reproducible processed-data version. A version folder must contain its own `README.md` before it can be used by modelling or reporting code.

## Versioning policy

- Keep raw source files immutable in `data/raw/` and out of Git.
- Name a version folder for the source and preprocessing version, for example `kaggle_churn_v1`.
- Store content hashes, source type, schema/quality checks and generation assumptions in a JSON manifest.
- Keep customer-level CSVs out of Git. Commit only the version README and safe manifest files after review.
- Do not overwrite a version with different input data or assumptions. Create a new version folder and update its README/configuration instead.

## Current versions

| Folder | Purpose | Label policy | Status |
| --- | --- | --- | --- |
| `kaggle_churn_v1/` | Cleaned static Kaggle-base extract only | `churn` is kept only in `labels_clean.csv` | Static base; not temporally validated |
| `kaggle_churn_v2/` | Outcome-independent synthetic behaviour/RFM augmentation derived from v1 | `churn` is excluded from every v2 CSV | Illustrative derived version |

See the README inside the version folder for exact schema, transforms, limitations and commands.
