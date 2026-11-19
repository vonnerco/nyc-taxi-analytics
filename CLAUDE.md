# nyc-taxi-analytics - agent notes

Take-home assessment: 2-3 hours, graded on layer separation, data quality tests,
gold-to-chart mapping, prompt log and articulated trade-offs.

Stack: dbt-core + dbt-duckdb, one DuckDB file at data/nyc_taxi.duckdb,
Streamlit read-only in front of it. Windows, PowerShell 5.1 compatible commands.
Pinned window is Q1 2024 (January-March), three monthly parquet files.

## Commands

setup (once):
    python -m venv .venv
    .venv\Scripts\pip install -r requirements.txt
    python scripts\download_data.py

build (always from dbt_project, so ../data resolves):
    cd dbt_project
    dbt build --profiles-dir .
    cd ..

run:
    streamlit run streamlit/app.py

fast rebuild while iterating on one model:
    cd dbt_project
    dbt build --profiles-dir . --select +gld_tip_behavior

## Rules

- bronze: select * from the source only. No casts, filters or renames. It is
  materialized (not a view) so the DuckDB file is queryable from any directory.
- silver: all typing, filtering, de-duplication, labels and derivations.
- gold: exactly one grain per view, and no columns the view does not read.
  Trip volume uses three grains (daily, weekly, hour of day); the app picks a
  table, it never aggregates.
- tests: yml tests for not_null / unique / accepted_values; singular tests in
  dbt_project/tests for assertions that span rows.
- every number on the dashboard must come from a gold model, not silver.
- never commit data/raw/, *.duckdb, .venv - they are gitignored.
- run dbt build after any model or test change; report the actual result.
- prompt log: every instruction gets an ISO 8601 timestamped entry in
  prompts.txt - what was asked and what was done. This is graded, not optional.
