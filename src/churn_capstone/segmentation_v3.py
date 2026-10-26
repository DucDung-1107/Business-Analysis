"""V3 clustering diagnostics: multi-seed stability and segment distinctiveness."""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

from .synthetic_v3 import build_feature_snapshot, generate_bank_tables


FEATURES = ("transaction_count_6m", "transaction_amount_6m", "app_active_days_6m", "failed_payments_6m", "inflow_6m", "inflow_months", "cash_withdrawal_share", "inflow_trend_ratio", "unresolved_case_share")


def fit_behavior_segments(features: pd.DataFrame, *, seed: int) -> tuple[pd.DataFrame, dict[str, float]]:
    """Fit a two-segment, behavior-only K-Means baseline."""
    matrix = features.loc[:, FEATURES].astype(float).copy()
    for column in ("transaction_count_6m", "transaction_amount_6m", "app_active_days_6m", "failed_payments_6m", "inflow_6m"):
        matrix[column] = np.log1p(matrix[column])
    scaled = StandardScaler().fit_transform(matrix)
    labels = KMeans(n_clusters=2, n_init=30, random_state=seed).fit_predict(scaled)
    result = features.loc[:, ["customer_id", "app_active_days_6m"]].copy()
    result["raw_segment"] = labels
    high_raw = int(result.groupby("raw_segment").app_active_days_6m.mean().idxmax())
    result["segment_id"] = np.where(result.raw_segment.eq(high_raw), "segment_high_digital", "segment_lower_digital")
    result = result.loc[:, ["customer_id", "segment_id"]]
    metrics = {"silhouette": float(silhouette_score(scaled, labels, sample_size=min(1000, len(scaled)), random_state=seed)) if len(scaled) > 2 else float("nan")}
    return result, metrics


def multi_seed_diagnostics(customers: pd.DataFrame, seeds: tuple[int, ...] = (11, 23, 37, 53, 71)) -> pd.DataFrame:
    """Measure whether the full generator-plus-cluster pipeline is seed-sensitive."""
    reference: pd.DataFrame | None = None
    rows = []
    for seed in seeds:
        features = build_feature_snapshot(generate_bank_tables(customers, seed=seed))
        assignments, metrics = fit_behavior_segments(features, seed=seed)
        ari = 1.0 if reference is None else adjusted_rand_score(reference.segment_id, assignments.segment_id)
        rows.append({"seed": seed, "silhouette": metrics["silhouette"], "share_high_digital": float(assignments.segment_id.eq("segment_high_digital").mean()), "ari_vs_seed_11": float(ari)})
        if reference is None:
            reference = assignments
    return pd.DataFrame(rows)


def distinctiveness(features: pd.DataFrame, assignments: pd.DataFrame) -> pd.DataFrame:
    """Cohen's d for each feature, segment high-digital minus other segment."""
    joined = features.merge(assignments, on="customer_id", validate="one_to_one")
    high = joined.segment_id.eq("segment_high_digital")
    rows = []
    for feature in FEATURES:
        left, right = joined.loc[high, feature], joined.loc[~high, feature]
        pooled = np.sqrt(((left.var(ddof=1) + right.var(ddof=1)) / 2))
        rows.append({"feature": feature, "mean_high_digital": float(left.mean()), "mean_other": float(right.mean()), "cohens_d": float((left.mean() - right.mean()) / pooled) if pooled else 0.0})
    return pd.DataFrame(rows).sort_values("cohens_d", key=lambda values: values.abs(), ascending=False)
