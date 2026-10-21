from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient

from churn_capstone.api import create_app
from churn_capstone.monitoring import drift_report, performance_report


def test_api_validates_and_predicts(demo_dir, features):
    with TestClient(create_app(demo_dir)) as client:
        assert client.get("/health").json()["mode"] == "demo"
        body = {"contract_version": "1.0", "customers": features.head(2).to_dict("records")}
        response = client.post("/predict", json=body)
        assert response.status_code == 200
        assert len(response.json()["predictions"]) == 2
        for bad in [
            {**body, "contract_version": "2.0"}, {**body, "customers": []},
            {**body, "customers": [body["customers"][0]] * 2},
            {**body, "customers": [{**body["customers"][0], "churn": 1}]},
            {**body, "customers": [{**body["customers"][0], "age": "42"}]},
        ]:
            assert client.post("/predict", json=bad).status_code == 422


def test_startup_requires_artifacts(tmp_path):
    with pytest.raises(FileNotFoundError):
        with TestClient(create_app(tmp_path)):
            pass


def test_drift_stable_and_shifted(features):
    assert not drift_report(features, features)["investigation_required"]
    shifted = features.copy()
    shifted["balance"] += 1000000
    assert drift_report(features, shifted)["features"]["balance"]["investigate"]


def test_constant_reference_detects_shift(features):
    reference = features.copy()
    reference["balance"] = 0.0
    incoming = reference.copy()
    incoming["balance"] = 500.0
    assert drift_report(reference, incoming)["features"]["balance"]["investigate"]


def test_delayed_and_misaligned_labels():
    predictions = pd.DataFrame({"customer_id": ["a", "b"], "risk_score": [0.9, 0.1]})
    assert performance_report(predictions)["status"] == "waiting_for_labels"
    labels = pd.DataFrame({"customer_id": ["b", "a"], "churn": [0, 1]})
    assert performance_report(predictions, labels)["metrics"]["f1"] == 1
    with pytest.raises(ValueError):
        performance_report(predictions, labels.iloc[:1])


def test_streamlit_app_renders_demo(demo_dir, monkeypatch):
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("CHURN_ARTIFACT_DIR", str(demo_dir))
    app = AppTest.from_file(Path("app/streamlit_app.py").resolve()).run(timeout=20)
    assert not app.exception
    assert len(app.selectbox[0].options) == 24


def test_dashboard_lookup_and_api_outage(demo_dir, monkeypatch):
    import httpx
    from streamlit.testing.v1 import AppTest
    monkeypatch.setenv("CHURN_ARTIFACT_DIR", str(demo_dir))
    with TestClient(create_app(demo_dir)) as client:
        def api_post(url, **kwargs):
            return client.post("/predict", json=kwargs["json"])
        monkeypatch.setattr(httpx, "post", api_post)
        app = AppTest.from_file(Path("app/streamlit_app.py").resolve()).run(timeout=20)
        app.button[0].click().run(timeout=20)
        assert not app.exception
        assert app.metric[0].label == "Demo risk score"
        def unavailable(*args, **kwargs):
            raise httpx.ConnectError("API unavailable")
        monkeypatch.setattr(httpx, "post", unavailable)
        app.button[0].click().run(timeout=20)
        assert not app.exception
        assert "Lookup unavailable" in app.error[0].value


def test_api_rejects_invalid_model_output(demo_dir, features):
    class BrokenClassifier:
        def predict_risk(self, frame):
            return pd.DataFrame({"customer_id": frame.customer_id, "risk_score": 2.0})
    app = create_app(demo_dir)
    with TestClient(app) as client:
        _, segmenter, profiles, versions = app.state.runtime
        app.state.runtime = (BrokenClassifier(), segmenter, profiles, versions)
        response = client.post("/predict", json={
            "contract_version": "1.0", "customers": features.head(1).to_dict("records"),
        })
        assert response.status_code == 500
        assert response.json()["detail"] == "Model output violated the integration contract"
