# Segmentation V2 upgrade plan

## Decision and scope

**Module:** segmentation, synthetic behavioural extension and business decision support.

**Business question:** Which *simulated behavioural* patterns are operationally distinguishable, what observed-static churn cross-tab accompanies them, and which experiment should test a distinct retention journey?

The assignment PDF itself is not present in this workspace. The user-provided assignment excerpt confirms the required Kaggle base plus Python-generated transaction/behavioural data. This implementation uses that evidence and records the missing full-PDF review as a documentation dependency.

## Change plan

1. Expand the synthetic observation window from three to six monthly periods.
2. Materialise separate, versioned monthly transaction, digital-usage and service-case tables, with explicit keys and source tags.
3. Derive RFM, trend, digital-engagement, channel-affinity and service-friction features at one customer/cutoff grain. Do not use `churn`, cluster ID or model score in their construction.
4. Retain a behaviour-only clustering input; demographic fields are only aggregated for persona context and fairness checks.
5. Compare clustering methods, document stability and generate detailed persona, lens and A/B-test outputs.
6. Add schema, cardinality, deterministic-seed and no-label-leakage tests; regenerate V2 artifacts and record actual command evidence.

## Acceptance checks

- Six simulated months per customer and exactly one feature row per customer.
- Transactions, digital months and service cases join only to known customer IDs and satisfy their grain rules.
- No generated primary behavioural field has access to `churn`.
- RFM/trend feature values are finite and have documented units, cut-off and source tag.
- At least K-Means, Gaussian Mixture and Ward hierarchical candidates are compared; diagnostics do not get presented as commercial validation.
- Persona cards state which fields are observed static versus synthetic behaviour/scenario.
