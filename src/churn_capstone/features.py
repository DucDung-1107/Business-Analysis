"""Classification owner coordinates this seam with Data Engineer."""
import pandas as pd

from .contracts import FeatureRow, validate_table
from .data import validate_inputs


def build_features(customers, behavior, as_of_date: str, observation_months: int = 3):
    """Use N completed calendar months strictly before as_of_date's month.

    Month-grain inputs cannot safely use the current partial month. Customers with
    no observations receive zero activity; coverage is reported separately in EDA.
    """
    validate_inputs(customers, behavior)
    if not isinstance(observation_months, int) or observation_months < 1:
        raise ValueError("observation_months must be a positive integer")
    cutoff = pd.Timestamp(as_of_date)
    if pd.isna(cutoff) or cutoff.tzinfo is not None:
        raise ValueError("as_of_date must be a valid timezone-naive date")
    end = cutoff.to_period("M")
    months = pd.PeriodIndex(behavior.month, freq="M")
    selected = behavior.loc[(months >= end - observation_months) & (months < end)]
    totals = selected.groupby("customer_id")[[
        "transaction_count", "transaction_amount", "login_count", "complaint_count", "mobile_count"
    ]].sum()
    result = customers[["customer_id", "age", "balance"]].merge(
        totals, left_on="customer_id", right_index=True, how="left", validate="one_to_one"
    ).fillna(0)
    result["mobile_share"] = result.mobile_count.div(
        result.transaction_count.where(result.transaction_count > 0, 1)
    )
    result = result.drop(columns="mobile_count")
    for name in ["transaction_count", "login_count", "complaint_count"]:
        result[name] = result[name].astype(int)
    return validate_table(result, FeatureRow)
