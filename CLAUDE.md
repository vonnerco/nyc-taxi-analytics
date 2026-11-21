<!-- Assessment setup prompt (2026-11-19): "Create a CLAUDE.md file in the project root with the following instruction:" -->

# Project Rules

## Prompt Logging

Every time you receive a new instruction or prompt, append it to prompts.txt in the project root with a timestamp (ISO 8601) and a brief summary of what you did in response. Create the file if it doesn't exist. Keep this log updated throughout all sessions.

---

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
- gold: the chart-specific models keep exactly one grain per view. Trip volume
  uses three grains (daily, weekly, hour of day). The interactive app reads the
  shared `gld_dashboard_facts` gold cube, filters it, and rolls it up to each
  chart grain so all filters and charts stay in sync.
- tests: yml tests for not_null / unique / accepted_values; singular tests in
  dbt_project/tests for assertions that span rows.
- every number on the dashboard must come from a gold model, not silver.
- never commit data/raw/, *.duckdb, .venv - they are gitignored. One exception:
  data/demo/nyc_taxi_gold.duckdb (22 MB, the nine gold tables only) is committed
  so the Streamlit Cloud demo runs without the 1.4 GB local build; regenerate it
  whenever the gold grain changes.
- run dbt build after any model or test change; report the actual result.
- prompt log: "Project Rules > Prompt Logging" above is the contract; entries
  carry the ISO 8601 offset (America/New_York). Graded, not optional.
- prompts.txt entries carry a detailed Did paragraph: what changed, why, and how it
  was verified - not a one-sentence summary.
