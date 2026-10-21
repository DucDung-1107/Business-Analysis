"""Leader-owned joins and artifact validation. Never depend on output row order."""
import json
from pathlib import Path

from . import classification, segmentation
from .contracts import (
    CONTRACT_VERSION, FEATURE_COLUMNS, FeatureRow, RiskRow, SegmentProfile, SegmentRow,
    same_customers, validate_table,
)


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def load_bundle(path, kind):
    bundle = json.loads(Path(path).read_text(encoding="utf-8"))
    if bundle.get("contract_version") != CONTRACT_VERSION:
        raise ValueError("Incompatible contract version")
    if bundle.get("kind") != kind or bundle.get("feature_columns") != list(FEATURE_COLUMNS):
        raise ValueError("Incompatible bundle kind or feature schema")
    if bundle.get("mode") != "demo" or not bundle.get("model_version"):
        raise ValueError("This backbone loader only supports explicit demo bundles")
    if bundle.get("preprocessing") != "identity-demo-v1":
        raise ValueError("Unsupported preprocessing")
    return bundle


def predict(features, classifier, segmenter, profiles):
    validate_table(features, FeatureRow)
    validate_table(profiles, SegmentProfile)
    risks = validate_table(classifier.predict_risk(features.copy()), RiskRow)
    segments = validate_table(segmenter.assign_segments(features.copy()), SegmentRow)
    same_customers(features, risks)
    same_customers(features, segments)
    if not set(segments.segment_id).issubset(set(profiles.segment_id)):
        raise ValueError("Unknown segment ID: no segment profile available")
    merged = features[["customer_id"]].merge(risks, on="customer_id", validate="one_to_one")
    merged = merged.merge(segments, on="customer_id", validate="one_to_one")
    same_customers(features, merged)
    return merged


def load_runtime(directory):
    directory = Path(directory)
    classifier_bundle = load_bundle(directory / "classifier.json", "classifier")
    segmenter_bundle = load_bundle(directory / "segmenter.json", "segmenter")
    return classification.load_model(classifier_bundle), segmentation.load_model(segmenter_bundle), {
        "classifier": classifier_bundle["model_version"],
        "segmenter": segmenter_bundle["model_version"],
    }
