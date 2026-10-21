"""Segmentation seam. Rules here are wiring fixtures, not discovered clusters."""
from dataclasses import dataclass
from typing import Protocol

import numpy as np
import pandas as pd

from .contracts import CONTRACT_VERSION, FEATURE_COLUMNS, numeric_features


class Segmenter(Protocol):
    def assign_segments(self, features: pd.DataFrame) -> pd.DataFrame: ...


@dataclass
class DemoSegmenter:
    def assign_segments(self, features):
        numeric_features(features)
        return pd.DataFrame({"customer_id": features.customer_id,
                             "segment_id": np.where(features.login_count >= 80, "demo-1", "demo-0")})


def build_bundle(features):
    numeric_features(features)
    return dict(contract_version=CONTRACT_VERSION, model_version="demo-segmenter-v1", mode="demo",
                kind="segmenter", implementation="demo-v1", feature_columns=list(FEATURE_COLUMNS),
                preprocessing="identity-demo-v1")


def load_model(bundle) -> Segmenter:
    if bundle["implementation"] != "demo-v1":
        raise ValueError("Unsupported segmentation implementation")
    return DemoSegmenter()


def describe_segments(assignments):
    counts = assignments.segment_id.value_counts()
    return pd.DataFrame([
        dict(segment_id=key, segment_name=f"Demo activity group {key[-1]}",
             description="Rule-based fixture; replace with an evidence-based cluster profile.",
             customer_count=int(counts.get(key, 0)))
        for key in ["demo-0", "demo-1"]
    ])
