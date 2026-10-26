"""Decision-grade V3 segmentation visuals from persisted artifacts."""
from pathlib import Path
import pandas as pd
from matplotlib import pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

FEATURES = ["transaction_count_6m", "transaction_amount_6m", "app_active_days_6m", "failed_payments_6m", "inflow_6m", "inflow_months", "cash_withdrawal_share", "inflow_trend_ratio", "unresolved_case_share"]


def render(output: Path = Path("reports/segmentation/v3")) -> None:
    features = pd.read_csv(output / "feature_snapshot.csv", dtype={"customer_id": "string"})
    assignments = pd.read_csv(output / "assignments.csv", dtype={"customer_id": "string"})
    frame = features.merge(assignments, on="customer_id", validate="one_to_one")
    matrix = frame[FEATURES].copy()
    for col in ["transaction_count_6m", "transaction_amount_6m", "app_active_days_6m", "failed_payments_6m", "inflow_6m"]:
        matrix[col] = (matrix[col] + 1).map(__import__("math").log)
    xy = PCA(n_components=2, random_state=0).fit_transform(StandardScaler().fit_transform(matrix))
    fig, ax = plt.subplots(figsize=(9, 6), constrained_layout=True)
    colors = {"segment_high_digital": "#286B52", "segment_lower_digital": "#B64E50"}
    labels = {"segment_high_digital": "Dùng số thường xuyên", "segment_lower_digital": "Dùng số thấp"}
    for segment in colors:
        mask = frame.segment_id.eq(segment)
        ax.scatter(xy[mask, 0], xy[mask, 1], s=7, alpha=.22, color=colors[segment], label=f"{labels[segment]} (n={mask.sum():,})")
    ax.set_title("Hai phân khúc hành vi trong mô phỏng sáu tháng")
    ax.set_xlabel("Trục hành vi 1"); ax.set_ylabel("Trục hành vi 2")
    ax.legend(); ax.text(.01, -.16, "Mỗi chấm là một khách. Hai trục là PCA của 9 feature hành vi; chỉ để nhìn cấu trúc, không phải điểm rủi ro.", transform=ax.transAxes, fontsize=8)
    fig.savefig(output / "v3_cluster_map.png", dpi=180); plt.close(fig)


if __name__ == "__main__":
    render()
