"""Leakage-safe, reproducible customer segmentation for the static churn base.

The Kaggle base has no observed transaction history.  This module therefore
creates an explicitly synthetic, outcome-independent behaviour extension before
clustering.  It is suitable for an academic product demonstration only: no
persona, cluster-to-churn association, or proposed treatment is causal or a
prospective prediction.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import matplotlib

matplotlib.use("Agg")

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import adjusted_rand_score, calinski_harabasz_score, davies_bouldin_score, silhouette_score
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


SEGMENTATION_VERSION = "behavioral-segmentation-v2"
BEHAVIOR_VERSION = "synthetic-behavior-v2"
SOURCE_TYPE = "synthetic_behavior"
RFM_FEATURES = (
    "avg_monthly_transactions",
    "avg_monthly_spend",
    "avg_monthly_logins",
    "complaints_per_month",
    "digital_transaction_share",
    "active_month_ratio",
    "recency_periods",
    "avg_transaction_value",
    "transaction_trend_ratio",
    "login_trend_ratio",
    "complaints_per_100_interactions",
    "avg_monthly_inflow",
    "inflow_regularity",
    "cash_withdrawal_share",
    "failed_payments_per_month",
    "app_active_days_mean",
    "unresolved_case_share",
)
SYNTHETIC_SCENARIO_COLUMNS = (
    "customer_id",
    "simulated_pain_signal",
    "simulated_need_to_test",
    "simulated_primary_journey",
    "source_type",
)
LOG_FEATURES = {
    "avg_monthly_transactions",
    "avg_monthly_spend",
    "avg_monthly_logins",
    "complaints_per_month",
    "avg_transaction_value",
    "complaints_per_100_interactions",
    "avg_monthly_inflow",
    "failed_payments_per_month",
}
METHODS = ("kmeans", "gaussian_mixture", "agglomerative_ward")
COLORS = {"deep_green": "#173F35", "green": "#286B52", "light_green": "#55A67A", "pale_green": "#CDE8D7", "ink": "#23352D", "muted": "#61746A", "danger": "#B64E50"}


class SegmentationValidationError(ValueError):
    """Raised when a segmentation input violates a critical invariant."""


@dataclass(frozen=True)
class SegmentationResult:
    """Output locations and model-selection metadata for a segmentation run."""

    selected_method: str
    selected_clusters: int
    output_dir: Path
    report_path: Path


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, content: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(content, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")


def _validate_customers(customers: pd.DataFrame) -> None:
    required = {
        "customer_id", "credit_score", "country", "gender", "age", "tenure", "balance",
        "products_number", "credit_card", "active_member", "estimated_salary", "source_type",
    }
    if set(customers.columns) != required:
        raise SegmentationValidationError(f"Unexpected cleaned-customer schema: {sorted(customers.columns)}")
    if customers.customer_id.isna().any() or customers.customer_id.duplicated().any():
        raise SegmentationValidationError("customer_id must be non-null and unique")
    if not customers.source_type.eq("kaggle_base").all():
        raise SegmentationValidationError("Customers must be explicitly marked source_type=kaggle_base")


def generate_synthetic_behavior(
    customers: pd.DataFrame, *, seed: int, periods: int
) -> pd.DataFrame:
    """Generate correlated behavioural records without accessing the churn label.

    The structural assumptions are deliberately simple and auditable: digital
    activity is correlated with membership, product count, age and salary; a
    latent service-friction term drives complaints.  ``churn`` is not accepted
    as an input and cannot affect any generated value.
    """
    _validate_customers(customers)
    if periods < 2:
        raise ValueError("At least two simulated periods are required for recency and activity features")
    rng = np.random.default_rng(seed)
    frame = customers.reset_index(drop=True).copy()
    n_customers = len(frame)
    active = frame["active_member"].to_numpy(dtype=float)
    products = frame["products_number"].to_numpy(dtype=float)
    age = frame["age"].to_numpy(dtype=float)
    credit = frame["credit_score"].to_numpy(dtype=float)
    salary = frame["estimated_salary"].to_numpy(dtype=float)
    salary_scaled = (salary - salary.mean()) / max(float(salary.std()), 1.0)
    credit_scaled = (credit - credit.mean()) / max(float(credit.std()), 1.0)
    engagement = (
        0.95 * active + 0.22 * (products - 1) - 0.014 * (age - 45)
        + 0.10 * salary_scaled + 0.08 * credit_scaled
    )
    engagement += rng.normal(0, 0.55, n_customers)
    friction = 0.45 * (1 - active) + 0.20 * (products - 1) + 0.12 * np.maximum(age - 55, 0) / 10
    friction += rng.normal(0, 0.45, n_customers)
    monthly_frames: list[pd.DataFrame] = []
    for period_index in range(1, periods + 1):
        seasonal = rng.normal(0, 0.20, n_customers)
        transaction_rate = np.exp(1.00 + 0.34 * engagement + seasonal)
        transaction_count = rng.poisson(np.clip(transaction_rate, 0.05, 80)).astype(int)
        login_rate = np.exp(1.18 + 0.42 * engagement + rng.normal(0, 0.18, n_customers))
        login_count = rng.poisson(np.clip(login_rate, 0.05, 100)).astype(int)
        complaint_rate = np.exp(-3.15 + 0.68 * friction + rng.normal(0, 0.16, n_customers))
        complaint_count = rng.poisson(np.clip(complaint_rate, 0.001, 5)).astype(int)
        ticket_value = np.exp(3.25 + 0.15 * (products - 1) + 0.08 * salary_scaled + rng.normal(0, 0.28, n_customers))
        transaction_amount = np.round(transaction_count * ticket_value, 2)
        digital_probability = 1 / (1 + np.exp(-(-0.05 + 0.75 * active - 0.022 * (age - 45))))
        mobile_count = rng.binomial(transaction_count, np.clip(digital_probability, 0.05, 0.95))
        remaining = transaction_count - mobile_count
        atm_count = rng.binomial(remaining, 0.55)
        branch_count = remaining - atm_count
        inflow = np.where(rng.random(n_customers) < (0.35 + 0.55 * active), salary / 12 * (0.82 + 0.36 * rng.random(n_customers)), 0)
        monthly_frames.append(pd.DataFrame({
            "customer_id": frame["customer_id"].to_numpy(), "period_index": period_index,
            "transaction_count": transaction_count, "transaction_amount": transaction_amount,
            "login_count": login_count, "complaint_count": complaint_count, "mobile_count": mobile_count,
            "atm_count": atm_count, "branch_count": branch_count, "inbound_deposit_amount": np.round(inflow, 2),
            "card_spend_amount": np.round(transaction_amount * (0.45 + 0.45 * digital_probability), 2),
            "bill_payment_amount": np.round(transaction_amount * (0.10 + 0.18 * rng.random(n_customers)), 2),
            "cash_withdrawal_amount": np.round(transaction_amount * (0.08 + 0.22 * (1 - digital_probability)), 2),
            "loan_repayment_amount": np.round(np.where(products >= 3, np.maximum(0, (products - 1) * 18 + 0.03 * salary / 12 + rng.normal(0, 10, n_customers)), 0), 2),
            "failed_payment_count": rng.poisson(np.clip(np.exp(-3.2 + 0.55 * friction), 0.001, 3)),
            "app_active_days": np.minimum(31, np.maximum(0, np.round(login_count * (1.1 + 0.4 * rng.random(n_customers))))).astype(int),
            "salary_payment_day": np.where((active > 0) & (salary > 0), np.clip(np.round(25 + rng.normal(0, 2.5, n_customers)), 1, 28), 0).astype(int),
            "service_case_opened": complaint_count,
            "service_case_resolved": np.array([rng.binomial(int(value), 0.72) for value in complaint_count]),
            "source_type": SOURCE_TYPE,
        }))
    behavior = pd.concat(monthly_frames, ignore_index=True)
    channel_total = behavior[["mobile_count", "atm_count", "branch_count"]].sum(axis=1)
    if not channel_total.eq(behavior["transaction_count"]).all():
        raise RuntimeError("Synthetic channel allocation invariant failed")
    return behavior


def build_rfm_features(behavior: pd.DataFrame, *, periods: int) -> pd.DataFrame:
    """Build RFM/behaviour features only; labels and static demographics are excluded."""
    required = {
        "customer_id", "period_index", "transaction_count", "transaction_amount", "login_count",
        "complaint_count", "mobile_count", "atm_count", "branch_count", "inbound_deposit_amount",
        "card_spend_amount", "bill_payment_amount", "cash_withdrawal_amount", "loan_repayment_amount",
        "failed_payment_count", "app_active_days", "salary_payment_day", "service_case_opened",
        "service_case_resolved", "source_type",
    }
    if set(behavior.columns) != required or not behavior.source_type.eq(SOURCE_TYPE).all():
        raise SegmentationValidationError("Synthetic-behaviour schema or provenance is invalid")
    if behavior.duplicated(["customer_id", "period_index"]).any():
        raise SegmentationValidationError("Behaviour must have one row per customer and simulated period")
    if set(behavior.period_index.unique()) != set(range(1, periods + 1)):
        raise SegmentationValidationError("Every configured simulated period must be present")
    grouped = behavior.groupby("customer_id", sort=False)
    totals = grouped[["transaction_count", "transaction_amount", "login_count", "complaint_count", "mobile_count", "inbound_deposit_amount", "cash_withdrawal_amount", "failed_payment_count", "app_active_days", "service_case_opened", "service_case_resolved"]].sum()
    active_months = grouped["transaction_count"].apply(lambda values: int((values > 0).sum()))
    last_active = behavior.loc[behavior.transaction_count > 0].groupby("customer_id")["period_index"].max()
    output = pd.DataFrame(index=totals.index)
    output["avg_monthly_transactions"] = totals.transaction_count / periods
    output["avg_monthly_spend"] = totals.transaction_amount / periods
    output["avg_monthly_logins"] = totals.login_count / periods
    output["complaints_per_month"] = totals.complaint_count / periods
    output["digital_transaction_share"] = totals.mobile_count.div(totals.transaction_count.where(totals.transaction_count > 0, 1))
    output["active_month_ratio"] = active_months / periods
    output["recency_periods"] = periods - last_active.reindex(output.index).fillna(0)
    output["avg_transaction_value"] = totals.transaction_amount.div(totals.transaction_count.where(totals.transaction_count > 0, 1))
    split_month = max(1, periods // 2)
    early = behavior.loc[behavior.period_index.le(split_month)].groupby("customer_id")
    late = behavior.loc[behavior.period_index.gt(split_month)].groupby("customer_id")
    early_tx = early.transaction_count.mean().reindex(output.index).fillna(0.0)
    late_tx = late.transaction_count.mean().reindex(output.index).fillna(0.0)
    early_login = early.login_count.mean().reindex(output.index).fillna(0.0)
    late_login = late.login_count.mean().reindex(output.index).fillna(0.0)
    output["transaction_trend_ratio"] = late_tx.add(0.5).div(early_tx.add(0.5))
    output["login_trend_ratio"] = late_login.add(0.5).div(early_login.add(0.5))
    output["complaints_per_100_interactions"] = 100 * totals.complaint_count.div(
        (totals.transaction_count + totals.login_count).where((totals.transaction_count + totals.login_count) > 0, 1)
    )
    output["avg_monthly_inflow"] = totals.inbound_deposit_amount / periods
    output["inflow_regularity"] = grouped.inbound_deposit_amount.apply(lambda values: float((values > 0).mean()))
    output["cash_withdrawal_share"] = totals.cash_withdrawal_amount.div(totals.transaction_amount.where(totals.transaction_amount > 0, 1))
    output["failed_payments_per_month"] = totals.failed_payment_count / periods
    output["app_active_days_mean"] = totals.app_active_days / periods
    output["unresolved_case_share"] = (totals.service_case_opened - totals.service_case_resolved).clip(lower=0).div(totals.service_case_opened.where(totals.service_case_opened > 0, 1))
    output = output.reset_index()
    if output.isna().any().any() or not np.isfinite(output[list(RFM_FEATURES)].to_numpy(dtype=float)).all():
        raise SegmentationValidationError("RFM feature construction produced missing or non-finite values")
    return output


def generate_synthetic_persona_scenarios(customers: pd.DataFrame, rfm: pd.DataFrame) -> pd.DataFrame:
    """Generate an auditable, outcome-independent scenario for each customer.

    These fields are not a survey, a stated preference, or an observed churn
    reason.  They encode the testable business scenario implied by the
    *simulated* activity pattern, so the CRM team can run different journeys
    without inventing a causal claim.  ``churn`` is intentionally unavailable
    to this function.
    """
    _validate_customers(customers)
    if set(rfm.columns) != {"customer_id", *RFM_FEATURES} or rfm.customer_id.duplicated().any():
        raise SegmentationValidationError("RFM features must contain one row per customer and only declared fields")
    joined = customers.merge(rfm, on="customer_id", validate="one_to_one")
    transaction_low = joined.avg_monthly_transactions.quantile(0.25)
    login_low = joined.avg_monthly_logins.quantile(0.25)
    digital_high = joined.digital_transaction_share.quantile(0.75)
    scenario = pd.DataFrame({"customer_id": joined.customer_id})
    scenario["simulated_pain_signal"] = "No simulated friction signal"
    scenario["simulated_need_to_test"] = "Test value or product-fit review, if consented"
    scenario["simulated_primary_journey"] = "Value-review experiment"

    low_activity = joined.avg_monthly_transactions.le(transaction_low) & joined.avg_monthly_logins.le(login_low)
    digital_routine = joined.digital_transaction_share.ge(digital_high)
    service_friction = joined.complaints_per_month.gt(0)
    scenario.loc[low_activity, ["simulated_pain_signal", "simulated_need_to_test", "simulated_primary_journey"]] = [
        "Simulated low-activity signal",
        "Test whether feature discovery or a simpler return journey improves active use",
        "Reactivation experiment",
    ]
    scenario.loc[digital_routine & ~low_activity, ["simulated_pain_signal", "simulated_need_to_test", "simulated_primary_journey"]] = [
        "Simulated digital self-service signal",
        "Test contextual self-service education rather than a blanket incentive",
        "Digital self-service experiment",
    ]
    scenario.loc[service_friction, ["simulated_pain_signal", "simulated_need_to_test", "simulated_primary_journey"]] = [
        "Simulated service-contact signal",
        "Test issue resolution before any retention incentive",
        "Service-recovery experiment",
    ]
    scenario["source_type"] = "synthetic_persona_scenario"
    if tuple(scenario.columns) != SYNTHETIC_SCENARIO_COLUMNS or scenario.isna().any().any():
        raise SegmentationValidationError("Synthetic persona scenario invariant failed")
    return scenario


def profile_synthetic_persona_scenarios(assignments: pd.DataFrame, scenarios: pd.DataFrame) -> pd.DataFrame:
    """Summarise simulated scenario mix within each label-free cluster."""
    if set(assignments.columns) != {"customer_id", "segment_id"} or assignments.customer_id.duplicated().any():
        raise SegmentationValidationError("Assignments must contain one row per customer")
    if tuple(scenarios.columns) != SYNTHETIC_SCENARIO_COLUMNS or scenarios.customer_id.duplicated().any():
        raise SegmentationValidationError("Synthetic persona scenarios have an unexpected schema")
    joined = assignments.merge(scenarios, on="customer_id", validate="one_to_one")
    counts = joined.groupby(["segment_id", "simulated_pain_signal", "simulated_need_to_test", "simulated_primary_journey"], sort=True).size().reset_index(name="customer_count")
    totals = counts.groupby("segment_id").customer_count.transform("sum")
    counts["segment_share"] = counts.customer_count / totals
    counts["interpretation"] = (
        "Synthetic scenario mix derived from simulated behaviour; it is a journey-design input, not an observed reason, need or preference."
    )
    return counts.sort_values(["segment_id", "customer_count"], ascending=[True, False]).reset_index(drop=True)


def build_augmented_customer_table(customers: pd.DataFrame, rfm: pd.DataFrame) -> pd.DataFrame:
    """Join static base attributes to synthetic RFM features without adding the label."""
    _validate_customers(customers)
    if set(rfm.columns) != {"customer_id", *RFM_FEATURES} or rfm.customer_id.duplicated().any():
        raise SegmentationValidationError("RFM features must contain one unique customer_id and the declared feature set")
    augmented = customers.merge(rfm, on="customer_id", validate="one_to_one")
    if len(augmented) != len(customers) or "churn" in augmented.columns:
        raise SegmentationValidationError("Augmented table must cover every customer and exclude the churn label")
    augmented["behavior_source_type"] = SOURCE_TYPE
    return augmented


def prepare_clustering_matrix(rfm: pd.DataFrame) -> tuple[np.ndarray, dict[str, Any]]:
    """Apply predeclared log, winsorisation and standardisation for clustering."""
    if set(rfm.columns) != {"customer_id", *RFM_FEATURES}:
        raise SegmentationValidationError("RFM table has unexpected fields; labels must never enter clustering")
    transformed = rfm.loc[:, RFM_FEATURES].astype(float).copy()
    for feature in LOG_FEATURES:
        transformed[feature] = np.log1p(transformed[feature])
    lower = transformed.quantile(0.01)
    upper = transformed.quantile(0.99)
    clipped = transformed.clip(lower=lower, upper=upper, axis="columns")
    matrix = StandardScaler().fit_transform(clipped)
    metadata = {
        "feature_columns": list(RFM_FEATURES),
        "log1p_features": sorted(LOG_FEATURES),
        "winsorisation_quantiles": [0.01, 0.99],
        "clip_lower": {key: float(value) for key, value in lower.items()},
        "clip_upper": {key: float(value) for key, value in upper.items()},
        "scaling": "StandardScaler fit on the segmentation discovery cohort; not an inference artifact.",
    }
    return matrix, metadata


def _fit_labels(method: str, matrix: np.ndarray, clusters: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    if method == "kmeans":
        estimator = KMeans(n_clusters=clusters, n_init=20, random_state=seed)
        labels = estimator.fit_predict(matrix)
        return labels, estimator.cluster_centers_
    if method == "gaussian_mixture":
        estimator = GaussianMixture(n_components=clusters, covariance_type="diag", n_init=3, random_state=seed)
        labels = estimator.fit_predict(matrix)
        centers = np.vstack([matrix[labels == index].mean(axis=0) for index in range(clusters)])
        return labels, centers
    if method == "agglomerative_ward":
        labels = AgglomerativeClustering(n_clusters=clusters, linkage="ward").fit_predict(matrix)
        centers = np.vstack([matrix[labels == index].mean(axis=0) for index in range(clusters)])
        return labels, centers
    raise ValueError(f"Unsupported clustering method: {method}")


def _stability_score(method: str, matrix: np.ndarray, clusters: int, labels: np.ndarray, seed: int, repeats: int) -> float:
    rng = np.random.default_rng(seed)
    subset_size = max(clusters * 10, int(len(matrix) * 0.75))
    scores: list[float] = []
    for repeat in range(repeats):
        indices = rng.choice(len(matrix), size=subset_size, replace=False)
        bootstrap_labels, _ = _fit_labels(method, matrix[indices], clusters, seed + repeat + 1)
        scores.append(float(adjusted_rand_score(labels[indices], bootstrap_labels)))
    return float(np.mean(scores))


def compare_clustering_methods(
    matrix: np.ndarray,
    *,
    methods: Iterable[str],
    candidate_clusters: Iterable[int],
    seed: int,
    stability_repeats: int,
    min_cluster_share: float,
) -> tuple[pd.DataFrame, dict[str, tuple[np.ndarray, np.ndarray]]]:
    """Evaluate predeclared methods and cluster counts on the same feature matrix."""
    rows: list[dict[str, Any]] = []
    fitted: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for method_position, method in enumerate(methods):
        for clusters in candidate_clusters:
            labels, centers = _fit_labels(method, matrix, clusters, seed + method_position * 100 + clusters)
            counts = np.bincount(labels, minlength=clusters)
            minimum_share = float(counts.min() / len(labels))
            identifier = f"{method}_k{clusters}"
            fitted[identifier] = (labels, centers)
            rows.append({
                "candidate_id": identifier,
                "method": method,
                "n_clusters": clusters,
                "silhouette": float(silhouette_score(
                    matrix, labels, sample_size=min(1000, len(matrix)), random_state=seed
                )),
                "davies_bouldin": float(davies_bouldin_score(matrix, labels)),
                "calinski_harabasz": float(calinski_harabasz_score(matrix, labels)),
                "stability_ari": _stability_score(
                    method, matrix, clusters, labels, seed + method_position * 1000 + clusters, stability_repeats
                ),
                "minimum_cluster_share": minimum_share,
                "eligible": bool(minimum_share >= min_cluster_share),
            })
    comparison = pd.DataFrame(rows)
    eligible = comparison["eligible"]
    comparison["selection_score"] = np.nan
    if not eligible.any():
        raise SegmentationValidationError("No clustering candidate met the minimum cluster-size rule")
    scoring = comparison.loc[eligible].copy()
    scoring["selection_score"] = (
        0.40 * scoring["silhouette"].rank(pct=True)
        + 0.30 * scoring["stability_ari"].rank(pct=True)
        + 0.20 * scoring["davies_bouldin"].rank(ascending=False, pct=True)
        + 0.10 * scoring["calinski_harabasz"].rank(pct=True)
    )
    comparison.loc[scoring.index, "selection_score"] = scoring["selection_score"]
    return comparison.sort_values(["method", "n_clusters"]).reset_index(drop=True), fitted


def _select_champion(comparison: pd.DataFrame) -> pd.Series:
    eligible = comparison.loc[comparison.eligible].copy()
    method_best = eligible.sort_values("selection_score", ascending=False).groupby("method", as_index=False).first()
    return method_best.sort_values(["selection_score", "silhouette"], ascending=False).iloc[0]


def _canonical_segments(labels: np.ndarray, rfm: pd.DataFrame) -> tuple[np.ndarray, dict[int, str]]:
    profile = rfm.assign(_raw_label=labels).groupby("_raw_label")[list(RFM_FEATURES)].mean()
    ranking = profile[["avg_monthly_transactions", "avg_monthly_logins", "avg_monthly_spend"]].rank(pct=True).mean(axis=1)
    ordered = ranking.sort_values(ascending=False).index.tolist()
    mapping = {old: f"segment_{position:02d}" for position, old in enumerate(ordered, start=1)}
    return np.array([mapping[label] for label in labels]), mapping


def _nearest_centroid_labels(matrix: np.ndarray, centroids: np.ndarray) -> np.ndarray:
    """Assign full-cohort rows to sample-derived hierarchical centroids."""
    squared_distance = ((matrix[:, None, :] - centroids[None, :, :]) ** 2).sum(axis=2)
    return squared_distance.argmin(axis=1)


def _persona_name(profile: pd.Series, reference: pd.DataFrame) -> str:
    transaction_median = reference.avg_monthly_transactions.median()
    login_median = reference.avg_monthly_logins.median()
    spend_median = reference.avg_monthly_spend.median()
    complaint_upper = max(float(reference.complaints_per_month.quantile(0.90)), 0.20)
    digital_median = reference.digital_transaction_share.median()
    if profile.complaints_per_month >= complaint_upper:
        return "Service-friction contacts"
    if profile.avg_monthly_transactions >= transaction_median and profile.avg_monthly_logins >= login_median:
        if profile.avg_monthly_spend >= spend_median:
            return "High-engagement, higher-spend customers"
        return "High-engagement routine customers"
    if profile.digital_transaction_share >= digital_median and profile.avg_monthly_transactions >= transaction_median:
        return "Digital routine customers"
    if profile.avg_monthly_transactions < transaction_median and profile.avg_monthly_logins < login_median:
        return "Low-activity customers"
    return "Moderate-activity customers"


def profile_segments(assignments: pd.DataFrame, rfm: pd.DataFrame) -> pd.DataFrame:
    merged = assignments.merge(rfm, on="customer_id", validate="one_to_one")
    profile = merged.groupby("segment_id", sort=True)[list(RFM_FEATURES)].agg(["mean", "median"])
    profile.columns = [f"{feature}_{statistic}" for feature, statistic in profile.columns]
    profile = profile.reset_index()
    counts = merged.segment_id.value_counts().rename_axis("segment_id").reset_index(name="customer_count")
    profile = profile.merge(counts, on="segment_id", validate="one_to_one")
    profile["customer_share"] = profile.customer_count / profile.customer_count.sum()
    persona_names: list[str] = []
    descriptions: list[str] = []
    used_names: dict[str, int] = {}
    for _, row in profile.iterrows():
        base = _persona_name(row.rename({f"{name}_mean": name for name in RFM_FEATURES}), rfm)
        used_names[base] = used_names.get(base, 0) + 1
        name = base if used_names[base] == 1 else f"{base} ({used_names[base]})"
        persona_names.append(name)
        descriptions.append(
            f"Observed in the synthetic behavioural extension: mean monthly transactions "
            f"{row.avg_monthly_transactions_mean:.1f}, mean monthly spend {row.avg_monthly_spend_mean:.1f}, "
            f"mean logins {row.avg_monthly_logins_mean:.1f}, monthly inflow {row.avg_monthly_inflow_mean:.1f}, "
            f"failed payments {row.failed_payments_per_month_mean:.2f}, and unresolved-case share "
            f"{row.unresolved_case_share_mean:.1%}."
        )
    profile.insert(1, "persona_name", persona_names)
    profile.insert(2, "persona_description", descriptions)
    return profile.sort_values("segment_id").reset_index(drop=True)


def _wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return float("nan"), float("nan")
    proportion = successes / total
    denominator = 1 + z**2 / total
    centre = (proportion + z**2 / (2 * total)) / denominator
    margin = z * np.sqrt(proportion * (1 - proportion) / total + z**2 / (4 * total**2)) / denominator
    return float(centre - margin), float(centre + margin)


def churn_cross_tab(assignments: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    if set(labels.columns) != {"customer_id", "churn"} or labels.customer_id.duplicated().any():
        raise SegmentationValidationError("Labels must be a unique customer_id/churn table")
    joined = assignments.merge(labels, on="customer_id", validate="one_to_one")
    if len(joined) != len(assignments):
        raise SegmentationValidationError("Every segmentation assignment needs one label for post-hoc evaluation")
    summary = joined.groupby("segment_id", sort=True).agg(
        customer_count=("churn", "size"), historical_churn_count=("churn", "sum"), historical_churn_rate=("churn", "mean")
    ).reset_index()
    intervals = [_wilson_interval(int(row.historical_churn_count), int(row.customer_count)) for row in summary.itertuples()]
    summary[["churn_rate_ci95_low", "churn_rate_ci95_high"]] = pd.DataFrame(intervals, index=summary.index)
    overall_rate = float(joined.churn.mean())
    summary["overall_historical_churn_rate"] = overall_rate
    summary["rate_difference_vs_overall"] = summary.historical_churn_rate - overall_rate
    summary["historical_churn_exposure"] = summary.historical_churn_count
    summary["interpretation"] = "Descriptive static-label cross-tab only; it is not a prospective risk score or causal treatment opportunity."
    return summary


def build_static_persona_profile(assignments: pd.DataFrame, customers: pd.DataFrame) -> pd.DataFrame:
    """Describe each segment with *observed static* source fields.

    This is a descriptive profile, not an eligibility or targeting rule.  The
    source field ``country`` denotes the recorded country category, not a
    customer's hometown, nationality, or ethnicity.  ``estimated_salary`` is
    in an unspecified source currency and is not verified income.
    """
    _validate_customers(customers)
    if set(assignments.columns) != {"customer_id", "segment_id"} or assignments.customer_id.duplicated().any():
        raise SegmentationValidationError("Assignments must contain one unique customer_id and segment_id")
    joined = assignments.merge(customers, on="customer_id", validate="one_to_one")
    if len(joined) != len(customers):
        raise SegmentationValidationError("Static persona profile must cover every source customer")
    profile = joined.groupby("segment_id", sort=True).agg(
        customer_count=("customer_id", "size"),
        mean_age_years=("age", "mean"),
        median_age_years=("age", "median"),
        median_estimated_salary_source_currency=("estimated_salary", "median"),
        median_balance_source_currency=("balance", "median"),
        mean_products=("products_number", "mean"),
        active_member_share=("active_member", "mean"),
    ).reset_index()
    country_shares = pd.crosstab(joined.segment_id, joined.country, normalize="index")
    gender_shares = pd.crosstab(joined.segment_id, joined.gender, normalize="index")
    for country in ("France", "Germany", "Spain"):
        profile[f"country_{country.lower()}_share"] = profile.segment_id.map(country_shares.get(country, pd.Series(0.0, index=country_shares.index))).fillna(0.0)
    for gender in ("Female", "Male"):
        profile[f"gender_{gender.lower()}_share"] = profile.segment_id.map(gender_shares.get(gender, pd.Series(0.0, index=gender_shares.index))).fillna(0.0)
    profile["profile_scope"] = (
        "Observed static Kaggle fields only. Country and gender are descriptive/fairness fields, "
        "not intervention-targeting inputs."
    )
    return profile.sort_values("segment_id").reset_index(drop=True)


def build_static_lenses(customers: pd.DataFrame) -> pd.DataFrame:
    """Create auditable non-cluster overlays from observed static attributes.

    Lenses add decision context; they are deliberately not presented as learned
    behavioural clusters and are constructed before the churn label is joined.
    """
    _validate_customers(customers)
    output = customers.loc[:, ["customer_id", "active_member", "products_number", "balance"]].copy()
    output["relationship_lens"] = np.where(
        output.active_member.eq(1), "Recorded active member", "Recorded not-active member"
    )
    output["product_lens"] = output.products_number.map({
        1: "1 product", 2: "2 products", 3: "3 products", 4: "4 products",
    })
    output["balance_lens"] = "Zero recorded balance"
    positive = output.balance.gt(0)
    if positive.any():
        ranks = output.loc[positive, "balance"].rank(method="first")
        output.loc[positive, "balance_lens"] = pd.qcut(
            ranks, q=3, labels=["Positive balance: lower third", "Positive balance: middle third", "Positive balance: upper third"]
        ).astype("string")
    return output.loc[:, ["customer_id", "relationship_lens", "product_lens", "balance_lens"]]


def summarise_static_lenses(lenses: pd.DataFrame, labels: pd.DataFrame) -> pd.DataFrame:
    """Cross-tab predeclared static lenses with the static churn label post hoc."""
    if set(labels.columns) != {"customer_id", "churn"} or labels.customer_id.duplicated().any():
        raise SegmentationValidationError("Labels must be a unique customer_id/churn table")
    expected = {"customer_id", "relationship_lens", "product_lens", "balance_lens"}
    if set(lenses.columns) != expected or lenses.customer_id.duplicated().any():
        raise SegmentationValidationError("Static lenses have an unexpected schema")
    joined = lenses.merge(labels, on="customer_id", validate="one_to_one")
    rows: list[dict[str, Any]] = []
    overall_rate = float(joined.churn.mean())
    for lens in ("relationship_lens", "product_lens", "balance_lens"):
        for group, frame in joined.groupby(lens, sort=True):
            count = len(frame)
            churn_count = int(frame.churn.sum())
            lower, upper = _wilson_interval(churn_count, count)
            rows.append({
                "lens": lens,
                "group": group,
                "customer_count": count,
                "customer_share": count / len(joined),
                "historical_churn_count": churn_count,
                "historical_churn_rate": churn_count / count,
                "churn_rate_ci95_low": lower,
                "churn_rate_ci95_high": upper,
                "overall_historical_churn_rate": overall_rate,
                "interpretation": "Descriptive static-label cross-tab only; it is not a causal churn reason or future-risk estimate.",
            })
    return pd.DataFrame(rows).sort_values(["lens", "historical_churn_rate"], ascending=[True, False]).reset_index(drop=True)


def build_retention_strategy(profiles: pd.DataFrame, churn_summary: pd.DataFrame) -> pd.DataFrame:
    """Create experiment-ready proposals, not claims of realised uplift or ROI."""
    merged = profiles.merge(churn_summary, on=["segment_id", "customer_count"], validate="one_to_one")
    merged["priority_rank"] = merged.historical_churn_rate.rank(method="dense", ascending=False).astype(int)
    merged["scale_exposure_rank"] = merged.historical_churn_exposure.rank(method="dense", ascending=False).astype(int)
    rows: list[dict[str, Any]] = []
    for row in merged.sort_values("priority_rank").itertuples():
        persona = row.persona_name.casefold()
        if "service-friction" in persona:
            action = "Offer an opt-in service-recovery check and resolve a stated issue before any incentive."
            channel = "Secure in-app message with optional human-support callback"
            owner = "Customer Care + CRM"
            primary_kpi = "Issue-resolution rate; incremental 90-day retention versus randomized control"
            guardrail = "Complaint recurrence, opt-out rate, service workload and incentive cost"
        elif "low-activity" in persona:
            action = "Test a low-cost reactivation journey focused on relevant digital-bank features, not blanket discounts."
            channel = "Consent-aware in-app/email journey"
            owner = "CRM Lifecycle Team"
            primary_kpi = "Incremental 90-day active-month rate and retention versus randomized control"
            guardrail = "Opt-outs, contact frequency and complaint rate"
        elif "high-engagement" in persona:
            action = "Test proactive value review or product-fit support; reserve incentives for experimentally eligible customers."
            channel = "In-app prompt or relationship-manager outreach where consented"
            owner = "Retention + Product"
            primary_kpi = "Incremental retention and product-fit completion versus randomized control"
            guardrail = "Incentive cost per retained customer and contact fatigue"
        elif "digital routine" in persona:
            action = "Test contextual self-service education and friction-free feature discovery."
            channel = "In-app contextual education"
            owner = "Digital Product + CRM"
            primary_kpi = "Feature adoption and incremental retention versus randomized control"
            guardrail = "Conversion friction, opt-outs and support contacts"
        else:
            action = "Use a lightweight preference survey before selecting a treatment; do not infer need from the segment alone."
            channel = "Consent-aware in-app survey"
            owner = "CRM Insights"
            primary_kpi = "Survey completion and incremental retention versus randomized control"
            guardrail = "Opt-outs and survey burden"
        rows.append({
            "segment_id": row.segment_id,
            "persona_name": row.persona_name,
            "priority_rank": row.priority_rank,
            "scale_exposure_rank": row.scale_exposure_rank,
            "priority_basis": "Pilot rank uses the descriptive static churn-label rate; scale-exposure rank uses its label count. Neither is expected future churn or financial value.",
            "historical_churn_exposure": int(row.historical_churn_exposure),
            "recommended_action": action,
            "owner": owner,
            "channel": channel,
            "rollout": "Randomize eligible customers within segment to treatment/control; begin with a capacity-limited pilot and pre-register eligibility.",
            "primary_success_measure": primary_kpi,
            "guardrails": guardrail,
            "stop_scale_rule": "Stop if guardrails worsen beyond a pre-specified tolerance; scale only if confidence intervals support positive incremental retention and unit economics pass break-even.",
            "break_even_formula": "required_uplift = (outreach_cost + incentive_cost + operating_cost) / (eligible_customers * value_per_retained_customer)",
        })
    return pd.DataFrame(rows)


def summarise_methods(comparison: pd.DataFrame, min_cluster_share: float) -> pd.DataFrame:
    """Retain one best diagnostic candidate per method, including rejected methods."""
    rows: list[pd.Series] = []
    for _, candidates in comparison.groupby("method", sort=True):
        eligible = candidates.loc[candidates.eligible]
        if not eligible.empty:
            selected = eligible.sort_values("selection_score", ascending=False).iloc[0].copy()
            selected["method_status"] = "eligible candidate"
        else:
            selected = candidates.sort_values(["minimum_cluster_share", "silhouette"], ascending=False).iloc[0].copy()
            selected["method_status"] = (
                f"rejected: no candidate reached minimum cluster share {min_cluster_share:.1%}"
            )
        rows.append(selected)
    return pd.DataFrame(rows).sort_values("method").reset_index(drop=True)


def _plot_method_comparison(method_summary: pd.DataFrame, output: Path) -> None:
    summary = method_summary.sort_values("selection_score", ascending=False)
    labels = [
        f"{method.replace('_', ' ').title()}\n(rejected: <5% cluster)" if status.startswith("rejected")
        else method.replace("_", " ").title()
        for method, status in zip(summary.method, summary.method_status)
    ]
    figure, axes = plt.subplots(1, 3, figsize=(14, 4.8), constrained_layout=True)
    values = [("silhouette", "Silhouette (higher better)"), ("stability_ari", "Stability ARI (higher better)"), ("davies_bouldin", "Davies–Bouldin (lower better)")]
    for axis, (column, title) in zip(axes, values):
        bars = axis.bar(labels, summary[column], color=[COLORS["green"], COLORS["light_green"], COLORS["pale_green"]])
        for bar, value in zip(bars, summary[column]):
            axis.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"{value:.3f}", ha="center", va="bottom", fontsize=8)
        axis.set_title(title, color=COLORS["deep_green"], fontweight="bold")
        axis.tick_params(axis="x", rotation=18, labelsize=8)
        axis.spines[["top", "right"]].set_visible(False)
    figure.suptitle("Illustrative segmentation method comparison | static Kaggle base + synthetic behaviour", color=COLORS["deep_green"], fontweight="bold")
    figure.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(figure)


def _plot_personas(profiles: pd.DataFrame, rfm: pd.DataFrame, output: Path) -> None:
    columns = [f"{feature}_mean" for feature in RFM_FEATURES]
    values = profiles[columns].to_numpy(dtype=float)
    cohort_mean = rfm.loc[:, RFM_FEATURES].mean().to_numpy(dtype=float)
    cohort_std = rfm.loc[:, RFM_FEATURES].std().to_numpy(dtype=float)
    standardised = (values - cohort_mean) / np.where(cohort_std == 0, 1, cohort_std)
    figure, axis = plt.subplots(figsize=(13, max(3.8, 0.8 * len(profiles) + 2)), constrained_layout=True)
    image = axis.imshow(standardised, cmap="RdYlGn", vmin=-2, vmax=2, aspect="auto")
    for row_index in range(standardised.shape[0]):
        for column_index in range(standardised.shape[1]):
            value = standardised[row_index, column_index]
            axis.text(column_index, row_index, f"{value:+.1f}", ha="center", va="center", fontsize=8, color=COLORS["ink"])
    axis.set_xticks(range(len(RFM_FEATURES)), [name.replace("_", "\n") for name in RFM_FEATURES], fontsize=8)
    axis.set_yticks(range(len(profiles)), [f"{row.segment_id}: {row.persona_name}" for row in profiles.itertuples()], fontsize=9)
    axis.set_title("Persona feature profile: standardised segment means\nSynthetic behaviour; green means above cohort mean", color=COLORS["deep_green"], fontweight="bold")
    figure.colorbar(image, ax=axis, label="Standardised mean")
    figure.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(figure)


def _plot_churn(churn_summary: pd.DataFrame, profiles: pd.DataFrame, output: Path) -> None:
    merged = churn_summary.merge(profiles[["segment_id", "persona_name"]], on="segment_id", validate="one_to_one")
    figure, axis = plt.subplots(figsize=(10, 5.2), constrained_layout=True)
    labels = [f"{row.segment_id}\n{row.persona_name}" for row in merged.itertuples()]
    rates = merged.historical_churn_rate.to_numpy()
    lower = rates - merged.churn_rate_ci95_low.to_numpy()
    upper = merged.churn_rate_ci95_high.to_numpy() - rates
    axis.bar(labels, rates, color=COLORS["green"], yerr=np.vstack([lower, upper]), capsize=4, label="Segment static churn rate (95% Wilson CI)")
    for position, row in enumerate(merged.itertuples()):
        axis.text(position, row.historical_churn_rate + 0.008, f"{row.historical_churn_rate:.1%}\nn={row.customer_count:,}", ha="center", va="bottom", fontsize=8)
    axis.axhline(float(merged.overall_historical_churn_rate.iloc[0]), color=COLORS["danger"], linestyle="--", label="Overall static-label rate")
    axis.set_ylabel("Historical/static churn-label rate")
    axis.set_ylim(0, min(1, max(0.30, float(merged.churn_rate_ci95_high.max()) * 1.25)))
    axis.tick_params(axis="x", rotation=15, labelsize=8)
    axis.set_title("Descriptive churn cross-tab by illustrative segment\nNot a prospective risk estimate or treatment effect", color=COLORS["deep_green"], fontweight="bold")
    axis.legend(fontsize=8)
    axis.spines[["top", "right"]].set_visible(False)
    figure.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(figure)


def _markdown_table(frame: pd.DataFrame) -> str:
    """Render a small Markdown table without the optional ``tabulate`` dependency."""
    headers = [str(column) for column in frame.columns]
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in frame.itertuples(index=False, name=None):
        formatted = [f"{value:.3f}" if isinstance(value, (float, np.floating)) else str(value) for value in row]
        lines.append("| " + " | ".join(formatted) + " |")
    return "\n".join(lines)


def _write_persona_document(
    path: Path,
    profiles: pd.DataFrame,
    static_profiles: pd.DataFrame,
    churn_summary: pd.DataFrame,
    scenario_profiles: pd.DataFrame,
    lens_summary: pd.DataFrame,
    strategy: pd.DataFrame,
    data_version: str,
) -> None:
    """Write a plain-language, evidence-labelled persona handoff in Vietnamese."""
    joined = profiles.merge(static_profiles, on=["segment_id", "customer_count"], validate="one_to_one")
    joined = joined.merge(churn_summary, on=["segment_id", "customer_count"], validate="one_to_one")
    joined = joined.merge(
        strategy.drop(columns=["persona_name"]), on="segment_id", validate="one_to_one"
    )
    lines = [
        "# Persona khach hang va chien luoc thu nghiem - Segmentation V2",
        "",
        "> **Canh bao pham vi:** Ho so co hai lop du lieu. Gioi tinh, quoc gia theo truong `country`, tuoi, so du, luong uoc tinh, san pham va trang thai thanh vien la truong tinh cua Kaggle. Giao dich, dang nhap, khieu nai va tin hieu pain-point/nhu cau duoc sinh bang Python cho bai tap. Khong co truong nao cho phep ket luan ly do roi bo that, nhu cau da phat bieu, hay hieu qua uu dai.",
        "",
        "## Du lieu da duoc kiem tra",
        "",
        f"- Phien ban goc: `{data_version}`, 10,000 khach hang; nhan churn tinh duoc tach khoi dau vao clustering.",
        "- Ba cach clustering da duoc so sanh trong tai lieu quyet dinh: K-Means, Gaussian Mixture va Ward hierarchical. Cac metric do do tach/stability cua du lieu hanh vi mo phong, khong do gia tri thuong mai.",
        "- Cac ty le churn ben duoi la cross-tab cua nhan Kaggle sau khi gan segment, co khoang tin cay Wilson 95%. Day la mo ta lich su/tinh, khong phai du bao quy tiep theo.",
        "- Scenario pain/need duoc sinh khong dung nhan churn. Kiem tra ky thuat gom: seed co the tai lap, mot dong/khach hang, khong null, chi nam trong tap scenario da khai bao, va label tach biet.",
        "",
        "## Quy tac su dung an toan",
        "",
        "- `country` chi la quoc gia trong source, khong phai que quan, quoc tich hay dan toc.",
        "- `estimated_salary` dung don vi tien te khong ro; khong goi la thu nhap thuc te va khong dung lam gia tri khach hang.",
        "- Gioi tinh va quoc gia chi dung de mo ta/tinh cong bang sau thi nghiem; khong dung de quyet dinh uu dai, kenh, gia hay dieu kien tham gia.",
        "",
        "## Persona chi tiet",
    ]
    for row in joined.sort_values("priority_rank").itertuples():
        scenario_rows = scenario_profiles.loc[scenario_profiles.segment_id.eq(row.segment_id)].head(3)
        scenario_text = "; ".join(
            f"{item.simulated_pain_signal}: {item.segment_share:.1%}; can test: {item.simulated_need_to_test}"
            for item in scenario_rows.itertuples()
        )
        lines.extend([
            "",
            f"### {row.segment_id} - {row.persona_name}",
            "",
            f"**Quy mo va churn da quan sat:** {row.customer_count:,} khach hang ({row.customer_share:.1%} mau). Churn tinh: {int(row.historical_churn_count):,}/{row.customer_count:,} = {row.historical_churn_rate:.1%}; Wilson 95%: {row.churn_rate_ci95_low:.1%}-{row.churn_rate_ci95_high:.1%}; toan mau: {row.overall_historical_churn_rate:.1%}.",
            "",
            f"**Chan dung tinh (du lieu Kaggle):** France {row.country_france_share:.1%}, Germany {row.country_germany_share:.1%}, Spain {row.country_spain_share:.1%}; female {row.gender_female_share:.1%}, male {row.gender_male_share:.1%}. Tuoi trung binh {row.mean_age_years:.1f}, tuoi trung vi {row.median_age_years:.1f}. Luong uoc tinh trung vi {row.median_estimated_salary_source_currency:.1f}, so du trung vi {row.median_balance_source_currency:.1f} (don vi source khong ro). Trung binh {row.mean_products:.1f} san pham; {row.active_member_share:.1%} co co active_member=1.",
            "",
            f"**Hanh vi V2 mo phong:** {row.persona_description} Ty le giao dich digital trung binh {row.digital_transaction_share_mean:.1%}; ty le thang co hoat dong {row.active_month_ratio_mean:.1%}; recency {row.recency_periods_mean:.2f} ky mo phong. Day la dau ra simulation, khong phai lich su giao dich that.",
            "",
            f"**Pain-point va mong cau trong kich ban mo phong:** {scenario_text} Khong duoc doc nhu phan hoi hay ly do roi bo cua khach hang that.",
            "",
            f"**Chien luoc de kiem chung:** {row.recommended_action} Kenh: {row.channel}. Chu so huu: {row.owner}.",
            "",
            f"**A/B test:** random hoa khach hang du dieu kien va da dong y trong chinh segment nay: treatment la journey o tren; control la trai nghiem trung lap/khong gui journey. KPI chinh: {row.primary_success_measure}. Guardrail: {row.guardrails}. {row.stop_scale_rule}",
        ])
    lines.extend([
        "",
        "## Nhieu goc nhin bo sung tu du lieu tinh",
        "",
        "Bang sau khong phai cluster. Day la cac lens tao truoc khi join churn de bo sung goc nhin relationship, do sau san pham va so du. Dung de lap ke hoach cong suat va phan tich ket qua A/B, khong dung de suy ra ly do roi bo.",
        "",
        _markdown_table(lens_summary[["lens", "group", "customer_count", "customer_share", "historical_churn_count", "historical_churn_rate", "churn_rate_ci95_low", "churn_rate_ci95_high"]]),
        "",
        "## Thong tin con thieu truoc khi goi day la insight khach hang that",
        "",
        "Can thu thap co governance: reason-for-close/cancel, noi dung va loai ticket, survey nhu cau va su hai long, preference/consent kenh, campaign assignment, chi phi, CLV/margin, va outcome retention theo mot cua so thoi gian that. Khi co, thay the scenario mo phong bang su kien quan sat va danh gia uplift bang A/B test.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_report(
    path: Path,
    champion: pd.Series,
    method_summary: pd.DataFrame,
    profiles: pd.DataFrame,
    churn_summary: pd.DataFrame,
    strategy: pd.DataFrame,
    data_version: str,
) -> None:
    pilot_segment = strategy.sort_values("priority_rank").iloc[0]
    scale_segment = strategy.sort_values("scale_exposure_rank").iloc[0]
    lines = [
        "# Segmentation v2 business decision brief",
        "",
        "> **Illustrative / synthetic extension.** Clusters use outcome-independent simulated behavioural records because the supplied base data has no observed behaviour. Static `churn` is joined only after cluster assignment. This is not prospective churn prediction, causal evidence, or measured retention value.",
        "",
        "## Executive decision",
        "",
        "- **Decision now:** approve a measurement-design and data-collection phase, not live customer targeting or financial-return claims.",
        f"- **First pilot hypothesis:** `{pilot_segment.segment_id} — {pilot_segment.persona_name}` has the highest descriptive static-label rate among the illustrative groups. Test its segment-specific treatment only with consented, randomized treatment/control eligibility.",
        f"- **Coverage hypothesis:** `{scale_segment.segment_id} — {scale_segment.persona_name}` has the largest descriptive static-label exposure count. Use it for a separate, capacity-gated coverage experiment after the first pilot's safety and economics review.",
        "- **Operating boundary:** CRM capacity, budget, value-per-retained-customer, treatment uplift and contact permissions are not in the source. The accountable owner must set those constraints before randomization; no segment should receive a blanket incentive.",
        "",
        "## Method selection",
        "",
        f"- Data version: `{data_version}`.",
        f"- Selected method: `{champion.method}`, k={int(champion.n_clusters)}; selection score={champion.selection_score:.3f}, silhouette={champion.silhouette:.3f}, stability ARI={champion.stability_ari:.3f}, Davies–Bouldin={champion.davies_bouldin:.3f}.",
        "- Compared methods: K-Means, diagonal-covariance Gaussian Mixture and Ward hierarchical clustering, over the predeclared k range. Selection weighs separation (40%), subsample-label stability (30%), Davies–Bouldin (20%) and Calinski–Harabasz (10%), after rejecting undersized clusters. Rejected methods remain in the comparison table and figure.",
        "- Cluster analysis is exploratory. Metrics assess geometric structure in simulated features; they do not validate commercial usefulness.",
        "",
        "## Method comparison",
        "",
        _markdown_table(method_summary[["method", "n_clusters", "silhouette", "stability_ari", "davies_bouldin", "calinski_harabasz", "selection_score", "method_status"]]),
        "",
        "## Segment decision register",
        "",
        "Each finding below follows the project insight contract. Counts/rates describe the supplied static label cross-tab, while behaviour is synthetic.",
    ]
    joined = profiles.merge(churn_summary, on=["segment_id", "customer_count"], validate="one_to_one").merge(
        strategy[["segment_id", "priority_rank", "scale_exposure_rank", "recommended_action", "owner", "primary_success_measure", "guardrails", "stop_scale_rule"]], on="segment_id", validate="one_to_one"
    )
    for row in joined.sort_values("priority_rank").itertuples():
        lines.extend([
            "",
            f"### {row.segment_id} — {row.persona_name}",
            "",
            f"1. **Finding:** This segment contains {row.customer_count:,} customers ({row.customer_share:.1%}) and has a historical/static churn-label rate of {row.historical_churn_rate:.1%}.",
            f"2. **Evidence:** {int(row.historical_churn_count):,}/{int(row.customer_count):,} labels are `churn=1`; 95% Wilson CI {row.churn_rate_ci95_low:.1%}–{row.churn_rate_ci95_high:.1%}; overall source rate {row.overall_historical_churn_rate:.1%}.",
            "3. **Confidence:** Counts are exact for this 10,000-row static extract; uncertainty intervals cover the label rate only. Behavioural inputs and personas are simulated, and no sampling frame or time horizon is available.",
            f"4. **Interpretation:** {row.persona_description} This is a descriptive association, not evidence that behaviour causes churn.",
            f"5. **Business impact:** Pilot priority {row.priority_rank} uses the descriptive label rate; scale-exposure rank {row.scale_exposure_rank} reflects {int(row.historical_churn_exposure):,} historical labels. Neither is revenue, CLV, expected saves or ROI; those inputs are unavailable.",
            f"6. **Recommended action:** {row.recommended_action}",
            f"7. **Execution:** Owner: {row.owner}. {strategy.loc[strategy.segment_id.eq(row.segment_id), 'rollout'].iloc[0]}",
            f"8. **Success measure:** {row.primary_success_measure}. Guardrails: {row.guardrails}. {row.stop_scale_rule}",
        ])
    lines.extend([
        "",
        "## Financial decision boundary",
        "",
        "No CLV, margin, outreach cost, incentive cost, operating cost or treatment uplift is present. Therefore no expected business value is calculated. Before a pilot is funded, estimate `required_uplift = (outreach_cost + incentive_cost + operating_cost) / (eligible_customers × value_per_retained_customer)` separately for conservative, base and optimistic assumptions approved by Finance. Do not substitute model accuracy, segment churn rate or a churn score for treatment uplift.",
        "",
        "## 30/60/90-day proposal",
        "",
        "- **0–30 days:** validate source licence, obtain observed behavioural/event history, agree eligibility and cost/CLV definitions, and pre-register a retention experiment.",
        "- **31–60 days:** run a capacity-limited randomized pilot within the two highest-priority segments; monitor opt-outs, complaints, costs and data-quality failures weekly.",
        "- **61–90 days:** evaluate incremental retention with confidence intervals and unit economics; stop, iterate or scale according to the registered rule. Replace synthetic behaviours before any operational targeting.",
    ])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_segmentation_v2(config: dict[str, Any]) -> SegmentationResult:
    """Run v2 augmentation and the end-to-end illustrative segmentation pipeline."""
    if config.get("segmentation_version") != SEGMENTATION_VERSION:
        raise ValueError(f"Expected segmentation_version '{SEGMENTATION_VERSION}'")
    base_data_dir = Path(config["base_data_dir"])
    augmented_data_dir = Path(config["augmentation_data_dir"])
    output_dir = Path(config["output_dir"])
    figures_dir = output_dir / "figures"
    seed = int(config["seed"])
    periods = int(config["synthetic_periods"])
    customer_path = base_data_dir / "customers_clean.csv"
    label_path = base_data_dir / "labels_clean.csv"
    manifest_path = base_data_dir / "manifest.json"
    customers = pd.read_csv(customer_path, dtype={"customer_id": "string"})
    labels = pd.read_csv(label_path, dtype={"customer_id": "string"})
    data_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    behavior = generate_synthetic_behavior(customers, seed=seed, periods=periods)
    rfm = build_rfm_features(behavior, periods=periods)
    persona_scenarios = generate_synthetic_persona_scenarios(customers, rfm)
    augmented_customers = build_augmented_customer_table(customers, rfm)
    matrix, preprocessing_metadata = prepare_clustering_matrix(rfm)
    evaluation_sample_size = min(int(config["evaluation_sample_size"]), len(matrix))
    evaluation_indices = np.sort(np.random.default_rng(seed).choice(len(matrix), size=evaluation_sample_size, replace=False))
    evaluation_matrix = matrix[evaluation_indices]
    comparison, fitted = compare_clustering_methods(
        evaluation_matrix,
        methods=METHODS,
        candidate_clusters=range(int(config["min_clusters"]), int(config["max_clusters"]) + 1),
        seed=seed,
        stability_repeats=int(config["stability_repeats"]),
        min_cluster_share=float(config["min_cluster_share"]),
    )
    champion = _select_champion(comparison)
    chosen_key = champion.candidate_id
    if champion.method in {"kmeans", "gaussian_mixture"}:
        raw_labels, _ = _fit_labels(str(champion.method), matrix, int(champion.n_clusters), seed)
        full_cohort_assignment = "Selected model refit on the full cohort after candidate selection."
    else:
        sample_labels, sample_centroids = fitted[chosen_key]
        raw_labels = _nearest_centroid_labels(matrix, sample_centroids)
        full_cohort_assignment = (
            "Ward clustering was fitted on the fixed evaluation sample; full-cohort rows are assigned to "
            "sample-derived centroids. This is an explicit deployment approximation."
        )
    canonical_labels, raw_mapping = _canonical_segments(raw_labels, rfm)
    assignments = pd.DataFrame({"customer_id": rfm.customer_id, "segment_id": canonical_labels})
    profiles = profile_segments(assignments, rfm)
    static_profiles = build_static_persona_profile(assignments, customers)
    scenario_profiles = profile_synthetic_persona_scenarios(assignments, persona_scenarios)
    churn_summary = churn_cross_tab(assignments, labels)
    static_lenses = build_static_lenses(customers)
    lens_summary = summarise_static_lenses(static_lenses, labels)
    strategy = build_retention_strategy(profiles, churn_summary)
    method_summary = summarise_methods(comparison, float(config["min_cluster_share"]))
    output_dir.mkdir(parents=True, exist_ok=True)
    augmented_data_dir.mkdir(parents=True, exist_ok=True)
    figures_dir.mkdir(parents=True, exist_ok=True)
    behavior_path = augmented_data_dir / "synthetic_behavior_v2.csv"
    rfm_path = augmented_data_dir / "behavioral_rfm_features_v2.csv"
    scenario_path = augmented_data_dir / "synthetic_persona_scenarios_v2.csv"
    augmented_customer_path = augmented_data_dir / "customers_augmented_behavioral_v2.csv"
    behavior.to_csv(behavior_path, index=False)
    rfm.to_csv(rfm_path, index=False)
    persona_scenarios.to_csv(scenario_path, index=False)
    augmented_customers.to_csv(augmented_customer_path, index=False)
    augmentation_manifest = {
        "augmentation_version": BEHAVIOR_VERSION,
        "data_version": data_manifest["data_version"],
        "mode": "illustrative_synthetic_extension",
        "row_grain": {
            "synthetic_behavior_v2.csv": "one customer × simulated period",
            "behavioral_rfm_features_v2.csv": "one customer",
            "synthetic_persona_scenarios_v2.csv": "one customer; auditable scenario signals derived from simulated behaviour; churn excluded",
            "customers_augmented_behavioral_v2.csv": "one customer; static base attributes + synthetic RFM features; churn excluded",
        },
        "source_separation": {
            "kaggle_base": "Static profile attributes are retained with source_type=kaggle_base.",
            "synthetic_behavior": "Generated behavioural/RFM values are marked behavior_source_type=synthetic_behavior.",
            "synthetic_persona_scenario": "Generated pain/need/journey scenario fields are marked source_type=synthetic_persona_scenario; they are not observed customer statements.",
            "label": "churn remains only in labels_clean.csv and is excluded from every augmentation output.",
        },
        "generation": {
            "seed": seed,
            "periods": periods,
            "outcome_independence": "The generator receives no churn label and does not condition values on churn.",
            "time_limitation": "period_index is simulated and cannot support temporal or next-quarter claims.",
        },
        "output_hashes": {
            "synthetic_behavior_v2.csv": _sha256(behavior_path),
            "behavioral_rfm_features_v2.csv": _sha256(rfm_path),
            "synthetic_persona_scenarios_v2.csv": _sha256(scenario_path),
            "customers_augmented_behavioral_v2.csv": _sha256(augmented_customer_path),
        },
    }
    _write_json(augmented_data_dir / "augmentation_manifest_v2.json", augmentation_manifest)
    comparison.to_csv(output_dir / "method_comparison.csv", index=False)
    method_summary.to_csv(output_dir / "method_summary.csv", index=False)
    assignments.to_csv(output_dir / "segment_assignments.csv", index=False)
    profiles.to_csv(output_dir / "segment_personas.csv", index=False)
    static_profiles.to_csv(output_dir / "segment_static_personas.csv", index=False)
    scenario_profiles.to_csv(output_dir / "segment_synthetic_scenarios.csv", index=False)
    churn_summary.to_csv(output_dir / "segment_churn_cross_tab.csv", index=False)
    lens_summary.to_csv(output_dir / "static_lens_churn_cross_tab.csv", index=False)
    strategy.to_csv(output_dir / "retention_strategy.csv", index=False)
    _plot_method_comparison(method_summary, figures_dir / "method_comparison.png")
    _plot_personas(profiles, rfm, figures_dir / "persona_profiles.png")
    _plot_churn(churn_summary, profiles, figures_dir / "segment_churn_cross_tab.png")
    report_path = output_dir / "segmentation_report.md"
    _write_report(report_path, champion, method_summary, profiles, churn_summary, strategy, data_manifest["data_version"])
    decision_document_path = Path(config["decision_document_path"])
    _write_report(decision_document_path, champion, method_summary, profiles, churn_summary, strategy, data_manifest["data_version"])
    persona_document_path = Path(config["persona_document_path"])
    _write_persona_document(
        persona_document_path,
        profiles,
        static_profiles,
        churn_summary,
        scenario_profiles,
        lens_summary,
        strategy,
        data_manifest["data_version"],
    )
    manifest = {
        "segmentation_version": SEGMENTATION_VERSION,
        "behavior_generation_version": BEHAVIOR_VERSION,
        "mode": "illustrative_synthetic_extension",
        "data_version": data_manifest["data_version"],
        "input_hashes": {"customers_clean.csv": _sha256(customer_path), "labels_clean.csv": _sha256(label_path)},
        "synthetic_assumptions": {
            "seed": seed,
            "periods": periods,
            "outcome_independence": "The behaviour generator accepts customer attributes only; it does not read, receive or condition on churn labels.",
            "time_limitation": "period_index is a simulated sequence, not a real observation window or temporal validation basis.",
        },
        "feature_preprocessing": preprocessing_metadata,
        "selection_protocol": {
            "methods": list(METHODS),
            "cluster_range": [int(config["min_clusters"]), int(config["max_clusters"])],
            "minimum_cluster_share": float(config["min_cluster_share"]),
            "stability_repeats": int(config["stability_repeats"]),
            "evaluation_sample_size": evaluation_sample_size,
            "silhouette_sample_size": min(1000, evaluation_sample_size),
            "evaluation_sample_rule": "Fixed-seed simple random sample drawn before clustering; no labels are used.",
            "score_weights": {"silhouette": 0.40, "stability_ari": 0.30, "davies_bouldin": 0.20, "calinski_harabasz": 0.10},
        },
        "full_cohort_assignment": full_cohort_assignment,
        "selected_candidate": champion.to_dict(),
        "raw_to_canonical_segment_id": {str(key): value for key, value in raw_mapping.items()},
        "limitations": [
            "Clusters are based on synthetic behaviour and cannot demonstrate real customer behaviour or demand.",
            "Persona pain/need/journey fields are synthetic scenario design inputs, not observed customer statements or churn reasons.",
            "Churn cross-tabs are descriptive static-label associations, not prospective prediction, treatment uplift or causality.",
            "No CLV, cost or intervention outcome supports financial return claims.",
        ],
    }
    _write_json(output_dir / "segmentation_manifest.json", manifest)
    return SegmentationResult(str(champion.method), int(champion.n_clusters), output_dir, report_path)
