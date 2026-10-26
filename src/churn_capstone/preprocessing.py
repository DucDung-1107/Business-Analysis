"""Deterministic preprocessing for the static Kaggle churn base data (v1).

This module deliberately does not manufacture a time index or behavioural data.
The source label is a historical/static ``churn`` label, so its outputs must not
be described as next-quarter predictions without a separate temporal study.
"""
from __future__ import annotations

import hashlib
import json
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd


PREPROCESSING_VERSION = "kaggle-static-preprocess-v1"
SOURCE_TYPE = "kaggle_base"
CUSTOMER_COLUMNS = (
    "customer_id",
    "credit_score",
    "country",
    "gender",
    "age",
    "tenure",
    "balance",
    "products_number",
    "credit_card",
    "active_member",
    "estimated_salary",
    "source_type",
)
LABEL_COLUMNS = ("customer_id", "churn")

_ALIASES = {
    "customerid": "customer_id",
    "creditscore": "credit_score",
    "geography": "country",
    "country": "country",
    "gender": "gender",
    "age": "age",
    "tenure": "tenure",
    "balance": "balance",
    "numofproducts": "products_number",
    "productsnumber": "products_number",
    "hascrcard": "credit_card",
    "creditcard": "credit_card",
    "isactivemember": "active_member",
    "activemember": "active_member",
    "estimatedsalary": "estimated_salary",
    "churn": "churn",
    "exited": "churn",
}
_IGNORED_SOURCE_COLUMNS = {"rownumber", "surname"}
_REQUIRED_COLUMNS = set(CUSTOMER_COLUMNS) - {"source_type"} | {"churn"}
_NUMERIC_COLUMNS = (
    "credit_score",
    "age",
    "tenure",
    "balance",
    "products_number",
    "credit_card",
    "active_member",
    "estimated_salary",
    "churn",
)
_INTEGER_COLUMNS = (
    "credit_score",
    "age",
    "tenure",
    "products_number",
    "credit_card",
    "active_member",
    "churn",
)
_RANGES = {
    "credit_score": (300, 850),
    "age": (18, 100),
    "tenure": (0, 10),
    "balance": (0, None),
    "products_number": (1, 4),
    "credit_card": (0, 1),
    "active_member": (0, 1),
    "estimated_salary": (0, None),
    "churn": (0, 1),
}
_COUNTRY_MAP = {"france": "France", "germany": "Germany", "spain": "Spain"}
_GENDER_MAP = {"female": "Female", "male": "Male"}


class DataValidationError(ValueError):
    """Raised when the raw source violates a critical preprocessing invariant."""


@dataclass(frozen=True)
class PreprocessResult:
    """Locations and deterministic identifiers produced by one preprocessing run."""

    customer_path: Path
    label_path: Path
    manifest_path: Path
    version_id: str
    rows_output: int


def _normalise_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.casefold())


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_sha256(value: dict[str, Any]) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _atomic_csv(frame: pd.DataFrame, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", delete=False, dir=destination.parent, suffix=".tmp"
    ) as temporary:
        temporary_path = Path(temporary.name)
        frame.to_csv(temporary, index=False, lineterminator="\n")
    temporary_path.replace(destination)


def _atomic_json(value: dict[str, Any], destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", newline="", delete=False, dir=destination.parent, suffix=".tmp"
    ) as temporary:
        temporary_path = Path(temporary.name)
        json.dump(value, temporary, indent=2, sort_keys=True, allow_nan=False)
        temporary.write("\n")
    temporary_path.replace(destination)


def _canonicalise_columns(frame: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Map supported Kaggle header variants to the v1 source schema."""
    renamed: dict[str, str] = {}
    ignored: list[str] = []
    unknown: list[str] = []
    for column in frame.columns:
        normalised = _normalise_name(str(column))
        if normalised in _IGNORED_SOURCE_COLUMNS:
            ignored.append(str(column))
        elif normalised in _ALIASES:
            target = _ALIASES[normalised]
            if target in renamed.values():
                raise DataValidationError(f"Multiple source columns map to '{target}'")
            renamed[str(column)] = target
        else:
            unknown.append(str(column))
    if unknown:
        raise DataValidationError(f"Unexpected source columns: {sorted(unknown)}")
    result = frame.drop(columns=ignored).rename(columns=renamed)
    missing = sorted(_REQUIRED_COLUMNS - set(result.columns))
    if missing:
        raise DataValidationError(f"Missing required source columns: {missing}")
    return result, sorted(ignored)


def _normalise_category(series: pd.Series, values: dict[str, str], field: str) -> pd.Series:
    normalised = series.astype("string").str.strip().str.casefold()
    result = normalised.map(values).astype("string")
    invalid = int(result.isna().sum())
    if invalid:
        observed = sorted(normalised.dropna().unique().tolist())
        raise DataValidationError(f"{field} has {invalid} missing or invalid values; observed={observed}")
    return result


def _normalise_numeric(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for column in _NUMERIC_COLUMNS:
        values = pd.to_numeric(result[column], errors="coerce")
        invalid = int(values.isna().sum())
        if invalid:
            raise DataValidationError(f"{column} has {invalid} missing or non-numeric values")
        lower, upper = _RANGES[column]
        in_range = values.ge(lower) if upper is None else values.between(lower, upper)
        if not bool(in_range.all()):
            bad_count = int((~in_range).sum())
            raise DataValidationError(
                f"{column} has {bad_count} values outside the allowed range [{lower}, {upper}]"
            )
        if column in _INTEGER_COLUMNS:
            if not bool(values.mod(1).eq(0).all()):
                raise DataValidationError(f"{column} must contain whole numbers")
            result[column] = values.astype("int64")
        else:
            result[column] = values.astype("float64")
    return result


def clean_kaggle_churn(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    """Validate and clean a static Kaggle churn extract without imputing or dropping rows."""
    rows_read = len(frame)
    canonical, ignored_columns = _canonicalise_columns(frame)
    canonical["customer_id"] = canonical["customer_id"].astype("string").str.strip()
    if canonical["customer_id"].isna().any() or canonical["customer_id"].eq("").any():
        raise DataValidationError("customer_id contains a missing or blank value")
    if canonical["customer_id"].duplicated().any():
        raise DataValidationError("customer_id must be unique before preprocessing")
    canonical["country"] = _normalise_category(canonical["country"], _COUNTRY_MAP, "country")
    canonical["gender"] = _normalise_category(canonical["gender"], _GENDER_MAP, "gender")
    canonical = _normalise_numeric(canonical)
    canonical["source_type"] = SOURCE_TYPE
    customers = canonical.loc[:, CUSTOMER_COLUMNS].copy()
    labels = canonical.loc[:, LABEL_COLUMNS].copy()
    audit = {
        "rows_read": rows_read,
        "rows_output": len(customers),
        "rows_dropped": 0,
        "nulls_before_cleaning": {column: int(frame[column].isna().sum()) for column in frame.columns},
        "nulls_after_cleaning": {column: int(customers[column].isna().sum()) for column in customers.columns},
        "duplicate_customer_ids_before_cleaning": int(canonical["customer_id"].duplicated().sum()),
        "duplicate_rows_before_cleaning": int(frame.duplicated().sum()),
        "ignored_source_columns": ignored_columns,
        "target_separation": {
            "label_column": "churn",
            "included_in_customer_table": False,
            "rule": "The target is written only to labels_clean.csv and is unavailable to preprocessing outputs intended as features.",
        },
        "label_summary": {
            "positive_count": int(labels["churn"].sum()),
            "negative_count": int((labels["churn"] == 0).sum()),
            "positive_prevalence": float(labels["churn"].mean()),
        },
        "row_policy": "No imputation or row deletion; fail on a critical schema, null, duplicate, or bounds violation.",
    }
    return customers, labels, audit


def preprocess_kaggle_churn(
    raw_path: Path,
    output_dir: Path,
    config: dict[str, Any],
) -> PreprocessResult:
    """Create immutable v1 cleaned tables and a provenance manifest from a raw CSV."""
    raw_path = Path(raw_path)
    output_dir = Path(output_dir)
    if not raw_path.is_file():
        raise FileNotFoundError(f"Raw data file not found: {raw_path}")
    if config.get("preprocessing_version") != PREPROCESSING_VERSION:
        raise ValueError(f"Expected preprocessing_version '{PREPROCESSING_VERSION}'")
    raw_hash = _file_sha256(raw_path)
    config_hash = _json_sha256(config)
    raw = pd.read_csv(raw_path, dtype="string")
    customers, labels, audit = clean_kaggle_churn(raw)
    version_id = f"v1-{raw_hash[:12]}-{config_hash[:8]}"
    customer_path = output_dir / "customers_clean.csv"
    label_path = output_dir / "labels_clean.csv"
    manifest_path = output_dir / "manifest.json"
    _atomic_csv(customers, customer_path)
    _atomic_csv(labels, label_path)
    manifest = {
        "data_version": version_id,
        "preprocessing_version": PREPROCESSING_VERSION,
        "source_type": SOURCE_TYPE,
        "source_file": raw_path.name,
        "source_file_sha256": raw_hash,
        "config_sha256": config_hash,
        "label_definition": "Static source column 'churn'; no prospectively validated next-quarter outcome is available.",
        "output_files": {
            "customers_clean.csv": _file_sha256(customer_path),
            "labels_clean.csv": _file_sha256(label_path),
        },
        "audit": audit,
    }
    _atomic_json(manifest, manifest_path)
    audit_path = config.get("audit_output_path")
    if audit_path:
        _atomic_json(manifest, Path(audit_path))
    return PreprocessResult(customer_path, label_path, manifest_path, version_id, len(customers))
