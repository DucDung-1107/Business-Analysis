# Monitoring and deployment handoff

## Demo behavior

`churn monitor` compares features.csv to reference_features.csv, writes monitoring.json, and reports waiting_for_labels. `churn features` refreshes the demo reference; this is only for a repeatable fixture. PSI uses reference quantile bins, infinite tails, 1e-6 smoothing and special bins for constant columns. An individual feature PSI >=0.2 triggers investigation. This threshold is a demo default requiring review with meaningful sample sizes; small batches can be noisy.

No automatic retraining occurs. Drift does not establish performance deterioration. Customer IDs and labels are excluded from drift features.

## Real implementation checklist for MLOps

1. Save an immutable reference distribution/version from the actual training set. Separate its location from incoming batches. Do not overwrite it during routine inference.
2. Log model and contract versions, observation time, batch ID, prediction timestamp, batch size, missing/invalid input counts and prediction/segment summaries. Public deployments must use fictional data only unless explicitly authorized.
3. Store actual outcomes with their prediction/observation linkage and horizon. Join after labels mature. Current v1 performance helper accepts one completely labeled customer snapshot, aligns by ID and rejects partial/mismatched labels. Multiple dates require a versioned customer-date contract first.
4. Calculate precision, recall and F1 with a documented threshold; add ROC-AUC, PR-AUC and capacity metrics for real model evaluation. Define monitoring intervals and minimum sample counts before operational use.
5. Investigate any PSI alert, schema failure or performance decline. Retraining proposal: two consecutive sufficiently sized labeled batches below the agreed baseline recall/F1 guardrails, or sustained confirmed drift with performance impact. Numeric performance guardrails must be agreed from baseline evidence, not invented now.
6. Retrain offline, compare against champion on held-out data and approve rollout. Version artifacts atomically; keep the previous artifact set for rollback. Reload API only with a compatible complete set.

## Deployment task for a later phase

Package `uvicorn churn_capstone.api:app --host 0.0.0.0 --port <provider-port>` with the validated artifact set, and run Streamlit as a separately configured service. Set CHURN_API_URL to the reachable API URL and CHURN_ARTIFACT_DIR consistently. Verify health/startup, browser lookup, missing-artifact failure and monitoring visibility. Choose free hosting after checking its current constraints; no cloud service or live link is provisioned by this scaffold.
