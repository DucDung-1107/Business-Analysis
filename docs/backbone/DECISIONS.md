# Decisions and unresolved work

## Backbone defaults (agreed implementation)

- New GitHub repository backbone at root; old assignment data/results are not imported.
- English code and documentation. Five official roles; @Nituv05 is leader/MLOps.
- Python 3.11 standard, also test 3.12. FastAPI + Streamlit; pandas dataframes at Python seams.
- Demo-only seeded fixtures and rule implementations. Strict contract 1.0 and JSON manifests; no untrusted pickled artifacts.
- One snapshot per customer. Monthly behavior includes only completed months before the observation month. Labels are separate.
- All model outputs align by unique customer ID; each segment must have a profile.
- Numeric dependencies use bounded ranges; CI checks supported Python versions. A fully pinned reproducibility lock should be generated when the substantive modeling stack is agreed.

## Open decisions blocking substantive modeling

| Decision | Owners | Evidence / required action |
| --- | --- | --- |
| Can official data support next-quarter churn? | Classification + all members | Audit timestamps/labels; define unit, horizon and provenance; seek instructor clarification if only static labels exist |
| What is the real synthetic generation design? | Data Engineer + model owners | Define realistic distributions/dependencies and document any label relationship explicitly |
| Which features and personas are supported? | Analyst + model owners | EDA, leakage audit, stability and interpretation evidence |
| CLV and retention costs | Analyst + all members | Establish data needs; use labeled scenarios when actual inputs unavailable |
| Actual teammate handles and branch settings | Leader | Assign people; update ownership and enable GitHub rules |
| Real artifacts and deployment | Leader + model owners | Agree preprocessing/model persistence; choose hosting after compatibility checks |
| Performance monitoring limits | Leader + Classification | Outcome delay, sufficient sample sizes, baseline guardrails and intervention assumptions |

No scores, model accuracy, churn rates, retention effects or ROI from the demo should appear as measured business findings. The project announcement remains the source of requirements; verify against the actual document before substantive implementation.
