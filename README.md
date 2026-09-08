# Sales Data ETL Platform

An end-to-end Sales Data ETL (Extract, Transform, Load) Pipeline and Analytics Platform.

## 📁 Project Structure

```text
sales-data-etl-platform/
│
├── data/
│   ├── raw/                  # Raw dataset (Online Retail.xlsx)
│   ├── processed/            # Cleaned & transformed data (sales_processed.csv)
│   └── errors/               # Records that failed validation (validation_errors.csv)
│
├── src/                      # Core ETL logic
│   ├── extraction/           # Extraction & profiling modules (ExcelReader, profiler)
│   ├── validation/           # Data quality & schema validator (DataValidator)
│   ├── transformation/       # Cleaning & transformation modules (DataTransformer)
│   ├── loading/              # Data warehouse loaders (WarehouseLoader)
│   ├── database/             # PostgreSQL DB connection
│   └── utils/                # Logging utility
│
├── sql/                      # Data warehouse & analytics SQL scripts
│   ├── 01_create_schema.sql
│   ├── 02_create_dimensions.sql
│   ├── 03_create_fact.sql
│   ├── 04_create_indexes.sql
│   └── analytics/            # Analytical SQL queries (01 to 08)
│
├── dashboard/                # Streamlit analytics dashboard
│   └── app.py
│
├── logs/                     # Pipeline execution logs (etl.log)
├── docker-compose.yml        # PostgreSQL service container
├── requirements.txt          # Python dependencies
├── .env.example              # Template environment variables
├── .gitignore
├── README.md
└── run_pipeline.py           # Pipeline entrypoint
```
