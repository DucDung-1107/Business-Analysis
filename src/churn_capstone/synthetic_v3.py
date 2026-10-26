"""V3 synthetic bank-event generator with explicit relational grains.

The generator is intentionally label-free.  It creates a teaching simulation,
not reconstructed bank history.  Each output has a source tag and is validated
before it can feed segmentation.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


SOURCE = "SYNTHETIC_BEHAVIOR"
MONTHS = 6


def generate_bank_tables(customers: pd.DataFrame, *, seed: int, months: int = MONTHS) -> dict[str, pd.DataFrame]:
    """Return consistent customer-month, transaction, digital and service facts.

    ``customers`` must not contain a churn label. Incoming flow is a synthetic
    cash-flow event, not a claim that estimated salary is paid into the bank.
    Loan repayment exists only for a separately generated synthetic loan holding.
    """
    if "churn" in customers or customers.customer_id.duplicated().any() or months < 6:
        raise ValueError("V3 requires unique label-free customers and at least six simulated months")
    rng = np.random.default_rng(seed)
    base = customers.reset_index(drop=True)
    n = len(base)
    active = base.active_member.to_numpy(float)
    products = base.products_number.to_numpy(int)
    salary = base.estimated_salary.to_numpy(float)
    age = base.age.to_numpy(float)
    digital_affinity = np.clip(0.25 + 0.55 * active - 0.006 * (age - 40) + rng.normal(0, 0.12, n), 0.05, 0.95)
    cashflow_regularity = np.clip(0.20 + 0.60 * active + 0.06 * (products > 1) + rng.normal(0, 0.14, n), 0.05, 0.95)
    service_propensity = np.clip(0.04 + 0.10 * (1 - active) + rng.normal(0, 0.035, n), 0.005, 0.35)
    has_loan = (products >= 3) & (rng.random(n) < 0.45)
    holdings = pd.DataFrame({"customer_id": base.customer_id, "product_type": np.where(has_loan, "synthetic_installment_loan", "synthetic_deposit_relationship"), "source_tag": SOURCE})
    snapshots: list[pd.DataFrame] = []
    transactions: list[pd.DataFrame] = []
    digitals: list[pd.DataFrame] = []
    cases: list[pd.DataFrame] = []
    for month in range(1, months + 1):
        inflow_event = rng.random(n) < cashflow_regularity
        inflow = np.where(inflow_event, salary / 12 * rng.lognormal(0, 0.12, n), 0.0)
        app_days = np.minimum(30, rng.poisson(np.clip(2 + 8 * digital_affinity + 3 * active, 0.1, 25)))
        card_count = rng.poisson(np.clip(1 + 4 * digital_affinity + active, 0.05, 30))
        cash_count = rng.poisson(np.clip(0.4 + 2 * (1 - digital_affinity), 0.02, 15))
        bill_count = rng.poisson(np.clip(0.5 + 0.5 * active, 0.02, 8))
        card_amount = card_count * rng.lognormal(3.4, 0.45, n)
        cash_amount = cash_count * rng.lognormal(3.2, 0.40, n)
        bill_amount = bill_count * rng.lognormal(3.7, 0.35, n)
        loan_amount = np.where(has_loan, rng.lognormal(4.1, 0.18, n), 0.0)
        failed = rng.poisson(np.clip(0.03 + 0.25 * service_propensity + 0.04 * (1 - active), 0.001, 1.5))
        opened = rng.binomial(1, service_propensity)
        resolved = opened * rng.binomial(1, 0.76)
        snapshots.append(pd.DataFrame({"customer_id": base.customer_id, "month_index": month, "inbound_flow_amount": np.round(inflow, 2), "outbound_flow_amount": np.round(card_amount + cash_amount + bill_amount + loan_amount, 2), "source_tag": SOURCE}))
        transactions.append(pd.concat([
            pd.DataFrame({"customer_id": base.customer_id, "month_index": month, "typical_day_of_month": rng.integers(1, 29, n), "channel": "mobile", "transaction_type": "card_purchase", "transaction_count": card_count, "transaction_amount": np.round(card_amount, 2)}),
            pd.DataFrame({"customer_id": base.customer_id, "month_index": month, "typical_day_of_month": rng.integers(1, 29, n), "channel": "atm", "transaction_type": "cash_withdrawal", "transaction_count": cash_count, "transaction_amount": np.round(cash_amount, 2)}),
            pd.DataFrame({"customer_id": base.customer_id, "month_index": month, "typical_day_of_month": rng.integers(1, 29, n), "channel": "mobile", "transaction_type": "bill_payment", "transaction_count": bill_count, "transaction_amount": np.round(bill_amount, 2)}),
        ]))
        digitals.append(pd.DataFrame({"customer_id": base.customer_id, "month_index": month, "app_active_days": app_days, "app_sessions": app_days + rng.poisson(2, n), "primary_app_feature": np.where(digital_affinity > .65, "transfers_and_bill_pay", np.where(active > 0, "balance_and_card_controls", "account_status_check")), "failed_payment_count": failed, "source_tag": SOURCE}))
        opened_ids = base.loc[opened.astype(bool), "customer_id"].reset_index(drop=True)
        if not opened_ids.empty:
            cases.append(pd.DataFrame({"service_case_id": [f"SIM-{month}-{i}" for i in range(len(opened_ids))], "customer_id": opened_ids, "opened_month_index": month, "resolved_month_index": np.where(resolved[opened.astype(bool)] == 1, month, 0), "category": rng.choice(["payment_support", "digital_help", "account_query"], len(opened_ids)), "severity": rng.choice(["low", "medium", "high"], len(opened_ids), p=[0.65, 0.28, 0.07]), "source_tag": SOURCE}))
    result = {"product_holding": holdings, "customer_snapshot": pd.concat(snapshots, ignore_index=True), "transaction_month": pd.concat(transactions, ignore_index=True).assign(source_tag=SOURCE), "digital_month": pd.concat(digitals, ignore_index=True), "service_case": pd.concat(cases, ignore_index=True) if cases else pd.DataFrame(columns=["service_case_id", "customer_id", "opened_month_index", "resolved_month_index", "category", "severity", "source_tag"])}
    validate_bank_tables(base, result, months)
    return result


def validate_bank_tables(customers: pd.DataFrame, tables: dict[str, pd.DataFrame], months: int) -> None:
    """Fail on broken grains, impossible amounts or case timelines."""
    ids = set(customers.customer_id)
    snapshot = tables["customer_snapshot"]
    if len(snapshot) != len(customers) * months or snapshot.duplicated(["customer_id", "month_index"]).any():
        raise ValueError("customer_snapshot grain is invalid")
    transaction = tables["transaction_month"]
    if not set(transaction.customer_id).issubset(ids) or (transaction.transaction_count < 0).any() or (transaction.transaction_amount < 0).any():
        raise ValueError("transaction facts are invalid")
    digital = tables["digital_month"]
    if not digital.app_active_days.between(0, 31).all() or (digital.app_sessions < digital.app_active_days).any():
        raise ValueError("digital facts are invalid")
    cases = tables["service_case"]
    if not cases.empty and ((cases.resolved_month_index.ne(0)) & (cases.resolved_month_index < cases.opened_month_index)).any():
        raise ValueError("service case timeline is invalid")


def build_feature_snapshot(tables: dict[str, pd.DataFrame], *, cutoff_month: int = MONTHS) -> pd.DataFrame:
    """Build cutoff-safe behavioural features at one row per customer."""
    transaction = tables["transaction_month"].query("month_index <= @cutoff_month")
    digital = tables["digital_month"].query("month_index <= @cutoff_month")
    snapshot = tables["customer_snapshot"].query("month_index <= @cutoff_month")
    cases = tables["service_case"].query("opened_month_index <= @cutoff_month")
    features = transaction.groupby("customer_id").agg(
        transaction_count_6m=("transaction_count", "sum"), transaction_amount_6m=("transaction_amount", "sum"),
        digital_transaction_share=("channel", lambda values: float((values == "mobile").mean())),
        cash_withdrawal_share=("transaction_type", lambda values: float((values == "cash_withdrawal").mean())),
    )
    digital_features = digital.groupby("customer_id").agg(app_active_days_6m=("app_active_days", "sum"), app_sessions_6m=("app_sessions", "sum"), failed_payments_6m=("failed_payment_count", "sum"))
    flow = snapshot.groupby("customer_id").agg(inflow_6m=("inbound_flow_amount", "sum"), inflow_months=("inbound_flow_amount", lambda values: int((values > 0).sum())), outflow_6m=("outbound_flow_amount", "sum"))
    case_features = cases.groupby("customer_id").agg(service_cases_6m=("service_case_id", "size"), unresolved_cases_6m=("resolved_month_index", lambda values: int((values == 0).sum())))
    output = features.join(digital_features).join(flow).join(case_features).fillna(0).reset_index()
    early = snapshot.query("month_index <= @cutoff_month // 2").groupby("customer_id").inbound_flow_amount.mean()
    late = snapshot.query("month_index > @cutoff_month // 2").groupby("customer_id").inbound_flow_amount.mean()
    output["inflow_trend_ratio"] = output.customer_id.map(np.log1p(late).sub(np.log1p(early))).fillna(0.0)
    output["unresolved_case_share"] = output.unresolved_cases_6m.div(output.service_cases_6m.where(output.service_cases_6m > 0, 1))
    if output.isna().any().any() or output.customer_id.duplicated().any():
        raise ValueError("feature snapshot invariant failed")
    return output
