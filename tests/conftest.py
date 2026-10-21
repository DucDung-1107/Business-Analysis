import json
from pathlib import Path

import pytest

from churn_capstone.cli import STAGES, run_stage
from churn_capstone.data import generate_demo
from churn_capstone.features import build_features


@pytest.fixture
def tables():
    return generate_demo()


@pytest.fixture
def features(tables):
    return build_features(*tables, "2026-04-01")


@pytest.fixture
def demo_dir(tmp_path):
    config = json.loads(Path("configs/demo.json").read_text())
    for stage in STAGES:
        run_stage(stage, tmp_path, config)
    return tmp_path
