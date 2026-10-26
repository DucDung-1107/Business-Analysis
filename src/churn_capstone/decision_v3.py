"""V3 decision cube and pre-registered pilot design; all economics are scenarios."""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


def _sample_per_arm(baseline: float, mde: float, z_alpha: float = 1.96, z_power: float = 0.842) -> int:
    """Normal-approximation sample size for a two-arm proportion comparison."""
    p2 = baseline + mde
    return int(np.ceil(((z_alpha * np.sqrt(2 * baseline * (1 - baseline)) + z_power * np.sqrt(baseline * (1-baseline) + p2 * (1-p2))) ** 2) / mde**2))


def run(output_dir: Path = Path("reports/segmentation/v3")) -> None:
    features = pd.read_csv(output_dir / "feature_snapshot.csv", dtype={"customer_id": "string"})
    assignments = pd.read_csv(output_dir / "assignments.csv", dtype={"customer_id": "string"})
    customers = pd.read_csv("data/processed/kaggle_churn_v1/customers_clean.csv", dtype={"customer_id": "string"})
    cube = assignments.merge(features, on="customer_id", validate="one_to_one").merge(customers[["customer_id", "active_member", "products_number"]], on="customer_id", validate="one_to_one")
    cube["relationship_lens"] = np.where(cube.active_member.eq(1), "recorded_active", "recorded_not_active")
    cube["service_policy"] = np.where(cube.unresolved_cases_6m.gt(0), "service_recovery_required", "eligible_for_experiment")
    cube["value_scenario"] = pd.qcut(cube.inflow_6m.rank(method="first"), 3, labels=["lower_simulated_cashflow", "middle_simulated_cashflow", "upper_simulated_cashflow"])
    summary = cube.groupby(["segment_id", "relationship_lens", "service_policy", "value_scenario"], observed=True).size().reset_index(name="customer_count")
    summary = summary.loc[summary.customer_count.ge(30)].sort_values("customer_count", ascending=False)
    pilots = pd.DataFrame([
        {"pilot": "P1_reactivation", "segment": "segment_lower_digital", "arm_a": "service_recovery", "arm_b": "reactivation_coach", "primary_outcome": "90_day_active_month_rate", "baseline_assumption": 0.50, "mde_assumption": 0.03, "sample_per_arm": _sample_per_arm(0.50, 0.03), "eligibility": "eligible_for_experiment; consent and contact-cap verification required", "hard_stop": "consent breach or unresolved complaint mis-routed"},
        {"pilot": "P2_retention", "segment": "segment_high_digital", "arm_a": "digital_concierge", "arm_b": "value_review", "primary_outcome": "90_day_retention", "baseline_assumption": 0.85, "mde_assumption": 0.02, "sample_per_arm": _sample_per_arm(0.85, 0.02), "eligibility": "eligible_for_experiment; consent and contact-cap verification required", "hard_stop": "consent breach or complaint/opt-out guardrail breach"},
    ])
    summary.to_csv(output_dir / "decision_cube_v3.csv", index=False); pilots.to_csv(output_dir / "pilot_protocol_v3.csv", index=False)
    fig, ax = plt.subplots(figsize=(10, 5), constrained_layout=True)
    pivot = summary.pivot_table(index="segment_id", columns="service_policy", values="customer_count", aggfunc="sum", fill_value=0)
    pivot.plot(kind="bar", stacked=True, color=["#55A67A", "#B64E50"], ax=ax)
    ax.set_ylabel("Customers"); ax.set_title("V3 decision cube: experiment eligibility versus service recovery")
    fig.savefig(output_dir / "v3_decision_cube.png", dpi=180); plt.close(fig)
    (output_dir / "pilot_assumptions.json").write_text(json.dumps({"alpha": 0.05, "power": 0.80, "note": "MDE and baseline are planning assumptions, not observed uplift or financial return."}, indent=2), encoding="utf-8")


if __name__ == "__main__":
    run()
