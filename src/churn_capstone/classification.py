"""Classification seam. This deterministic stub is NOT a trained classifier."""
from dataclasses import dataclass
from typing import Protocol

import numpy as np
import pandas as pd

from .contracts import CONTRACT_VERSION, FEATURE_COLUMNS, numeric_features


class Classifier(Protocol):
    def predict_risk(self, features: pd.DataFrame) -> pd.DataFrame: ...


@dataclass
class DemoClassifier:
    def predict_risk(self, features):
        numeric_features(features)
        # Wiring fixture only: no labels, training, causal or probability claim.
        score = np.clip(0.2 + features.complaint_count * 0.08 - features.login_count * 0.001, 0, 1)
        return pd.DataFrame({"customer_id": features.customer_id, "risk_score": score})


def build_bundle(features):
    numeric_features(features)
    return dict(contract_version=CONTRACT_VERSION, model_version="demo-classifier-v1",
                mode="demo", kind="classifier", implementation="demo-v1",
                feature_columns=list(FEATURE_COLUMNS), preprocessing="identity-demo-v1")


def load_model(bundle) -> Classifier:
    # Real owner replaces this loader and supplies preprocessing inside the bundle.
    if bundle["implementation"] != "demo-v1":
        raise ValueError("Unsupported classifier implementation")
    return DemoClassifier()
