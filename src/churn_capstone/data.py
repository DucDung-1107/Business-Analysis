"""Data Engineer seam: replace fixture generation with documented real generation."""
import numpy as np
import pandas as pd

from .contracts import Customer, MonthlyBehavior, validate_table


def generate_demo(seed: int = 42, n_customers: int = 24):
    if n_customers < 2:
        raise ValueError("At least two customers required")
    rng = np.random.default_rng(seed)
    customers = pd.DataFrame({
        "customer_id": [f"DEMO-{i:04d}" for i in range(n_customers)],
        "age": rng.integers(18, 76, n_customers),
        "balance": rng.uniform(0, 100000, n_customers).round(2),
        "country": rng.choice(["France", "Germany", "Spain"], n_customers),
    })
    rows = []
    for customer_id in customers.customer_id:
        for month in ["2026-01", "2026-02", "2026-03"]:
            count = int(rng.integers(0, 50))
            mobile, atm, branch = map(int, rng.multinomial(count, [0.7, 0.2, 0.1]))
            rows.append(dict(
                customer_id=customer_id, month=month, transaction_count=count,
                transaction_amount=round(float(count * rng.uniform(10, 100)), 2),
                login_count=int(rng.integers(0, 60)), complaint_count=int(rng.integers(0, 3)),
                mobile_count=mobile, atm_count=atm, branch_count=branch,
            ))
    behavior = pd.DataFrame(rows)
    validate_inputs(customers, behavior)
    return customers, behavior


def validate_inputs(customers, behavior):
    validate_table(customers, Customer)
    validate_table(behavior, MonthlyBehavior)
    if not set(behavior.customer_id).issubset(set(customers.customer_id)):
        raise ValueError("Behavior contains unknown customer IDs")
    return {
        "status": "passed", "customer_rows": len(customers),
        "behavior_rows": len(behavior), "missing_values": 0, "duplicate_keys": 0,
    }
