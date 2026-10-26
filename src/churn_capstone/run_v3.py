"""Run the full-cohort V3 segmentation diagnostics."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from matplotlib import pyplot as plt

from .segmentation_v3 import distinctiveness, fit_behavior_segments, multi_seed_diagnostics
from .synthetic_v3 import build_feature_snapshot, generate_bank_tables


def run(output_dir: Path, *, seed: int = 20261026) -> None:
    customers = pd.read_csv("data/processed/kaggle_churn_v1/customers_clean.csv", dtype={"customer_id": "string"})
    labels = pd.read_csv("data/processed/kaggle_churn_v1/labels_clean.csv", dtype={"customer_id": "string"})
    tables = generate_bank_tables(customers, seed=seed)
    features = build_feature_snapshot(tables)
    assignments, metrics = fit_behavior_segments(features, seed=seed)
    diagnostics = multi_seed_diagnostics(customers)
    effects = distinctiveness(features, assignments)
    churn = assignments.merge(labels, on="customer_id", validate="one_to_one").groupby("segment_id").churn.agg(["size", "sum", "mean"]).reset_index()
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in {**tables, "feature_snapshot": features, "assignments": assignments, "multi_seed_diagnostics": diagnostics, "distinctiveness": effects, "segment_churn": churn}.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)
    figure, axes = plt.subplots(1, 2, figsize=(12, 4.5), constrained_layout=True)
    axes[0].bar(diagnostics.seed.astype(str), diagnostics.ari_vs_seed_11, color="#286B52")
    axes[0].set_title("V3 multi-seed stability (ARI)"); axes[0].set_ylim(0, 1)
    top = effects.head(8).sort_values("cohens_d")
    axes[1].barh(top.feature, top.cohens_d, color="#55A67A")
    axes[1].set_title("Feature separation: Cohen's d")
    figure.savefig(output_dir / "v3_stability_and_distinctiveness.png", dpi=180)
    plt.close(figure)
    (output_dir / "manifest.json").write_text(json.dumps({"seed": seed, "customers": len(customers), "silhouette": metrics["silhouette"], "mode": "SYNTHETIC_BEHAVIOR"}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run(Path("reports/segmentation/v3"))
