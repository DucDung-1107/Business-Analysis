import json

import pandas as pd
import pytest

from churn_capstone.preprocessing import (
    DataValidationError,
    PREPROCESSING_VERSION,
    clean_kaggle_churn,
    preprocess_kaggle_churn,
)


@pytest.fixture
def raw_frame():
    return pd.DataFrame({
        "customer_id": ["001", "002"],
        "credit_score": [619, 608],
        "country": [" france ", "SPAIN"],
        "gender": ["Female", "male"],
        "age": [42, 41],
        "tenure": [2, 1],
        "balance": [0.0, 83807.86],
        "products_number": [1, 1],
        "credit_card": [1, 0],
        "active_member": [1, 1],
        "estimated_salary": [101348.88, 112542.58],
        "churn": [1, 0],
    })


def test_cleaning_preserves_label_separation_and_provenance(raw_frame):
    customers, labels, audit = clean_kaggle_churn(raw_frame)
    assert customers.customer_id.tolist() == ["001", "002"]
    assert customers.country.tolist() == ["France", "Spain"]
    assert customers.gender.tolist() == ["Female", "Male"]
    assert customers.source_type.eq("kaggle_base").all()
    assert labels.to_dict("records") == [{"customer_id": "001", "churn": 1}, {"customer_id": "002", "churn": 0}]
    assert audit["rows_dropped"] == 0
    assert not audit["target_separation"]["included_in_customer_table"]


@pytest.mark.parametrize("column,value", [("customer_id", "001"), ("age", 101), ("churn", 3)])
def test_critical_data_errors_fail_loudly(raw_frame, column, value):
    broken = raw_frame.copy()
    broken.loc[1, column] = value
    with pytest.raises(DataValidationError):
        clean_kaggle_churn(broken)


def test_preprocessing_writes_hashed_reproducible_manifest(tmp_path, raw_frame):
    raw_path = tmp_path / "raw.csv"
    raw_frame.to_csv(raw_path, index=False)
    config = {
        "preprocessing_version": PREPROCESSING_VERSION,
        "raw_path": str(raw_path),
        "output_dir": str(tmp_path / "processed"),
        "audit_output_path": str(tmp_path / "audit.json"),
    }
    first = preprocess_kaggle_churn(raw_path, tmp_path / "processed", config)
    manifest = json.loads(first.manifest_path.read_text())
    second = preprocess_kaggle_churn(raw_path, tmp_path / "processed_again", config)
    assert first.version_id == second.version_id
    assert manifest["audit"]["rows_output"] == 2
    assert manifest["source_file_sha256"]
    assert (tmp_path / "audit.json").is_file()
