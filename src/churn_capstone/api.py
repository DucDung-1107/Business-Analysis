"""API startup loads validated artifacts once; failures stop startup visibly."""
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, Literal

import pandas as pd
from fastapi import FastAPI, HTTPException, Request
from pydantic import Field, model_validator

from .contracts import CONTRACT_VERSION, FeatureRow, RiskRow, Row, SegmentProfile, read_table
from .integration import load_runtime, predict


class PredictRequest(Row):
    contract_version: Literal["1.0"]
    customers: Annotated[list[FeatureRow], Field(min_length=1, max_length=1000)]

    @model_validator(mode="after")
    def unique_ids(self):
        ids = [row.customer_id for row in self.customers]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate customer IDs")
        return self


class Prediction(RiskRow):
    segment_id: str


class PredictResponse(Row):
    mode: Literal["demo"]
    contract_version: str
    model_versions: dict[str, str]
    predictions: list[Prediction]


def create_app(artifact_dir=None):
    directory = Path(artifact_dir or os.getenv("CHURN_ARTIFACT_DIR", "artifacts/demo"))

    @asynccontextmanager
    async def lifespan(app):
        classifier, segmenter, versions = load_runtime(directory)
        profiles = read_table(directory / "segment_profiles.csv", SegmentProfile)
        app.state.runtime = (classifier, segmenter, profiles, versions)
        yield

    app = FastAPI(title="Bank Churn Capstone — Demo", version="0.1.0", lifespan=lifespan)

    @app.get("/health")
    def health(request: Request):
        return dict(status="ready", mode="demo", contract_version=CONTRACT_VERSION,
                    model_versions=request.app.state.runtime[3])

    @app.post("/predict", response_model=PredictResponse)
    def predict_batch(body: PredictRequest, request: Request):
        classifier, segmenter, profiles, versions = request.app.state.runtime
        frame = pd.DataFrame([row.model_dump() for row in body.customers])
        try:
            output = predict(frame, classifier, segmenter, profiles)
        except ValueError as error:
            # Input was validated; this indicates a broken model/contract, not a user error.
            raise HTTPException(500, "Model output violated the integration contract") from error
        return dict(mode="demo", contract_version=CONTRACT_VERSION, model_versions=versions,
                    predictions=output.to_dict("records"))

    return app


app = create_app()
