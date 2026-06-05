# Analytics Dashboard Demo

Streamlit dashboard example for monitoring sales, costs, invoices, and operational KPIs from a relational database populated by external API integrations.

This folder is part of an anonymized portfolio repository. It keeps the technical structure of a real dashboard while replacing customer names, provider names, domains, contacts, cloud accounts, and credentials with neutral placeholders.

## Purpose

The dashboard demonstrates how to:

- Query normalized sales and invoice data from a SQL database.
- Build interactive KPI views with Streamlit.
- Separate dashboard code from API ingestion jobs.
- Load runtime configuration through environment variables or AWS Secrets Manager.
- Package a Streamlit application for container-based deployment.

## Main Features

- Login flow backed by user records loaded from a secret store.
- Sales monitoring with date filters, product views, and transaction metrics.
- Invoice and cost monitoring with supplier, order, and product-level analysis.
- KPI panels for revenue, average ticket, cost incidence, and trend comparison.
- CSV export for selected tables and analysis outputs.
- Optional anomaly views based on configurable thresholds.

## Architecture

The dashboard is designed as the presentation layer of a small data platform:

1. Scheduled API ingestion jobs collect sales and invoice data from external services.
2. Ingestion jobs normalize records and write them into a relational database.
3. This Streamlit app reads from the database through SQLAlchemy.
4. Secrets such as database credentials and app users are loaded from AWS Secrets Manager or equivalent environment-specific configuration.
5. The app can run locally or as a Docker container on a cloud compute service.

Typical cloud components for this pattern:

| Component | Role |
| --- | --- |
| Streamlit app | Interactive analytics UI |
| Relational database | Stores normalized sales, invoice, supplier, order, and product data |
| Serverless jobs | Pull external APIs and update the database on a schedule |
| Container registry | Stores application and job images |
| Scheduler | Triggers ingestion jobs periodically |
| Logs and alarms | Tracks ingestion failures and runtime errors |
| Secret manager | Stores API credentials, database credentials, and app user data |

## Folder Structure

```text
analytics-dashboard/
  andamento_vendite_per_prodotto.py  Sales trend page
  app.py                             Streamlit entry point
  monitoraggio_costi_pizze.py       Product cost analysis page
  monitoraggio_dati_vendite.py      Sales overview page
  monitoraggio_fatture.py           Invoice monitoring page
  monitors_fatture.json             Example monitor configuration
  requirements.txt                  Python dependencies
  Dockerfile                        Container build definition
  LICENSE                           License file
  .gitignore                        Local ignore rules
  calculus_pages/
    costo_pizze.py                  Product cost calculation helpers
    vendite.py                      Sales query and analysis helpers
  config_scripts/
    aws_bucket_config.py            Example bucket configuration loader
    aws_secret_loader.py            Example secret loader
  user_pages/
    user_admin.py                   Admin dashboard page
    user_cliente.py                    Example role-specific dashboard page
```

## Configuration

No real credentials are included. The helper modules use placeholder names such as:

- `DB_SECRET_NAME=demo/database/credentials`
- `APP_USERS_SECRET_NAME=demo/app/users`
- `REPORTS_BUCKET_NAME=demo-api-reports-bucket`

For local development, provide equivalent values through environment variables or replace the secret loader with a local development configuration.

## Local Run

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

On macOS/Linux, activate the virtual environment with:

```bash
source .venv/bin/activate
```

Streamlit usually starts on `http://localhost:8501`.

## Data Model

The examples assume a relational schema with tables similar to:

| Table | Purpose |
| --- | --- |
| `Scontrini` | Sales transactions and product lines |
| `Fornitori` | Supplier master data |
| `Ordini` | Purchase or invoice headers |
| `Prodotti` | Purchased product or invoice detail lines |

The code is intended as a demonstration of integration and analytics patterns, not as a ready-to-run production product.

## Security Notes

- Keep secrets outside source control.
- Use environment variables or a secret manager for runtime values.
- Treat the included hostnames, database names, and bucket names as placeholders.
- Review and adapt IAM permissions before using this pattern in a real cloud environment.

## License

See `LICENSE`.
