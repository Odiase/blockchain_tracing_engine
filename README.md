# AlphaTrace — Blockchain Investigation Platform

AlphaTrace is a Django prototype for investigating suspected cryptocurrency fund flows. Its current tracing flow focuses on USDT (ERC-20) transfers on Ethereum Mainnet. It retrieves transfer data from Etherscan, stores wallet/transaction relationships in Neo4j, and evaluates transaction behavior with risk heuristics. Celery and Redis are configured for background investigations.

> Heuristic results are investigative signals, not proof of fraud or financial/legal advice.

## Project layout

- `blockchain_tracing_engine/` — Django project, application code, templates, and static assets.
- `frontend/` — additional frontend templates and styles.
- `AR_test/` — separate 3D/AR experiments and assets.

## Services and configuration

The Django application uses SQLite by default. A complete live tracing workflow also requires Redis, Neo4j, and an Etherscan API key. Configure `ETHERSCAN_API_KEY`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, and optionally `NEO4J_DB_NAME` in a local `.env` file under the Django project directory. Keep `.env` private; it is excluded from Git.

The configured tracing flow targets Ethereum Mainnet USDT. Although other chain identifiers are listed in the code, arbitrary networks/tokens are not currently supported by the investigation workflow.

## Run locally

From the repository root, install the Django application's Python dependencies in your environment, then run:

```powershell
cd blockchain_tracing_engine
python manage.py migrate
python manage.py runserver
```

Start Redis and Neo4j separately. In another terminal, run a Celery worker from the same directory:

```powershell
celery -A blockchain_tracing_engine worker --loglevel=info --pool=solo
```

The `solo` worker pool is suitable for local Windows development. The current Django settings are development settings; configure secrets, `DEBUG`, allowed hosts, and deployment security before exposing the application publicly.

## Security

- Do not commit credentials, API keys, `.env` files, or local databases.
- Rotate any credentials that have been exposed.
- Do not use the development settings or risk scores as production security controls or definitive judgments.
