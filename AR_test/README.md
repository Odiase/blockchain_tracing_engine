# AlphaTrace — Blockchain Investigation Platform

AlphaTrace is a Django-based prototype for investigating suspected cryptocurrency fund flows. It currently focuses on **USDT (ERC-20) transfers on Ethereum Mainnet**. Investigators provide the victim wallet, target wallet, relevant transaction hash, and a date range. The application retrieves transfer data from Etherscan, builds wallet/transaction relationships in Neo4j, and evaluates transaction behavior with fraud-risk heuristics. The web workflow is designed to submit investigations as background Celery tasks.

> **Scope:** Other networks appear in the chain constants, but the current user interface and tracing configuration target Ethereum Mainnet and USDT. Do not treat this prototype's heuristic output as proof of fraud or as financial/legal advice.

## Features

- Web workflow for submitting and viewing an investigation.
- Etherscan API v2 integration for ERC-20 transfer data.
- Neo4j graph storage for wallet and transfer relationships.
- Heuristic analysis that includes rapid fund movement, balance dominance, and exchange interactions.
- Celery integration with Redis as the configured broker and result backend.
- SQLite configured as Django's default database.

## Technology

- Python and Django
- Celery and Redis
- Neo4j
- Etherscan API and Web3.py
- HTML, CSS/SCSS, and JavaScript

## Repository layout

```text
.
├── requirements.txt
├── blockchain_tracing_engine/
│   ├── manage.py
│   ├── .env                 # local secrets/configuration; do not commit
│   ├── blockchain_tracing_engine/  # Django settings and Celery app
│   ├── core/                # tracing, views, graph access, heuristics, tests
│   ├── templates/           # Django templates
│   └── static/              # application CSS and JavaScript
├── frontend/                # additional frontend styles/templates
└── *.usdz / *.glb           # 3D assets in the workspace
```

The main Django application is in the nested `blockchain_tracing_engine/` directory. Run Django and Celery commands from there.

## Requirements

- Python version compatible with the pinned packages in `requirements.txt` (Django 6 requires a supported recent Python release).
- Redis running locally at `127.0.0.1:6379` (the current Celery settings use this address).
- A reachable Neo4j database.
- An Etherscan API key.

## Local setup (Windows PowerShell)

From the repository root:

1. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. Install project dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create or update `blockchain_tracing_engine/.env` with the configuration described below. Keep this file private and out of version control.

4. Start Redis and Neo4j, and ensure the database/user in the environment settings exist.

5. Run Django migrations and start the web server:

   ```powershell
   cd blockchain_tracing_engine
   python manage.py migrate
   python manage.py runserver
   ```

6. In a **second** PowerShell terminal, activate the same virtual environment, change to the Django project directory, and start a Celery worker:

   ```powershell
   cd blockchain_tracing_engine
   ..\.venv\Scripts\Activate.ps1
   celery -A blockchain_tracing_engine worker --loglevel=info --pool=solo
   ```

   The `solo` pool is a practical option for local Windows development. For deployment, use an appropriate supported worker platform and production configuration.

7. Open `http://127.0.0.1:8000/` in your browser.

## Environment configuration

The tracing and graph modules load variables from `blockchain_tracing_engine/.env`:

| Variable | Purpose | Required |
| --- | --- | --- |
| `ETHERSCAN_API_KEY` | Etherscan API v2 access for transfer history | Yes |
| `NEO4J_URI` | Neo4j connection URI, such as `neo4j://127.0.0.1:7687` | Yes |
| `NEO4J_USER` | Neo4j username | Yes |
| `NEO4J_PASSWORD` | Neo4j password | Yes |
| `NEO4J_DB_NAME` | Neo4j database name; defaults to `alphadb` when unset | Optional |

Use your own credentials and do not put real keys or passwords in documentation, source control, or issue reports. The current workspace has a local `.env` file; if its credentials have been shared or committed, revoke/rotate them and remove the file from source control.

## Using the application

1. Open the landing page and select **Start Investigation**.
2. Enter the victim wallet address, target wallet address, victim transaction hash, and investigation date range.
3. Submit the form. The investigation is intended to be queued through Celery; see [Current limitations](#current-limitations) for the worker autodiscovery configuration requirement.
4. View task progress/status and the resulting analysis in the investigation pages. The graph explorer page is also available from the application UI.

Current tracing constants select Ethereum Mainnet and the USDT ERC-20 contract. Confirm that the entered transaction belongs to the supported asset and network.

## Tests

Tests are located under `blockchain_tracing_engine/core/core_tests/`. From the Django project directory, run:

```powershell
pytest
```

The existing tests should be reviewed against the current `ChainTrace` API before relying on them; some test imports may reflect an earlier implementation. Django's test runner is also available:

```powershell
python manage.py test
```

## Security and production notes

- The checked-in Django settings currently use `DEBUG = True`, an insecure development `SECRET_KEY`, and an empty `ALLOWED_HOSTS`. Replace these before deployment; use environment-based secrets and Django's deployment checklist.
- Keep API keys, Neo4j credentials, and production secrets out of Git. Rotate credentials if they were ever exposed.
- Use HTTPS, restrict allowed hosts, configure secure cookies, and review access control before exposing this application publicly.
- Validate and rate-limit external API access, and plan for Etherscan failures, rate limits, and incomplete transaction history.
- Risk heuristics are investigative signals, not definitive classifications.

## Current limitations

- The implemented tracing flow is configured for Ethereum Mainnet USDT rather than arbitrary chains/tokens.
- Neo4j, Redis, and the Etherscan API must be available for a complete live investigation.
- The `core` app is not currently listed in Django's `INSTALLED_APPS`, while Celery task autodiscovery scans installed apps. Register the app before relying on worker autodiscovery for the investigation task.
- The repository contains additional frontend assets and 3D model files; these are not required for the Django tracing workflow.
