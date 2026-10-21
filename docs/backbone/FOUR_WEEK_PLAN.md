# Four-week delivery plan and team assignments

## Objective and working assumptions

Deliver the eight modules in Business_Analytics_Project_Announcement.pdf: an evidence-based business problem, required Kaggle base plus documented Python-generated behavior, EDA, cleaning, features, classification, clustering, deployed API/Streamlit, monitoring, and final PDF/PPTX deliverables.

Week 1 starts on the team's agreed kick-off date. Use relative days below; these are internal deadlines, not instructor submission dates. This is a compressed four-week project, not the earlier three-week foundation roadmap. Each member needs a daily work block; report capacity constraints at kick-off and reduce tuning/UI scope first. Course authorship rules still apply to substantive work and use of the scaffold.

Roles: DE = Data Engineer; DA = Data Analyst; CL = Classification Engineer; SG = Segmentation Engineer; ML = Leader/MLOps (@Nituv05). Replace role abbreviations with actual member names when assigning tasks. Business understanding belongs to everyone; DA consolidates the written business/report narrative, ML coordinates integration and submission, and each owner writes their own methods/results.

The current demo is not the actual data/model pipeline. Early Week 1 tasks below add missing backbone boundaries before model owners implement real components. Existing contract 1.0 remains the demo reference until a coordinated revision is accepted.

## Milestones and evidence

| Week | Outcome | Required milestone evidence |
| --- | --- | --- |
| 1 | Agreed business/target, real data route and stable handoff boundaries | source audit, target/KPI decisions, cleaning/generation pipeline, dictionary, initial EDA, revised contracts, cloud smoke link |
| 2 | Reproducible analysis and evaluated model baselines | completed EDA/cleaning evidence, frozen splits, classifier comparison, clustering profiles, two reloadable model bundles |
| 3 | Working integrated hosted application and monitoring | live API/UI links, risk-by-segment analysis, retention matrix, incoming-batch drift report and delayed-label performance path |
| 4 | Verified final submission and rehearsed presentation | clean-clone run, final models/reports, monitoring notebook/report, final report PDF, slides PPTX/PDF, live link and recorded backup |

## Week 1 — Business, data and interface freeze

Purpose: everyone knows what they are producing and which dataset/target their work relies on. Do not spend this week tuning models or designing polished slides.

| Task | Owner | Inputs | Required outputs | Due / handoff |
| --- | --- | --- | --- | --- |
| W1-DE | DE | official Kaggle source and synthetic field needs | new source audit and checksum record; raw-to-clean adapter; seeded synthetic behavior generator joined to source customer IDs; dictionary and assumptions; quality counts before/after cleaning | D2 schema draft to CL/SG/DA; D5 runnable data PR |
| W1-DA | DA | announcement, source audit, draft validated tables | business problem/stakeholder/decision scope; KPI formulas/time periods and feasibility; initial data audit and 3–5 preliminary figures with interpretations | D3 business/KPI draft; D5 audit to DE and model owners |
| W1-CL | CL | source labels, timestamps, draft features | target feasibility note; observation/horizon/provenance and allowed-feature list; train/validation/test specification; signatures for training, evaluation and reloadable classifier bundle | D2 target issue raised; D3 target proposal; D5 feature/training contract |
| W1-SG | SG | profile/behavior schema, segmentation objective | behavioral feature proposal including feasible RFM-style/trend signals; cluster evaluation plan; inference assignment and profile output examples | D3 proposal to DE/CL; D5 segmentation contract |
| W1-ML | ML | audit findings, all proposed interfaces | separate import/clean/generate/features/train/evaluate boundaries; separate label/split and branch-specific feature specifications; real bundle manifest/loading contract; fixed reference/incoming batch paths; updated examples/tests; hosting smoke test with demo artifacts | D3 interface proposal; D5 coordinated contract PR and demo cloud smoke link |

Daily sequence:

1. D1: 45-minute kick-off; read the announcement, assign names and GitHub ownership, confirm deadlines and capacity; each owner opens a branch and runs the demo.
2. D2: DE publishes source schema/provenance; CL reports whether next-quarter labels are genuinely supported. If not, ML coordinates an instructor clarification immediately. SG/DA specify required columns before generator design is fixed.
3. D3: jointly review target proposal, feature availability and split approach. Approve interface shapes, source-to-clean rules and synthetic design. Record unresolved instructor decisions explicitly.
4. D4–D5: implement boundary revisions and new data pipeline; demonstrate a clean import/generate/clean/features run and initial hosted demo. A smoke deployment reduces hosting uncertainty; it is not the final deployed model.
5. D6: cross-review, regenerate data from configuration, inspect joins/quality and fix integration failures.
6. D7: milestone review and updated Week 2 assignments; version the agreed schema/config and dictionary.

Week 1 gate:

- [ ] Required Kaggle source is explicitly recorded; synthetic behavior extends source customers rather than replacing them with fictional profiles.
- [ ] Raw data stays unchanged; cleaning has documented before/after evidence, not just validation that rejects bad rows.
- [ ] Every synthetic field has name, type, unit, valid range and generation logic; label-dependent generation, if proposed, is explicit and reviewed.
- [ ] Labels and prediction timing are defined or visibly blocked pending instructor clarification. No unsupported future-quarter claim is made.
- [ ] Source tables, features, split manifest, label table, model bundles and incoming monitoring batches have reviewed handoff specifications/examples.
- [ ] All five members can run the shared fixture pipeline, CI passes, and actual dataset handoff has no unknown IDs or duplicate keys.

If the target decision remains unresolved, continue descriptive EDA, source cleaning, unlabeled clustering and deployment. Classification training and future-quarter claims stay gated. A static-label proxy or simulated target requires explicit documented instructor acceptance; silence is not approval.

## Week 2 — Complete analysis and train evaluated baselines

| Task | Owner | Inputs | Required outputs | Due / handoff |
| --- | --- | --- | --- | --- |
| W2-DE | DE | Week 1 data contract and quality feedback | reproducible integrated dataset, complete cleaning evidence/dictionary, realistic synthetic validation, schema/ID/window tests, versioned data manifest | D2 data release to DA/CL/SG; D5 corrections only |
| W2-DA | DA | versioned data and permitted labels | completed EDA notebook/report and figures: distributions, missingness, outliers, correlations, age/product/balance churn comparisons where available, behavior/coverage summaries; distinguish association from causation | D3 findings to model owners; D5 reproducible report |
| W2-CL | CL | approved target, released features/labels and split manifest | Dummy + Logistic Regression baselines, Random Forest/XGBoost comparisons with bounded tuning; validation ROC-AUC, precision, recall, F1 and confusion matrix; threshold rationale; reloadable classifier/preprocessing bundle with feature/version metadata | D2 split manifest; D3 first LR bundle; D5 comparison and selected candidate |
| W2-SG | SG | released unlabeled features, clustering specification | K-Means baseline across a small feasible k range; silhouette where valid, repeated-seed stability and profile summaries; interpretable evidence-based names; reloadable preprocessing/clusterer supporting unseen customers | D3 first bundle; D5 selected segmentation and profiles |
| W2-ML | ML | real bundle contracts and first bundles | compatible loaders and API inference for real artifacts; dashboard lookup on new integrated data; CI runs independent branch tests plus integration; reproducible environment versions captured for release | D3 integration with first bundles; D5 both real branches working locally |

Rules: freeze split IDs and data version before comparison. Fit encoders/scalers/imputation/resampling only on training folds. Use validation results for selection/thresholds; reserve the final test for the locked pipeline. Use temporal splits if genuine observations/labels support them; an approved static proxy uses an explicitly justified customer-level split. Repeated customer snapshots require grouping/time rules to prevent contamination.

Week 2 gate:

- [ ] Completed EDA and cleaning artifacts, not placeholders, regenerate from documented inputs.
- [ ] Prediction and clustering inference exclude labels and customer ID as predictive inputs; clustering also excludes risk scores.
- [ ] Classifier comparison uses the same evaluation protocol; imbalance treatment and feature selection are documented, including justified decisions not to apply a method.
- [ ] Segment names follow actual profiles; assignments are stable enough to explain and usable on new customers.
- [ ] Both fitted model/preprocessing bundles reload in a fresh process and produce contract-valid outputs for a held-out sample.
- [ ] API and dashboard use actual model bundles locally. No need to wait until Week 3 to discover loader incompatibility.

## Week 3 — Integration, business decisions and monitoring

| Task | Owner | Inputs | Required outputs | Due / handoff |
| --- | --- | --- | --- | --- |
| W3-DE | DE | fixed training reference and incoming schema | reproducible separate unchanged, shifted and invalid incoming batches; label-arrival fixture with explicit provenance; no reference overwrite | D2 monitoring fixtures to ML |
| W3-DA | DA | cluster profiles, legitimate outcomes/risk and approved cost assumptions | churn/risk-by-segment tables with denominators; retention action matrix linking segment/evidence/action/priority/cost assumption; report draft; scenario economics only if assumptions are explicit | D3 matrix for team review; D5 report draft |
| W3-CL | CL | validation errors, real inference logs, label fixtures | selected classifier/threshold frozen; error and subgroup review; performance-monitoring inputs and baseline guardrails agreed with ML; limitations/calibration explanation | D2 model freeze; D4 monitoring review |
| W3-SG | SG | selected clustering and real lookup outputs | frozen segmentation bundle, segment profiles with sizes and meaningful feature summaries; unusual/new-customer checks; persona/retention interpretation with DA | D2 model freeze; D4 business interpretation |
| W3-ML | ML | validated model set, fixtures, report requirements | deploy compatible API and Streamlit with live links; monitoring notebook or Evidently report with separate frozen reference, drift, performance history and retraining triggers; visible monitoring UI; version/rollback instructions | D3 live real-model app; D5 monitoring and end-to-end review |

Week 3 gate:

- [ ] Another team member can open the live app and complete a bank-staff customer lookup without a local development environment.
- [ ] API and UI show matching model versions and use the same feature contract; no demo rule is presented as the real selected model.
- [ ] Monitoring detects shifted data, accepts stable data, reports invalid input and shows waiting status before labels arrive.
- [ ] A labeled fixture demonstrates the performance path and multiple batch results/history; simulated outcomes are clearly identified and never treated as real model performance.
- [ ] Drift/performance investigation and retraining conditions are written and demonstrated; numeric guardrails and minimum sample sizes are recorded from the reviewed baseline by D4.
- [ ] Monitoring deliverable includes the required notebook or Evidently report; JSON alone is insufficient for the stated deliverable format.
- [ ] Retention actions are recommendations, with evidence and assumptions separated. No unsupported causal churn reduction/ROI claim.

## Week 4 — Freeze, verify and submit

| Task | Owner | Inputs | Required outputs | Due / handoff |
| --- | --- | --- | --- | --- |
| W4-DE | DE | frozen pipeline and data manifests | final data dictionary, generation/cleaning methodology and quality evidence; verify reproduction from raw source | D2 final section to DA |
| W4-DA | DA | each owner's methods/results plus figures | consolidate final report PDF and slide narrative; check every number against saved results; final retention recommendations and limitations | D3 report/slides draft; D5 final exports |
| W4-CL | CL | locked selected pipeline and held-out test | one final held-out evaluation; final model card, comparison table, errors, target/label limitations; explain selected threshold | D2 results to DA; fix only documented defects afterward |
| W4-SG | SG | frozen segmentation and profiles | final profile/persona figures, quality/stability evidence, assignment explanation and business interpretation | D2 results to DA |
| W4-ML | ML | all frozen deliverables, live services | clean-clone setup/run validation, final deployment smoke test, monitoring report, release commit/tag and submission checklist; record demo backup; final links/access check | D3 rehearsal build; D5 release candidate |

D1–D2: freeze features/algorithms; finish held-out evaluation and artifact documentation. D3: full rehearsal and report review. D4–D5: fix demonstrated defects, export report PDF and slides PPTX/PDF, record demo. D6: verify final links/environment from another machine. D7: submission buffer. All five members present their own work and can explain business meaning and limitations.

Final acceptance:

- [ ] GitHub source code and exact setup/run instructions.
- [ ] Required base dataset provenance plus reproducible synthetic extension and complete Markdown/Excel dictionary.
- [ ] EDA, quality assessment, cleaning before/after and feature engineering evidence.
- [ ] Classifier evaluation and interpretable clustering, integrated risk/churn-by-segment analysis.
- [ ] Accessible deployed API and dashboard live links.
- [ ] Monitoring notebook/Evidently report, demonstrated drift/performance paths and retraining triggers.
- [ ] Final report PDF and slides PPTX; slide PDF and recorded demo as useful backups.
- [ ] Limitations include label horizon, synthetic realism, unavailable economics and untested interventions.

## Team operating rhythm and PR acceptance

- Daily async update: completed artifact/PR link, next output, blocker and needed owner. Report a blocking dependency the same day; do not wait for the weekly meeting.
- D3 each week: 20-minute integration check. D5: owner PRs ready. D6: leader review and fixes. D7: 45-minute artifact-based milestone demo and next-week commitments.
- One branch/PR per task or coherent subtask. Small reviewed changes to shared contracts; never silently edit another owner's interface.
- Leader reviews within one working day. Assign a backup reviewer so the leader's own PRs receive review.
- Every handoff provides versioned inputs, produced outputs, exact command, assumptions, tests and a short business interpretation. Existing CI/demo checks are necessary, but an actual data/model acceptance run is also required; passing fixture tests alone does not complete a workstream.
- A failed milestone becomes a named recovery task with owner and next-day deadline. Optional tuning/polish stops until the data/interface/integration blocker is fixed.

## If the actual deadline is three weeks

Keep the same requirements; change sequencing and depth, not required deliverables.

| Period | Required outcome |
| --- | --- |
| Week 1 | Complete Week 1 gates; on D4–D7 start full EDA, baseline classification and clustering against the released dataset; deploy demo smoke app |
| Week 2 | Complete analysis and baseline comparisons by D3; freeze models/bundles by D4; complete real API/UI deployment and monitoring integration by D7; draft report continuously |
| Week 3 | First two days finish monitoring and business integration; D3 freeze and final test/report; D4 rehearsal; D5 final exports/recording; D6–D7 verification and submission buffer |

Reduce hyperparameter searches, secondary clustering methods and UI styling. Keep straightforward classifier comparisons and one defensible K-Means solution. Do not remove the required Kaggle/synthetic combination, cleaning documentation, evaluation, real deployment, monitoring or final reports. Target approval and usable data must arrive early in Week 1; otherwise the team must escalate feasibility/scope to the instructor rather than pretend the three-week schedule is guaranteed.
