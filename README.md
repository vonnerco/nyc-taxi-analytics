# NYC Yellow Taxi Analytics - Q1 2024

dbt over DuckDB, eight gold models, one Streamlit dashboard with a
day/week/hour grain selector. Built as a 2-3 hour take-home; the bar is a
pipeline a reviewer can clone and run from scratch, with every number on screen
traceable to exactly one gold table.

Live dashboard: https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app

Rendered model documentation: https://vonnerco.github.io/nyc-taxi-analytics/

## Live demo

**App:** [vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app](https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app)

The deployed copy reads the committed gold-only snapshot
(`data/demo/nyc_taxi_gold.duckdb`, 2 MB) and says so in a caption, so the hosted
app needs no 1.4 GB build. Streamlit Cloud sleeps an idle app; the first load may
take half a minute to wake. The quick start below builds the real pipeline locally.

[![Deploy to Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/deploy?repository=vonnerco/nyc-taxi-analytics&branch=main&mainModule=streamlit/app.py)

GitHub Pages cannot execute Streamlit, so a running copy needs a host; the button
above redeploys it to Streamlit Community Cloud (Python 3.11) in one step.

## Quick start

```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
python scripts\download_data.py          # ~153 MB parquet (Jan-Mar) + zone lookup
cd dbt_project
dbt build --profiles-dir .
cd ..
streamlit run streamlit/app.py
```

Steps 4-5 are also wrapped in one PowerShell command:

```powershell
.\scripts\run_pipeline.ps1               # dbt build: every model and every test
.\scripts\run_pipeline.ps1 -Select gold  # any dbt selection, same gate
```

Data is not committed, except the 2 MB gold-only snapshot under `data/demo/` that
the hosted demo reads. `scripts/download_data.py` fetches the pinned quarter from
the TLC CDN; everything else is reproducible from the repo.

## Pipeline

```
data/raw/yellow_tripdata_2024-0{1,2,3}.parquet
      |  sources (external_location glob, no copy)
      v
bronze   brz_yellow_trips (table) brz_zones (table)
      |  typing, filters, de-dup, zone labels
      v
silver   slv_trips (table)        slv_zones (table)
      |  one grain per view, no extra columns
      v
gold     gld_trip_summary (1 row)      gld_trips_daily (91 rows)
         gld_trips_weekly (13 rows)    gld_trips_hourly (24 rows)
         gld_trips_by_dow (7 rows)     gld_revenue_by_zone
         gld_payment_analysis          gld_tip_behavior
      |  read-only DuckDB, cached queries
      v
streamlit/app.py  (KPI strip + five views)
```

Field descriptions in `sources.yml` are copied verbatim from the TLC dictionary
(18 March 2025); the 2024 extracts carry 19 of its 20 fields (`cbd_congestion_fee`
starts 5 January 2025).

Bronze is a straight copy of the parquet with no casts or filters, so a reviewer
can always diff it against the source. It is materialized because dbt-duckdb
resolves the parquet path at query time: as a view it broke outside
`dbt_project/`, and a self-contained `.duckdb` is worth the ~1.4 GB. Silver is
the only place cleaning happens; gold is chart-shaped so the app holds no logic.

## Gold-to-view mapping

| View | Question | Gold model(s) | Grain | Columns |
|---|---|---|---|---|
| KPI strip | How big is the quarter? | `gld_trip_summary` | exactly one row | `trips`, `total_revenue`, `tip_pct` |
| Trip volume | When is demand high? | `gld_trips_daily` / `gld_trips_weekly` / `gld_trips_hourly` / `gld_trips_by_dow` | one row per day / ISO week start / hour of day / weekday | `trip_count` (+ `revenue` for day/week) |
| Top pickup zones | Where is revenue concentrated? | `gld_revenue_by_zone` | one row per zone | `pickup_zone`, `trip_count`, `total_revenue`, `avg_fare` |
| Payment mix | How do people pay, and how does behaviour differ? | `gld_payment_analysis` | one row per payment type | `trip_count`, `trip_share_pct`, `avg_fare`, `tip_pct` |
| Tip by distance | Does distance change tipping? | `gld_tip_behavior` | one row per distance bucket | `distance_bucket`, `tip_pct` |

The Day / Week / Hour-of-day selector swaps the gold table the chart reads; no
aggregation happens in the app. Top-10 slicing lives in `app.py` so the zone
model keeps its total-per-zone grain.

`tip_pct` is fare-weighted (`sum(tip) / sum(fare)`), not the mean of per-trip
percentages: averaging percentages would let a thousand 50-cent tips outweigh
the long rides that actually carry the money.

## Data quality tests

- Bronze: `not_null` on vendor, pickup, dropoff and total amount - a raw row
  that loses its meter timestamps is not salvageable - plus `not_null`/`unique`
  on the zone lookup's `LocationID` so a bad download fails before the join.
- Silver: `not_null` on the keys and measures, `accepted_values` on the
  payment label and borough so the CASE mapping cannot silently drift, and
  `not_null` + `unique` on the surrogate `trip_id`.
- Gold: `not_null` + `unique` on every grain key, which is what makes each
  view safe to read as one-row-per-category.
- Singular tests (`dbt_project/tests/`): duration bounds, plausible pickup
  range (locks the pinned quarter), non-negative fares, and a populated,
  positive summary row.

`dbt build` runs 58 tests; a failing test stops the build, so the dashboard
cannot be served from a broken table.

## Rendered documentation

The `dbt docs` site is published at
[vonnerco.github.io/nyc-taxi-analytics](https://vonnerco.github.io/nyc-taxi-analytics/)
from the `gh-pages` branch - `index.html`, `manifest.json` and `catalog.json`, produced
by `dbt docs generate`. `target/` stays gitignored on `main`; republish only when a
model or description changes.

## Trade-offs

- **One quarter, pinned.** January-March 2024: 153 MB of parquet, 9.08 M trips
  after cleaning. A quarter is the smallest span where the Week toggle is a
  real trend (13 points) rather than four boundaries; multi-year would need
  incremental models, and the take-home grades reasoning, not volume.
- **Size is chosen at ingestion, never in bronze.** `scripts/download_data.py`
  pins three months; trim `MONTHS` to one for a smaller local build. Bronze
  keeps no filter, cap or cast, so what it holds is exactly what the TLC
  published.
- **Silver exclusions are opinionated.** Duration 1-180 min, distance
  0.1-100 mi, fare >= 0, passengers 1-6 with null allowed, pickup inside the
  quarter. Null is kept on purpose: TLC's Flex Fare rows (payment_type 0) carry no
  passenger count, and dropping them would erase a payment type the brief asks us
  to analyse. The bounds keep 95.0% of bronze rows - GPS gaps, metered corrections,
  driver typos - and every view inherits that cut.
- **Three grains for one chart.** Daily, weekly and hour-of-day are separate
  gold tables, so each grain is testable and the app only picks a table. The
  cost is three scans of silver and three models to keep; the alternative is a
  day x hour model plus app-side resampling, which moves logic into the app and
  blurs the grain the brief asks to define.
- **Cash trips show no tip.** The TLC records tips on card payments only, so
  the payment table shows 22.54% for cards and 0.00% for cash, and any tip
  conclusion is a statement about card trips, not all trips. Flex Fare reports
  5.46%, far below cards, so it is never pooled into the card rate.
- **Dedupe key is heuristic.** Same vendor, timestamps, zones and total is
  duplicate-shaped; a shared trip would be dropped with it. The surrogate
  `trip_id` is an md5 of that key, so it inherits the heuristic - it identifies
  a row after de-duplication, not a trip in the physical world.
- **DuckDB file, not a warehouse.** Fast to clone, no credentials, no hosting -
  and the wrong choice the moment two people need to write concurrently. The
  role names Snowflake; this machine has no account, so the SQL keeps to
  portable constructs and the dbt project is one profile swap away.
- **Bronze carries no casts or renames.** A common medallion variant makes
  bronze a typed mirror: rename the messy source columns
  (`tpep_pickup_datetime` -> `pickup_at`, `PULocationID` -> `pickup_zone_id`)
  and cast types, while dropping no rows. This project takes the stricter
  variant - bronze is byte-faithful to the parquet, and every rename and cast
  happens once, in silver. The reason is reviewability: bronze diffs against the
  source column for column, and a type decision has exactly one home. The cost is
  that silver is not thin - it is where the data contract is defined.
- **Bronze materialized, database ~1.4 GB.** A bronze view kept the raw data
  coupled to `dbt_project/` as the working directory; the table makes the
  `.duckdb` queryable from anywhere (the app, a shell, a reviewer). The cost is
  disk and a 9 s build instead of 2 s.
- **No orchestration, no CI.** `dbt build` is the pipeline. Adding Airflow to a
  three-file source would be theatre.

## Scalability

- **Today.** One DuckDB file (~1.4 GB), 9.5 M bronze rows, an 11 s full rebuild.
  Every model is a full refresh, which is the right shape at this size.
- **Partitioning.** The source is already one parquet per month; silver could be
  partitioned by `pickup_date` so date-filtered queries prune files instead of
  scanning the quarter.
- **Incremental models.** `slv_trips` would move to `materialized='incremental'`
  with `trip_id` as the unique key and a lookback window on `pickup_at`, so a
  nightly run reprocesses only late-arriving trips. Each gold model becomes
  incremental on its grain key.
- **At 100x volume (~950 M trips).** The single-file warehouse stops fitting
  comfortably: move to Snowflake or BigQuery, keep the SQL (the models use
  portable constructs), make gold incremental, and have Streamlit read a cached
  aggregate layer rather than the warehouse.
- **Cost control.** Partition on pickup date, read only the columns the models
  use (12 of the dictionary's 20), and keep top-N slicing in the app so gold
  stays at one row per zone.

## Decisions taken early (expensive to reverse)

- **Engine and storage.** dbt-duckdb, one local `data/nyc_taxi.duckdb`,
  rebuilt by `dbt build`, read read-only by Streamlit. Moving to BigQuery or
  Snowflake later rewrites the profile, not the models or tests.
- **Silver grain and thresholds.** One cleaned trip row with a surrogate
  `trip_id`; the caps above. Every cap re-baselines every count and every test.
- **Gold grains.** One row per day, per ISO week, per hour of day, per zone, per
  payment type, per distance bucket, plus a single-row summary. Changing a grain
  breaks its view and its tests together.

## How this meets the brief

| Brief asks for | Where |
|---|---|
| Public git repository | [github.com/vonnerco/nyc-taxi-analytics](https://github.com/vonnerco/nyc-taxi-analytics) (public, `main`) |
| CLAUDE.md whose first prompt installs prompt logging | `CLAUDE.md`, rule "prompt log"; log is `prompts.txt` with ISO 8601 timestamps |
| dbt project with bronze, silver, gold | `dbt_project/models/` |
| Data quality tests and documentation | 58 tests, yml descriptions on every model and column, singular tests; rendered at [vonnerco.github.io/nyc-taxi-analytics](https://vonnerco.github.io/nyc-taxi-analytics/) |
| Streamlit dashboard powered by gold | `streamlit/app.py`; every number reads a gold model; live at [streamlit.app](https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app) |
| Trip volume over time, day/week/hour, defined grain | `gld_trips_daily` / `_weekly` / `_hourly` + grain selector; `gld_trips_by_dow` for seasonality |
| Revenue by pickup zone, metric, filter or sort | `gld_revenue_by_zone`, top 10 sorted by revenue |
| Payment type analysis of behaviour | `gld_payment_analysis`: share, average fare, fare-weighted tip |
| One additional visualisation | `gld_tip_behavior` (tip rate by distance) |
| Loom walkthrough | `LOOM.md` (script; video recorded from the running app) |

## Verified on this machine

- `dbt build` - 70/70 pass (12 models, 58 tests), 11.3 s on 9,554,778 bronze rows.
- Silver keeps 9,076,422 rows (95.0%); every gold row sums from that grain.
- Streamlit `AppTest` - 0 exceptions, 5 charts, 1 table, grain selector with
  three options; metrics 9,076,422 trips / $249.57M / 17.94% tip.
- Same `AppTest` with the full database moved aside - the app falls back to
  `data/demo/nyc_taxi_gold.duckdb` and still reports those metrics.
- `screenshots/dashboard.png` - captured from the running app at 1440 px.

## Repo layout

```
nyc-taxi-analytics/
  LICENSE              MIT
  CLAUDE.md            agent notes for this repo
  prompts.txt          prompt and decision log (graded)
  LOOM.md              walkthrough script
  README.md
  requirements.txt
  data/raw/            downloaded, gitignored
  data/demo/           gold-only snapshot (2 MB) the hosted demo reads
  dbt_project/
    dbt_project.yml
    profiles.yml       relative DuckDB path, committed on purpose
    models/bronze/     sources.yml, brz_yellow_trips, brz_zones
    models/silver/     slv_trips, slv_zones (+ yml tests)
    models/gold/       eight chart-shaped tables + gold.yml
    tests/             four singular tests
  streamlit/app.py
  screenshots/
  scripts/download_data.py
  scripts/run_pipeline.ps1
```

## Prompt log

`prompts.txt` records every instruction with an ISO 8601 timestamp, the mode
and grain decisions, and the ones that were rejected. It is the collaboration
record the brief asks for.

## Screenshots

`screenshots/dashboard.png` shows the running dashboard with real Q1 2024
numbers, so a reviewer can judge the views without a local build.
