# Demo fixture dictionary and assumptions

These distributions are plumbing fixtures, not estimates of actual digital-bank behavior. Seed 42; 24 fictional customers by default. Generator: `numpy.random.default_rng`; generated results are reproducible within the installed environment. Units use an unspecified demo currency. No real customer records, churn outcomes or campaign outcomes are included.

## Customer profiles

| Column | Type | Unit | Valid range | Fixture generation / assumption |
| --- | --- | --- | --- | --- |
| customer_id | string | identifier | nonempty, no whitespace, unique | DEMO-0000 onward; never model input |
| age | integer | years | 18–100 | discrete uniform 18–75 |
| balance | float | currency | finite, >=0 | uniform [0,100000), rounded to two decimals; snapshot at observation date |
| country | string | category | France/Germany/Spain | equal-probability sample |

## Monthly behavior

Exactly three rows per demo customer: January–March 2026. Counts use nonnegative integers. Customer IDs must reference the profiles table.

| Column | Type | Unit | Valid range | Fixture generation / assumption |
| --- | --- | --- | --- | --- |
| customer_id | string | identifier | existing profile ID | profile foreign key |
| month | string | calendar month | YYYY-MM with month 01–12 | fixed 2026-01, 2026-02, 2026-03 |
| transaction_count | integer | transactions/month | >=0 | uniform integers 0–49 |
| transaction_amount | float | currency/month | finite, >=0 | transaction_count × uniform [10,100), rounded to two decimals |
| login_count | integer | logins/month | >=0 | uniform integers 0–59 |
| complaint_count | integer | complaints/month | >=0 | uniform integers 0–2 |
| mobile_count | integer | mobile transactions/month | >=0 | multinomial channel allocation, probability 0.7 |
| atm_count | integer | ATM transactions/month | >=0 | same multinomial allocation, probability 0.2 |
| branch_count | integer | branch transactions/month | >=0 | same multinomial allocation, probability 0.1 |

Channel counts sum exactly to transaction_count. Channels describe transactions, not logins. No churn-dependent generation mechanism exists in this fixture. No realism claim is attached to independence or distribution choices.

## Derived feature fields

All features are one row per customer for the configured observation window. ID, age and balance come from profiles; customer country is excluded in v1.

| Column | Type | Unit | Valid range | Derivation |
| --- | --- | --- | --- | --- |
| transaction_count | integer | transactions/window | >=0 | sum of included months |
| transaction_amount | float | currency/window | finite, >=0 | sum of included months |
| login_count | integer | logins/window | >=0 | sum of included months |
| complaint_count | integer | complaints/window | >=0 | sum of included months |
| mobile_share | float | proportion | [0,1] | summed mobile_count / transaction_count; 0 if no transactions |

## Outputs and labels

- `risk_score`: finite float [0,1], demo rule `clip(0.2 + 0.08*complaint_count - 0.001*login_count, 0, 1)`; not calibrated probability.
- `segment_id`: nonempty string; demo-1 if login_count >=80, else demo-0. These are rules, not fitted clusters or business personas.
- `segment_name`, `description`: nonempty display strings explicitly marked demo; `customer_count`: nonnegative integer count in profiling dataset.
- `churn`: integer 0/1 in a **separate** label table; no labels are generated for the demo. Meaning and future-quarter provenance remain unresolved.

The Data Engineer replaces this fixture specification with defensible distributions, dependencies and validation evidence before real synthetic generation. Any additional field requires the same name/type/unit/range/logic documentation.
