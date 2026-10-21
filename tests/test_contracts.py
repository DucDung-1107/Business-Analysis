import pandas as pd
import pytest

from churn_capstone.contracts import Customer, FeatureRow, MonthlyBehavior, read_table, validate_table
from churn_capstone.data import generate_demo, validate_inputs
from churn_capstone.features import build_features


def test_reproducible(tables):
    for expected, actual in zip(tables, generate_demo()):
        pd.testing.assert_frame_equal(expected, actual)


@pytest.mark.parametrize("mutation", ["missing", "extra", "null", "duplicate", "id_type", "range"])
def test_customer_contract_rejects_broken_handoffs(tables, mutation):
    frame = tables[0].copy()
    if mutation == "missing":
        frame = frame.drop(columns="age")
    elif mutation == "extra":
        frame["churn"] = 0
    elif mutation == "null":
        frame.loc[0, "balance"] = None
    elif mutation == "duplicate":
        frame = pd.concat([frame, frame.iloc[[0]]])
    elif mutation == "id_type":
        frame["customer_id"] = range(len(frame))
    elif mutation == "range":
        frame.loc[0, "age"] = 200
    with pytest.raises(ValueError):
        validate_table(frame, Customer)


def test_monthly_contracts(tables):
    customers, behavior = tables
    broken = behavior.copy()
    broken.loc[0, "mobile_count"] += 1
    with pytest.raises(ValueError, match="Channel"):
        validate_table(broken, MonthlyBehavior)
    broken = behavior.copy()
    broken.loc[0, "customer_id"] = "unknown"
    with pytest.raises(ValueError, match="unknown"):
        validate_inputs(customers, broken)
    broken = behavior.copy()
    broken.loc[0, "month"] = "2026-13"
    with pytest.raises(ValueError):
        validate_inputs(customers, broken)


def test_string_id_survives_csv(tmp_path, tables):
    customers = tables[0].copy()
    customers["customer_id"] = [f"{i:05d}" for i in range(len(customers))]
    path = tmp_path / "customers.csv"
    customers.to_csv(path, index=False)
    assert read_table(path, Customer).iloc[0].customer_id == "00000"


def test_future_and_partial_month_excluded(tables, features):
    customers, behavior = tables
    later = behavior.loc[behavior.month == "2026-03"].copy()
    later["month"] = "2026-04"
    pd.testing.assert_frame_equal(features, build_features(
        customers, pd.concat([behavior, later]), "2026-04-15"
    ))
    march = behavior.loc[behavior.month == "2026-03"]
    expected = march.groupby("customer_id").login_count.sum()
    actual = build_features(customers, behavior, "2026-04-01", 1).set_index("customer_id")
    pd.testing.assert_series_equal(actual.login_count, expected, check_names=False)


def test_missing_activity_becomes_zero(tables):
    customers, behavior = tables
    customer_id = customers.iloc[0].customer_id
    result = build_features(customers, behavior.loc[behavior.customer_id != customer_id], "2026-04-01")
    row = result.loc[result.customer_id == customer_id].iloc[0]
    assert row.login_count == row.transaction_count == row.mobile_share == 0


def test_labels_rejected_as_features(features):
    features["churn"] = 1
    with pytest.raises(ValueError):
        validate_table(features, FeatureRow)
