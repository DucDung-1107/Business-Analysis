import pandas as pd

from churn_capstone.preprocessing import clean_kaggle_churn
from churn_capstone.synthetic_v3 import build_feature_snapshot, generate_bank_tables
from churn_capstone.segmentation_v3 import distinctiveness, fit_behavior_segments, multi_seed_diagnostics


def test_v3_tables_have_valid_grains_and_no_churn_field():
    raw = pd.DataFrame({"customer_id": ["a", "b"], "credit_score": [600, 700], "country": ["France", "Spain"], "gender": ["Female", "Male"], "age": [30, 45], "tenure": [2, 4], "balance": [100.0, 200.0], "products_number": [1, 3], "credit_card": [1, 1], "active_member": [1, 0], "estimated_salary": [60000.0, 80000.0], "churn": [0, 1]})
    customers, _labels, _audit = clean_kaggle_churn(raw)
    tables = generate_bank_tables(customers, seed=9)
    assert len(tables["customer_snapshot"]) == 12
    assert tables["customer_snapshot"].customer_id.nunique() == 2
    assert "churn" not in tables["transaction_month"].columns
    assert tables["service_case"].resolved_month_index.ge(0).all()
    features = build_feature_snapshot(tables)
    assert len(features) == 2
    assert features.isna().sum().sum() == 0
    assignments, metrics = fit_behavior_segments(features, seed=9)
    assert len(assignments) == 2 and pd.isna(metrics["silhouette"])
    assert len(distinctiveness(features, assignments)) > 0
    assert len(multi_seed_diagnostics(customers, seeds=(1, 2))) == 2
