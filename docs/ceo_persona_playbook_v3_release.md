# CEO persona playbook V3 release

**Release:** seed `20261026`, 10.000 customers, six simulated months. Every behavioural statement below is `SYNTHETIC_BEHAVIOR`; churn, age, credit score, country, gender, tenure, balance, products and active-member flag are `OBSERVED_STATIC_DATA`.

## What the portfolio says

The analysis separates 5.285 customers who use digital banking regularly from 4.715 whose digital relationship is thin. The lower-digital group has a historical static churn rate of **27,3%**; the higher-digital group is **14,2%**. This 13,1-point gap prioritises recovery work, but does not prove that app use causes churn.

![Cluster map](../reports/segmentation/v3/v3_cluster_map.png)

## Persona A: Digital relationship builders

**Who they are.** 5.285 customers, average age 39,6, average credit score 653,2, average tenure and product depth stable at roughly 1,5 products. Gender, country, salary estimate and balance must never determine treatment; they are retained for aggregate fairness review only.

**What they do.** In the six-month simulation they are the group with regular app activity, repeated incoming-flow months and more payments. `transfers_and_bill_pay` is their primary simulated app task in 26.472 customer-months; `balance_and_card_controls` appears in 4.308 customer-months. The recurring pattern is use of the app to move money and complete routine payments, not evidence of loyalty or satisfaction.

**What is at stake.** Their churn rate is lower, but 751 customers still carry a churn label. The risk is silent erosion: a friction in a routine transfer or bill flow can affect a large base before complaints appear.

**Big idea: make routine banking invisible.**

- **Arm A, Digital concierge:** show one contextual shortcut when a customer begins a transfer/bill task; route failures straight to support.
- **Arm B, Value review:** explain current fees, benefits and product settings; the customer chooses whether to continue. No default cross-sell.
- **Test question:** Does removing task friction retain more customers than clarifying the current relationship?
- **SMART target:** after 90 days, choose an arm only if the lower bound of its 95% retention-effect CI is above zero, its opt-out/complaint rate is no worse than the alternative, and Finance approves cost per retained customer.

**Operating policy.** Product owns task completion; CRM owns consent and contact caps; Care receives failed-task escalations; Compliance can halt the journey for any consent breach. CEO sees weekly completion, repeated support contact, opt-out and incident counts.

## Persona B: Thin digital relationship, recovery first

**Who they are.** 4.715 customers, average age 38,2, average credit score 647,5, and similar product depth, salary estimate and balance to Persona A. The key distinction is not wealth. It is relationship activity.

**What they do.** Their simulated app pattern is overwhelmingly `account_status_check`: 28.134 customer-months. They rarely reach transfer/bill-payment features. Their lower app activity, irregular incoming flow, higher failed-payment count and higher unresolved-service-case share create a practical signal that the relationship needs attention.

**Timing.** Transaction dates in this synthetic release are roughly uniform around day 14–15 for all transaction types. There is no defensible “payday” or day-of-month insight. The bank should instrument actual timestamps before using timing in outreach.

**What is at stake.** 1.286 customers have a historical churn label. If service issues are treated as sales opportunities, the bank can increase distrust and complaint volume.

**Big idea: recover trust before asking for another action.**

- **Arm A, Service recovery:** identify open/reopened case, assign a named owner, meet SLA, confirm closure, then suppress promotion for a cooling period.
- **Arm B, Reactivation coach:** for customers without an open case, offer a 14-day guided return to one useful task, with one reminder and no cash incentive.
- **Test question:** Is relationship repair more effective than guided reactivation for restoring active use and 90-day retention?
- **SMART target:** within 90 days, the winning arm must have a positive lower 95% CI for active-month/retention effect, no consent breach, and no deterioration in complaint, repeat-contact or failed-payment guardrails.

**Operating policy.** An unresolved case overrides marketing eligibility. Care owns closure and re-open rate; CRM owns randomisation and contact frequency; Digital Product owns journey completion; Analytics declares the result; CFO signs off on scale.

## Decision gates

The two planned pilots need 4.360 and 4.920 customers **per arm** to detect 3-point and 2-point effects at 80% power. Current eligible cells do not meet that requirement. CEO must not launch until the team chooses a larger MDE, longer follow-up, or a wider cohort.

## Evidence and limits

[Manifest](../reports/segmentation/v3/manifest.json) · [churn cross-tab](../reports/segmentation/v3/segment_churn.csv) · [feature separation](../reports/segmentation/v3/distinctiveness.csv) · [pilot protocol](../reports/segmentation/v3/pilot_protocol_v3.csv). This is a decision rehearsal with synthetic behaviour, not a claim about a real bank's customers.
