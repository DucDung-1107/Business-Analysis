# Five-person work assignment and handoff

Assign actual names to the roles below at kick-off. Each member begins with `churn demo` and their test commands. Existing fixtures let everyone work in parallel. Code and documentation are English. Leader: @Nituv05.

| Role | Own modules | Prerequisite | Required deliverables |
| --- | --- | --- | --- |
| Data Engineer | data.py; raw/synthetic generation and validation | contracts and source audit | reproducible generator, integration/cleaning code, quality report, full dictionary, assumptions |
| Data Analyst | analysis.py; EDA notebooks/reports | customer + behavior + feature examples | executable EDA, plots, insights, KPI definitions, data-quality findings |
| ML Classification | classification.py; features.py with Data Engineer | features, separate labels, target decision | classifier/preprocessing bundle, evaluation report, allowed features and threshold rationale |
| ML Segmentation | segmentation.py | unlabeled features | clusterer/preprocessing bundle, profiles, stability/quality report, persona evidence |
| Leader / MLOps | contracts.py, integration.py, cli.py, api.py, monitoring.py; app, config, CI | all validated artifacts | integration, API/UI, monitoring, deployment instructions and review |

## Task 1 — Data Engineer

Input: official source data once audited; contract v1 and `examples/customers.csv` / `monthly_behavior.csv`. Do not reuse old assignment outputs as project data.

Deliver: profile and monthly tables passing `validate_inputs`; a seeded Python generator, documented joins/cleaning, and a before/after quality report. Extend the data dictionary for every synthetic field. Keep immutable raw sources out of public commits unless deliberately approved and suitable for publication.

Acceptance: `pytest -q tests/test_contracts.py`, `churn data`, `churn features`, then the full checks below. Provide a small generated fixture and exact run command. Changing schema requires leader review before downstream work changes.

## Task 2 — Data Analyst

Input: validated profiles, monthly behavior and snapshot features. Read source artifacts; write reports to a separate output destination.

Deliver: reproducible EDA with distributions, outliers, correlations, behavior and coverage summaries; churn comparisons only once legitimate labels exist. Give each chart a business interpretation and limitation. Document churn rate numerator/denominator/time period, CLV data needs, and retention-cost assumptions. Unsupported KPIs stay unavailable rather than invented.

Acceptance: `churn eda`; summary is JSON-safe, contains sample counts and unavailable KPI statuses; notebook/report runs from a clean environment using documented inputs. Include quality issues for Data Engineer and evidence for both model owners. Add charts and a written report as substantive work; the initial summary stub alone is not a completed EDA.

## Task 3 — Classification owner

Input: features; separate labels and agreed target/split specification for actual training. Interface examples are in `examples/features.csv` and `risk_output.csv`.

Deliver: target definition (unit, observation window, horizon, provenance), reproducible training and validation protocol, model bundle including fitted preprocessing, `predict_risk(features)` output, and evaluation report. Compare dummy/logistic baselines before complexity; report ROC-AUC, precision, recall, F1 and threshold choice. Do not train until target feasibility is resolved. Only training data may fit preprocessing and sampling.

Acceptance: `pytest -q tests/test_contracts.py tests/test_integration.py`; all input customer IDs returned exactly once; scores finite in [0,1]; calibration assessed before calling them probabilities. Coordinate changes to real-bundle persistence/loading with leader. A real estimator and its dependencies need additional tests; current demo manifests are not general model serialization.

## Task 4 — Segmentation owner

Input: unlabeled features, never churn or predicted risk. Interface examples are `examples/segment_output.csv` and `segment_profiles.csv`.

Deliver: reproducible clustering and transform/assignment code, fitted preprocessing in bundle, `assign_segments(features)`, profiles and persona rationale based on feature summaries. Assess silhouette where appropriate, stability and interpretability; do not predetermine the final personas. Analyze churn by segment only after clustering independently.

Acceptance: `pytest -q tests/test_integration.py`; every customer assigned once; every segment ID maps to a profile; profiles document dataset-level counts. Same fitted preprocessing and model support unseen customers at inference time. Coordinate bundle loading with leader.

## Task 5 — Leader / MLOps

Own integration contracts, strict ID joins and CI. Review cross-module changes. Configure branch protection as described in GITHUB_WORKFLOW.md. Ensure API, dashboard and monitor use compatible artifacts. Replace demo loaders with versioned real loaders only when both owners supply validated bundles. Never unpickle untrusted artifacts.

Deliver: working API/UI, deployment documentation and live-link task, frozen training reference and incoming batch monitoring, delayed-label performance workflow, retraining criteria and final integration checklist. Cloud publication remains a later phase; this repository provides a local runnable service and app.

Acceptance: `pytest -q`, `ruff check src app tests`, `churn demo`; start API and Streamlit from README. Test API outage in dashboard; validate artifacts fail startup when missing or incompatible.

## Definition of done for every handoff

1. PR names owner, contract version, exact commands and produced files.
2. Code imports through the package; no hardcoded user paths, notebook-only functions or manual cell-order dependencies.
3. Examples and docs match actual input/output; new contract behavior has meaningful tests.
4. Full CI and demo pass. Generated artifacts, private data and virtualenvs are absent from the diff.
5. Leader reviews shared-interface changes; teammate can reproduce the handoff from README.
6. Limitations distinguish observed, simulated and assumed information.

## Recommended handoff order

Agree target/source feasibility and schema first. Data Engineer and Analyst refine data/EDA while both model owners develop against fixtures. Accept validated data before training; accept independently evaluated model bundles before deployment. Business understanding and final interpretation remain shared responsibilities.
