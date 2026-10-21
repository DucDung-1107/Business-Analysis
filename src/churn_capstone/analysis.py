"""Analyst seam: descriptive demo outputs, no intervention-effect claims."""


def summarize(features, customers, behavior):
    return {
        "mode": "demo", "customer_count": len(features),
        "monthly_rows": len(behavior),
        "mean_age": float(features.age.mean()),
        "mean_balance": float(features.balance.mean()),
        "customers_without_behavior": len(set(customers.customer_id) - set(behavior.customer_id)),
        "kpis": {
            "churn_rate": {"value": None, "status": "unavailable: no observed outcome labels"},
            "clv": {"value": None, "status": "unavailable: no margin/lifetime data"},
            "retention_cost": {"value": None, "status": "unavailable: no campaign costs"},
        },
    }
