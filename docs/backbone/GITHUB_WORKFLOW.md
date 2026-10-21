# GitHub workflow and enforcement

## Member workflow

```bash
git switch main
git pull --ff-only
git switch -c feat/your-role-task
# implement inside your owned module(s)
ruff check src app tests
pytest -q
churn demo
git add <specific-files>
git commit -m "Describe the behavior change"
git push -u origin feat/your-role-task
```

Open a PR against main, fill the template, and attach artifact schemas/commands rather than private datasets. Resolve review comments and CI failures before merging. Avoid concurrent edits to the same notebook; use small focused PRs. The leader coordinates interface migrations.

## Repository administrator setup

CODEOWNERS identifies reviewers but **does not enforce protection** by itself. After CI has run, configure Settings → Rules → Rulesets (or branch protection) for `main`:

- Require a pull request and at least one approving review.
- Require Code Owner review; dismiss stale approvals when new commits arrive.
- Require status checks matching both matrix jobs: `contracts-and-integration (3.11)` and `contracts-and-integration (3.12)`; select the exact emitted names in GitHub.
- Require conversations resolved; block force pushes and branch deletion.
- Apply to administrators where the account/plan supports it.

Until actual teammate handles are known, @Nituv05 owns all files. Add teammate ownership patterns for their modules; keep the leader as co-owner for shared contracts, config, integration and CI. A PR author cannot approve their own PR: the leader's PR needs another authorized reviewer if approval rules are enabled. Availability/enforcement may depend on repository visibility and account plan; inspect the repository UI.

This scaffold does not enable server-side repository settings automatically. CI catches tested integration failures; review and protection are still needed to control changes to CI/tests themselves.
