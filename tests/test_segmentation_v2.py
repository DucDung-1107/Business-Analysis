import pandas as pd

from churn_capstone.preprocessing import clean_kaggle_churn
from churn_capstone.segmentation_v2 import (
    METHODS,
    build_augmented_customer_table,
    build_rfm_features,
    build_static_lenses,
    compare_clustering_methods,
    generate_synthetic_behavior,
    generate_synthetic_persona_scenarios,
    profile_synthetic_persona_scenarios,
    prepare_clustering_matrix,
    summarise_static_lenses,
)


def _customers(n_customers=60):
    index = range(n_customers)
    raw = pd.DataFrame({
        "customer_id": [f"{number:04d}" for number in index],
        "credit_score": [500 + number % 200 for number in index],
        "country": ["France", "Germany", "Spain"] * (n_customers // 3),
        "gender": ["Female", "Male"] * (n_customers // 2),
        "age": [25 + number % 45 for number in index],
        "tenure": [number % 11 for number in index],
        "balance": [float(number * 1000) for number in index],
        "products_number": [1 + number % 4 for number in index],
        "credit_card": [number % 2 for number in index],
        "active_member": [(number // 2) % 2 for number in index],
        "estimated_salary": [50000.0 + number * 1000 for number in index],
        "churn": [number % 2 for number in index],
    })
    return clean_kaggle_churn(raw)[0]


def test_synthetic_behaviour_is_reproducible_and_has_no_label_input():
    customers = _customers()
    first = generate_synthetic_behavior(customers, seed=7, periods=3)
    second = generate_synthetic_behavior(customers, seed=7, periods=3)
    pd.testing.assert_frame_equal(first, second)
    assert "churn" not in first.columns
    assert first.groupby("customer_id").size().eq(3).all()
    assert first[["mobile_count", "atm_count", "branch_count"]].sum(axis=1).eq(first.transaction_count).all()


def test_three_clustering_methods_compare_without_target_leakage():
    behaviour = generate_synthetic_behavior(_customers(), seed=7, periods=3)
    rfm = build_rfm_features(behaviour, periods=3)
    matrix, metadata = prepare_clustering_matrix(rfm)
    comparison, _ = compare_clustering_methods(
        matrix,
        methods=METHODS,
        candidate_clusters=[2, 3],
        seed=7,
        stability_repeats=2,
        min_cluster_share=0.05,
    )
    assert set(comparison.method) == set(METHODS)
    assert len(comparison) == 6
    assert "churn" not in metadata["feature_columns"]
    assert comparison.eligible.any()


def test_augmented_customer_table_keeps_label_separate():
    customers = _customers()
    behaviour = generate_synthetic_behavior(customers, seed=7, periods=3)
    augmented = build_augmented_customer_table(customers, build_rfm_features(behaviour, periods=3))
    assert len(augmented) == len(customers)
    assert "churn" not in augmented.columns
    assert augmented.behavior_source_type.eq("synthetic_behavior").all()


def test_synthetic_persona_scenarios_are_label_free_and_profiled_by_segment():
    customers = _customers()
    behaviour = generate_synthetic_behavior(customers, seed=7, periods=3)
    rfm = build_rfm_features(behaviour, periods=3)
    scenarios = generate_synthetic_persona_scenarios(customers, rfm)
    assignments = rfm.loc[:, ["customer_id"]].copy()
    assignments["segment_id"] = ["segment_01"] * 30 + ["segment_02"] * 30
    summary = profile_synthetic_persona_scenarios(assignments, scenarios)
    assert "churn" not in scenarios.columns
    assert scenarios.customer_id.is_unique
    assert scenarios.source_type.eq("synthetic_persona_scenario").all()
    assert summary.groupby("segment_id").segment_share.sum().eq(1.0).all()


def test_static_lens_cross_tab_joins_labels_only_after_lenses_exist():
    customers = _customers()
    labels = pd.DataFrame({"customer_id": customers.customer_id, "churn": [number % 2 for number in range(60)]})
    summary = summarise_static_lenses(build_static_lenses(customers), labels)
    assert set(summary.lens) == {"relationship_lens", "product_lens", "balance_lens"}
    assert summary.customer_count.sum() == len(customers) * 3
    assert summary.historical_churn_rate.between(0, 1).all()
