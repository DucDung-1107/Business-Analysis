"""Leader-owned drift and delayed-label performance monitoring."""
import numpy as np

from .contracts import FEATURE_COLUMNS, FeatureRow, LabelRow, RiskRow, same_customers, validate_table


def drift_report(reference, current, threshold=0.2):
    validate_table(reference, FeatureRow)
    validate_table(current, FeatureRow)
    if threshold <= 0:
        raise ValueError("PSI threshold must be positive")
    metrics = {}
    for column in FEATURE_COLUMNS:
        ref, cur = reference[column].to_numpy(float), current[column].to_numpy(float)
        # Reference quantiles only. Add a finite center for constant reference columns.
        inner = np.unique(np.quantile(ref, np.linspace(0.1, 0.9, 9)))
        if ref.min() == ref.max():
            v = ref[0]
            inner = np.array([v - max(abs(v) * 0.01, 0.5), v + max(abs(v) * 0.01, 0.5)])
        edges = np.r_[-np.inf, inner, np.inf]
        p = np.histogram(ref, edges)[0] / len(ref)
        q = np.histogram(cur, edges)[0] / len(cur)
        p, q = np.maximum(p, 1e-6), np.maximum(q, 1e-6)
        psi = float(np.sum((q - p) * np.log(q / p)))
        metrics[column] = {"psi": psi, "investigate": psi >= threshold}
    return dict(threshold=threshold, features=metrics,
                investigation_required=any(m["investigate"] for m in metrics.values()),
                action="Investigate drift; retraining requires review and labeled evaluation.")


def performance_report(predictions, labels=None, threshold=0.5):
    risks = validate_table(predictions[["customer_id", "risk_score"]], RiskRow)
    if not 0 <= threshold <= 1:
        raise ValueError("Decision threshold must be within [0, 1]")
    if labels is None:
        return {"status": "waiting_for_labels", "metrics": None}
    validate_table(labels, LabelRow)
    same_customers(risks, labels)
    joined = risks.merge(labels, on="customer_id", validate="one_to_one")
    predicted = joined.risk_score >= threshold
    actual = joined.churn == 1
    tp = int((predicted & actual).sum())
    fp = int((predicted & ~actual).sum())
    fn = int((~predicted & actual).sum())
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {"status": "evaluated", "threshold": threshold, "rows": len(joined), "metrics": {
        "precision": precision, "recall": recall,
        "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
    }}
