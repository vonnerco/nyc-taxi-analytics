# Loom script - NYC Yellow Taxi take-home

Target 5:00. 1440 px browser at 100%, terminal font 16+.
Pre-warm Streamlit once before recording (load the page, then start the take).
All figures below are the verified Q1 2024 numbers.

## 0:00 - What this is (20 s)

> This is a dashboard over 9.1 million NYC yellow taxi trips from January to
> March 2024, built as a dbt project on DuckDB: bronze, silver and gold layers,
> 58 data tests, and every number on screen comes from exactly one gold table -
> the app only renders.

## 0:20 - Dashboard tour (60 s)

Read the KPI strip: 9,076,422 trips, $249.57M charged, 17.94% fare-weighted tip.

> The main chart answers "when is demand high", and the brief asked for a
> day/week/hour grain. Three gold models back that selector - one row per day,
> per ISO week, per hour of day - and the selector swaps which table the chart
> reads. No aggregation happens in the app, so each grain is testable alone.

Click Week, then Hour of day, then back to Day.

> Day shows the weekly rhythm and the holiday dips, with the top three peaks
> annotated; Week compresses it to 13 points; hour of day peaks at 18:00, with
> 17:00 just behind.

Point at the bar on the right.

> The weekday bar is its own gold model, one row per ISO weekday - Thursday is
> the busiest day of the quarter, Monday the quietest.

Scroll to zones, tips, payments.

> Zones: a metric selector switches the ranking between total revenue, average
> fare and trip count, and the slider goes from 5 to 30. The top-N slice lives
> in the app, so the model keeps one row per zone. The tip chart is
> fare-weighted. Payments show mix and behaviour together: card is 78% of trips
> at a 22.54% tip rate, cash is 14% at zero because the TLC records no cash
> tips, and Flex Fare - code 0 in the TLC dictionary - is 7% at 5.46%.

Click one "Export this view as CSV" button.

> Every view exports the frame it drew, straight from gold.

## 1:20 - The build is the gate (40 s)

Terminal at repo root:

    cd dbt_project
    dbt build --profiles-dir .

> Twelve models and 58 tests in about ten to twenty seconds over 9.5 million
> bronze rows. dbt counts each model and test item, so the run ends at 70 of 70.
> A failing test stops the build, so the dashboard cannot be served from a broken
> table.

Point at `PASS=70 WARN=0 ERROR=0`.

## 2:00 - The layers (50 s)

Open `models/silver/slv_trips.sql`.

> Bronze is a straight copy of the parquet - no casts, no filters, no renames -
> so it can be diffed against the source column for column. It is materialized,
> not a view: dbt-duckdb resolves the parquet path at query time, so as a view
> it broke the moment anything queried it outside dbt_project. The table costs
> about 1.4 GB and makes the .duckdb queryable from anywhere.
>
> Silver is the only place cleaning happens: casts, the bounds - duration 1 to
> 180 minutes, distance 0.1 to 100 miles, non-negative fares, 1 to 6 passengers
> with null allowed for Flex Fare - the pinned quarter, de-duplication, the zone
> label join, and a surrogate trip_id: md5 of the de-duplication key, tested
> not_null and unique. It keeps 95.0% of bronze.

## 2:50 - Trace three numbers (50 s)

Open `models/gold/gld_tip_behavior.sql`.

> One row per distance bucket. tip_pct is sum of tips over sum of fares, not the
> average of per-trip percentages - otherwise a thousand 50-cent tips outweigh
> the long rides that carry the money. Cash trips record no tip, so this is a
> statement about card trips.

Open `models/gold/gld_revenue_by_zone.sql`.

> Grain is one row per zone: trips, revenue and average fare. The ranking and
> the top-N slice are the chart's job, not the model's.

Open `models/gold/gld_payment_analysis.sql`.

> Share, average fare and tip rate at one row per payment type, so the bar and
> the table read the same row.

## 3:40 - Trade-offs (50 s)

> One quarter, pinned: the brief allows one to three months, and a quarter is
> the smallest span where the week grain is a trend rather than five points.
> Silver exclusions are opinionated and every view inherits them. Three grain
> models for one chart cost three scans but keep each grain explicit and
> testable. DuckDB instead of Snowflake is deliberate: no credentials on this
> machine, and the dbt project is one profile swap away - the SQL stays
> portable. The hosted copy reads a 2 MB gold-only snapshot committed with the
> repo, so it runs without rebuilding the warehouse. No orchestration or CI,
> because dbt build is the pipeline at this size; the README says what changes at
> 100x volume.

## 4:30 - Close (30 s)

> README maps each brief requirement to the artifact that satisfies it, plus the
> tests, the trade-offs and the scalability notes. The repo is
> https://github.com/vonnerco/nyc-taxi-analytics - rendered docs at
> https://vonnerco.github.io/nyc-taxi-analytics/, and a deployed copy of this
> dashboard linked at the top of the README. Say each URL with its scheme, since a
> bare host is not clickable when pasted. prompts.txt logs every instruction with
> an ISO timestamp. Next, in production: incremental models, a Snowflake profile,
> CI on dbt build, and a freshness check on the TLC drop.

## Do not show on camera

- `prompts.txt` contents (say what it is, do not scroll it)
- The local dbt docs opened from `target/` (the published site is fine to name);
  the .venv and target/ artefacts
- Theming or Streamlit's own toolbar - the grain selector, zone controls and
  export buttons are the only controls to touch

## Recording checklist

1. `.venv` active (or call `.venv\Scripts\streamlit.exe` directly).
2. `streamlit run streamlit/app.py` running and loaded once before the take.
3. Terminal width > 100 columns so `PASS=70` is visible.
4. Second monitor closed; notifications off.
5. `.streamlit/config.toml` pins the server to 127.0.0.1; do not override it.
6. Published links: docs https://vonnerco.github.io/nyc-taxi-analytics/ and the
   live app https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app -
   always with `https://`, since a bare domain does not auto-link in mail or chat.
   The repository homepage points at the live app; both are linked in the README.
