"""Shared contract v1. Changes require leader review and coordinated migration."""
from typing import Annotated, Literal

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, StringConstraints

CONTRACT_VERSION = "1.0"
CustomerId = Annotated[str, StringConstraints(strict=True, min_length=1, pattern=r"^\S+$")]
Count = Annotated[int, Field(strict=True, ge=0)]
Money = Annotated[float, Field(strict=True, ge=0, allow_inf_nan=False)]


class Row(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Customer(Row):
    customer_id: CustomerId
    age: Annotated[int, Field(strict=True, ge=18, le=100)]
    balance: Money
    country: Literal["France", "Germany", "Spain"]


class MonthlyBehavior(Row):
    customer_id: CustomerId
    month: Annotated[str, StringConstraints(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")]
    transaction_count: Count
    transaction_amount: Money
    login_count: Count
    complaint_count: Count
    mobile_count: Count
    atm_count: Count
    branch_count: Count


class FeatureRow(Row):
    customer_id: CustomerId
    age: Annotated[int, Field(strict=True, ge=18, le=100)]
    balance: Money
    transaction_count: Count
    transaction_amount: Money
    login_count: Count
    complaint_count: Count
    mobile_share: Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)]


FEATURE_COLUMNS = tuple(name for name in FeatureRow.model_fields if name != "customer_id")


class LabelRow(Row):
    customer_id: CustomerId
    churn: Annotated[int, Field(strict=True, ge=0, le=1)]


class RiskRow(Row):
    customer_id: CustomerId
    risk_score: Annotated[float, Field(strict=True, ge=0, le=1, allow_inf_nan=False)]


class SegmentRow(Row):
    customer_id: CustomerId
    segment_id: Annotated[str, StringConstraints(min_length=1)]


class SegmentProfile(Row):
    segment_id: Annotated[str, StringConstraints(min_length=1)]
    segment_name: Annotated[str, StringConstraints(min_length=1)]
    description: Annotated[str, StringConstraints(min_length=1)]
    customer_count: Count


KEYS = {MonthlyBehavior: ["customer_id", "month"], SegmentProfile: ["segment_id"]}


def validate_table(frame: pd.DataFrame, schema: type[Row], *, allow_empty=False) -> pd.DataFrame:
    """Reject missing/extra columns, nulls, invalid values and duplicate keys."""
    expected = set(schema.model_fields)
    if set(frame.columns) != expected:
        raise ValueError(f"{schema.__name__}: expected columns {sorted(expected)}")
    if frame.empty and not allow_empty:
        raise ValueError(f"{schema.__name__}: table must not be empty")
    if frame.isna().any().any():
        raise ValueError(f"{schema.__name__}: missing values are not allowed")
    for record in frame.to_dict("records"):
        schema.model_validate(record)
    keys = KEYS.get(schema, ["customer_id"])
    if frame.duplicated(keys).any():
        raise ValueError(f"{schema.__name__}: duplicate keys {keys}")
    if schema is MonthlyBehavior:
        channels = frame[["mobile_count", "atm_count", "branch_count"]].sum(axis=1)
        if not channels.eq(frame.transaction_count).all():
            raise ValueError("Channel counts must sum to transaction_count")
    return frame


def read_table(path, schema: type[Row]) -> pd.DataFrame:
    # Keep string IDs, including leading zeroes. Never infer them as numeric.
    frame = pd.read_csv(path, dtype={"customer_id": "string", "segment_id": "string"})
    return validate_table(frame, schema)


def same_customers(expected: pd.DataFrame, actual: pd.DataFrame) -> None:
    if actual.customer_id.duplicated().any() or set(expected.customer_id) != set(actual.customer_id):
        raise ValueError("Output customer IDs must match input exactly once")


def numeric_features(frame: pd.DataFrame) -> np.ndarray:
    validate_table(frame, FeatureRow)
    return frame[list(FEATURE_COLUMNS)].to_numpy(dtype=float)
