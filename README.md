# Digital Bank Customer Churn — Team Backbone

A runnable integration scaffold for a five-person Business Analytics capstone. All supplied data, risk scores and segments are **demo fixtures**. No real model has been trained, and no next-quarter predictive performance is claimed. No previous assignment data is used.

Start with [Team assignments](docs/backbone/TEAM_ASSIGNMENTS.md) and [I/O contracts](docs/backbone/CONTRACTS.md). The leader owns integration; members replace their module implementations while keeping contracts stable.

## Setup

Use Python 3.11 (CI also checks 3.12). From the repository root:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
churn demo
pytest -q
ruff check src app tests
```

Windows PowerShell: create with `py -3.11 -m venv .venv`, activate with `.venv\Scripts\Activate.ps1`; remaining commands are the same. If 3.11 is unavailable, Python 3.12 is supported. Avoid reusing another project's virtualenv.

## Run the application

Generate artifacts with `churn demo`, then keep these commands running in two terminals with the virtualenv activated:

```bash
uvicorn churn_capstone.api:app --host 127.0.0.1 --port 8000
```

```bash
streamlit run app/streamlit_app.py
```

API docs: http://127.0.0.1:8000/docs. Dashboard: http://localhost:8501. The dashboard calls the API when a customer is looked up. `CHURN_API_URL` configures its API URL; `CHURN_ARTIFACT_DIR` configures the artifact folder for both processes. Restart the API after changing artifacts.

Try the API using [the checked-in request](examples/predict_request.json):

```bash
curl -X POST http://127.0.0.1:8000/predict -H 'Content-Type: application/json' --data-binary @examples/predict_request.json
```

## Independent workstreams

```bash
churn data
churn features
churn eda
churn classifier
churn segmentation
churn predict
churn monitor
```

Stages read and write `artifacts/demo/` by default. `churn demo` runs all stages in dependency order. `--output` chooses a separate directory and `--config` selects a config file. Running a stage with missing dependencies fails visibly. Classifier and segmentation stages are scaffold builders, not training commands.

The current monitor compares the fixture with its own snapshot, so initial drift is zero. Real incoming batches must use a **frozen training reference**, rather than regenerating the reference every time. See [Monitoring](docs/backbone/MONITORING.md).

## Structure and handoff

- `src/churn_capstone/`: contracts, role modules, integration, CLI and API.
- `app/`: Streamlit interface.
- `examples/`: versioned miniature I/O fixtures, safe to commit.
- `configs/`: explicit demo settings.
- `tests/`: contracts, model substitution, temporal boundaries, API and monitoring checks.
- `docs/backbone/`: assignments, dictionary, decisions and collaboration instructions.
- `.github/`: CI, ownership, pull request and task templates.

Generated artifacts, virtualenvs, secrets and raw datasets are ignored. Never use notebooks as the only integration interface. Model owners supply importable Python implementations and preprocessing artifacts.

## Team workflow

Create a branch per task, run checks, and open a pull request. Do not merge a changed shared contract without coordinating all affected owners. [GitHub setup](docs/backbone/GITHUB_WORKFLOW.md) explains branch protection: CODEOWNERS and CI files alone do not enforce merge restrictions.

The instructor's next-quarter target, official source mapping and synthetic generation assumptions still require team decisions documented in [Open decisions](docs/backbone/DECISIONS.md). Course rules require student-authored code: use this AI-generated scaffold transparently as permitted, and have each owner understand and author their substantive work.
