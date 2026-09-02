# Sales Data ETL Platform

An end-to-end Sales Data ETL (Extract, Transform, Load) Pipeline and Analytics Platform.

## 📁 Project Structure

```text
sales-data-etl-platform/
│
├── data/
│   ├── raw/                  # Source CSV/JSON files
│   │   ├── orders.csv
│   │   ├── customers.csv
│   │   └── products.json
│   ├── processed/            # Cleaned / staging data
│   └── errors/               # Records that failed validation
│
├── src/                      # Core ETL logic
│   ├── extraction/           # Extraction modules (CSV, JSON, API)
│   ├── transformation/       # Cleaning & transformation modules
│   ├── validation/           # Data quality & schema validators
│   ├── loading/              # Data warehouse loaders (PostgreSQL)
│   ├── database/             # DB connection & DDL schemas
│   └── pipeline.py           # Pipeline orchestration script
│
├── airflow/                  # Airflow DAGs and plugins
│   ├── dags/
│   └── plugins/
│
├── sql/                      # SQL scripts
│   ├── staging/              # Staging table DDL
│   ├── warehouse/            # Data warehouse schema DDL
│   └── analytics/            # Analytical queries (revenue, products, etc.)
│
├── dashboard/                # Analytics dashboard application
│   ├── app.py
│   └── queries.py
│
├── tests/                    # Unit and integration tests
├── config/                   # Configuration files (YAML)
├── logs/                     # Pipeline execution logs
├── docker/                   # Dockerfiles
├── docker-compose.yml        # Multi-container orchestration (Postgres, Airflow, etc.)
├── requirements.txt          # Python dependencies
├── .env.example              # Template environment variables
├── .gitignore
├── README.md
└── run_pipeline.py           # Pipeline entrypoint
```
