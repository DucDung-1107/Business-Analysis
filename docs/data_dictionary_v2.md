# Data dictionary - synthetic behavioural and persona extension V2

V2 extends the immutable static Kaggle base in `data/processed/kaggle_churn_v1/`. It is generated with the fixed seed and parameters in `configs/segmentation_v2.json`. It exists for an academic segmentation and experiment-design demonstration. It is not observed banking history, a customer survey, or a record of churn reasons.

| Field | Source | Type | Unit / valid values | Generation logic | Time availability | Validation rule |
| --- | --- | --- | --- | --- | --- | --- |
| customer_id | V1 Kaggle base | string | existing unique ID | carried from V1 | static | exactly one matching V1 customer |
| period_index | synthetic behaviour V2 | integer | 1..configured periods | simulated period counter | simulated, not calendar time | each customer has every period once |
| transaction_count | synthetic behaviour V2 | integer | >=0 | Poisson rate from active-member, product count, age, salary, credit and seeded noise | simulated | non-negative |
| transaction_amount | synthetic behaviour V2 | float | >=0, source currency unknown | transaction count x simulated ticket value | simulated | non-negative |
| inbound_deposit_amount | synthetic behaviour V2 | float | >=0, source currency unknown | seeded monthly incoming-flow scenario driven by active-member flag and salary estimate; not verified salary payment | simulated | non-negative |
| card_spend_amount / bill_payment_amount / cash_withdrawal_amount | synthetic behaviour V2 | float | >=0, source currency unknown | seeded allocation of simulated transaction amount | simulated | non-negative |
| loan_repayment_amount | synthetic behaviour V2 | float | >=0, source currency unknown | synthetic repayment scenario for selected higher-product-count customers; not observed loan ownership | simulated | non-negative |
| failed_payment_count | synthetic behaviour V2 | integer | >=0 | Poisson scenario from latent service-friction term | simulated | non-negative |
| app_active_days | synthetic behaviour V2 | integer | 0..31 | seeded transformation of simulated logins | simulated | integer in range |
| salary_payment_day | synthetic behaviour V2 | integer | 0 or 1..28 | seeded day-of-month for a simulated incoming-flow event | simulated | integer in range |
| service_case_opened / service_case_resolved | synthetic behaviour V2 | integer | >=0; resolved <= opened | complaint-derived simulated case lifecycle | simulated | resolved <= opened |
| login_count | synthetic behaviour V2 | integer | >=0 | Poisson rate from latent seeded engagement | simulated | non-negative |
| complaint_count | synthetic behaviour V2 | integer | >=0 | Poisson rate from latent seeded service-friction term | simulated | non-negative |
| mobile_count / atm_count / branch_count | synthetic behaviour V2 | integer | >=0 | seeded channel allocation conditional on simulated transaction count | simulated | channel sum equals transaction_count |
| RFM fields | derived synthetic V2 | numeric | see `docs/segmentation_v2_methodology.md` | aggregation of the simulated period rows | simulated | one finite row/customer |
| simulated_pain_signal | synthetic persona scenario V2 | category | service-contact, low-activity, digital self-service, or no-signal | deterministic scenario assignment from simulated RFM quantiles and simulated complaints; no churn input | simulated | non-null declared category |
| simulated_need_to_test | synthetic persona scenario V2 | string | journey-design statement | paired with the simulated pain signal | simulated | non-null; not an observed preference |
| simulated_primary_journey | synthetic persona scenario V2 | category | service recovery, reactivation, digital self-service, value review | paired with the simulated pain signal | simulated | non-null declared category |
| source_type | pipeline metadata | string | `synthetic_behavior` or `synthetic_persona_scenario` | assigned by generator | all rows | exact declared value |

## Critical limitations

- The scenario fields are useful for creating distinct A/B-test treatments. They do not verify a customer's pain point, desired product, reason for churn, or likely response.
- `churn` is never passed into behaviour or persona-scenario generation and is absent from all V2 augmentation tables. It is joined after segmentation only for descriptive static-label cross-tabs.
- The source has no real observation/prediction/label windows. V2 cannot support a next-quarter churn claim.
