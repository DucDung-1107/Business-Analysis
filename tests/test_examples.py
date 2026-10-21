import json
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

from churn_capstone.api import PredictRequest, PredictResponse, create_app
from churn_capstone.contracts import Customer, FeatureRow, MonthlyBehavior, read_table
from churn_capstone.features import build_features


def test_examples_match_contract_and_runtime(demo_dir):
    root = Path("examples")
    customers = read_table(root / "customers.csv", Customer)
    behavior = read_table(root / "monthly_behavior.csv", MonthlyBehavior)
    features = read_table(root / "features.csv", FeatureRow)
    pd.testing.assert_frame_equal(features, build_features(customers, behavior, "2026-04-01"))
    request = json.loads((root / "predict_request.json").read_text())
    expected = json.loads((root / "predict_response.json").read_text())
    PredictRequest.model_validate(request)
    PredictResponse.model_validate(expected)
    with TestClient(create_app(demo_dir)) as client:
        assert client.post("/predict", json=request).json() == expected
    assert json.loads((root / "predict_request.schema.json").read_text()) == PredictRequest.model_json_schema()
    assert json.loads((root / "predict_response.schema.json").read_text()) == PredictResponse.model_json_schema()
