import json

import pandas as pd
import pytest

from churn_capstone.classification import DemoClassifier
from churn_capstone.contracts import FeatureRow, SegmentProfile, read_table
from churn_capstone.integration import load_bundle, load_runtime, predict, write_json
from churn_capstone.segmentation import DemoSegmenter, describe_segments


def test_complete_demo_and_reload(demo_dir):
    results = pd.read_csv(demo_dir / "predictions.csv", dtype={"customer_id": "string"})
    features = read_table(demo_dir / "features.csv", FeatureRow)
    profiles = read_table(demo_dir / "segment_profiles.csv", SegmentProfile)
    classifier, segmenter, versions = load_runtime(demo_dir)
    pd.testing.assert_frame_equal(results, predict(features, classifier, segmenter, profiles))
    assert "demo" in versions["classifier"]
    report = json.loads((demo_dir / "monitoring.json").read_text())
    assert not report["investigation_required"]
    assert report["performance"]["status"] == "waiting_for_labels"
    assert set(results.customer_id) == set(features.customer_id)


@pytest.mark.parametrize("field,value", [
    ("contract_version", "9.0"), ("kind", "segmenter"),
    ("feature_columns", ["churn"]), ("mode", "production"),
    ("preprocessing", "unknown"),
])
def test_bad_bundle_rejected(demo_dir, field, value):
    path = demo_dir / "classifier.json"
    bundle = json.loads(path.read_text())
    bundle[field] = value
    write_json(path, bundle)
    with pytest.raises(ValueError):
        load_bundle(path, "classifier")


@pytest.mark.parametrize("problem", ["missing_id", "duplicate_id", "invalid_score", "wrong_id"])
def test_broken_classifier_handoff(features, problem):
    class BrokenClassifier:
        def predict_risk(self, frame):
            output = DemoClassifier().predict_risk(frame)
            if problem == "missing_id":
                return output.iloc[1:]
            if problem == "duplicate_id":
                return pd.concat([output, output.iloc[[0]]])
            if problem == "invalid_score":
                output.loc[0, "risk_score"] = 9
            if problem == "wrong_id":
                output.loc[0, "customer_id"] = "stranger"
            return output
    segmenter = DemoSegmenter()
    profiles = describe_segments(segmenter.assign_segments(features))
    with pytest.raises(ValueError):
        predict(features, BrokenClassifier(), segmenter, profiles)


def test_replacement_implementation_and_reordered_outputs(features):
    class ReplacementClassifier:
        def predict_risk(self, frame):
            return pd.DataFrame({"customer_id": frame.customer_id, "risk_score": 0.42}).iloc[::-1]
    class ReplacementSegmenter:
        def assign_segments(self, frame):
            return pd.DataFrame({"customer_id": frame.customer_id, "segment_id": "new"}).iloc[::-1]
    profiles = pd.DataFrame([dict(segment_id="new", segment_name="Replacement",
                                  description="Interface compatibility test", customer_count=len(features))])
    output = predict(features, ReplacementClassifier(), ReplacementSegmenter(), profiles)
    assert output.customer_id.tolist() == features.customer_id.tolist()
    assert output.risk_score.eq(0.42).all()
    assert output.segment_id.eq("new").all()


def test_unknown_segment_rejected(features):
    profiles = pd.DataFrame([dict(segment_id="unknown", segment_name="Unknown",
                                  description="Invalid profile mapping", customer_count=0)])
    with pytest.raises(ValueError, match="Unknown segment"):
        predict(features, DemoClassifier(), DemoSegmenter(), profiles)
