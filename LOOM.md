# Loom script - NYC Yellow Taxi take-home

Target 5:00. 1440 px browser at 100%, terminal font 16+.
Pre-warm Streamlit once before recording (load the page, then start the take).
All figures below are the verified Q1 2024 numbers.

## 0:00 - What this is (20 s)

> This is a four-view dashboard over 9.1 million NYC yellow taxi trips from
> January to March 2024, built as a dbt project on DuckDB. Bronze, silver and
> gold layers, forty-six data tests, and every number on screen comes from one
> gold table - the app only renders.

## 0:20 - Dashboard tour (55 s)

Read the KPI strip: 9,076,422 trips, $249.57M charged, 17.94% fare-weighted tip.

> The main chart answers "when is demand high", and the brief asked for a
> day/week/hour grain. There are three gold models - one row per day, per ISO
> week, per hour of day - and this selector swaps which table the chart reads.
> No aggregation happens in the app, so each grain is testable on its own.

Click Week, then Hour of day, then back to Day.

> Day shows the weekly rhythm and the holiday dips; Week compresses it to 13
> points; hour of day shows the 5-6pm peak.

Scroll to zones, tips, payment mix and the payment behaviour table.

> Top zones are revenue-sorted, and the top-10 slice lives in the app so the
> model keeps a total-per-zone grain. The tip chart is fare-weighted. Payments
> show both mix and behaviour: card is 78% of trips with a 22.54% tip rate, cash
> is 14% with zero, because the TLC records no cash tips, and Flex Fare - code 0
> in the TLC dictionary - is 7% of trips at 5.46%.

## 1:15 - The build is the gate (40 s)

Terminal at repo root:

    cd dbt_project
    dbt build --profiles-dir .

> Eleven models and 46 tests in about eleven seconds over 9.5 million bronze
> rows. dbt counts each item, so the run ends at 57 of 57. A failing test stops
> the build, so the dashboard cannot be served from a broken table.

Point at `PASS=57 WARN=0 ERROR=0`.

## 1:55 - The layers (55 s)

Open `models/silver/slv_trips.sql`.

> Bronze is a straight copy of the parquet - no casts, no filters - so it can
> be diffed against the source. It is materialized, not a view: dbt-duckdb
> resolves the parquet path at query time, so as a view it broke the moment
> anything queried it outside dbt_project. The table costs about a gigabyte and
> makes the .duckdb queryable from anywhere.
>
> Silver is the only place cleaning happens: casts, the bounds - duration 1 to
> 180 minutes, distance 0.1 to 100 miles, non-negative fares, 1 to 6 passengers
> with null allowed for Flex Fare - the pinned quarter, de-duplication, then the
> zone label join. It keeps 95.0% of bronze.

## 2:50 - Trace three numbers (50 s)

Open `models/gold/gld_tip_behavior.sql`.

> One row per distance bucket. tip_pct is sum of tips over sum of fares, not the
> average of per-trip percentages - otherwise a thousand 50-cent tips outweigh
> the long rides that carry the money. Cash trips record no tip, so this is a
> statement about card trips.

Open `models/gold/gld_revenue_by_zone.sql`.

> Grain is total revenue per zone; the top-10 slice is the chart's job.

Open `models/gold/gld_payment_analysis.sql`.

> Share, average fare and tip rate, all at one row per payment type, so the
> table and the bar read the same row.

## 3:40 - Trade-offs (50 s)

> One quarter, pinned: the brief allows one to three months, and a quarter is
> the smallest span where the week grain is a trend rather than five points.
> Silver exclusions are opinionated and every view inherits them. Three grains
> for one chart costs three scans, but keeps the grain explicit and testable.
> DuckDB instead of Snowflake is deliberate: no credentials on this machine, and
> the dbt project is one profile swap away - the SQL stays portable. No
> orchestration or CI, because dbt build is the pipeline at this size.

## 4:30 - Close (30 s)

> README maps each brief requirement to the artifact that satisfies it, lists
> the tests and the trade-offs. prompts.txt logs every instruction with an ISO
> timestamp, including the decisions I rejected. Next, if this were production:
> incremental models, a Snowflake profile, CI on dbt build, and a freshness
> check on the TLC drop.

## Do not show on camera

- `prompts.txt` contents (say what it is, do not scroll it)
- dbt docs, target/ artefacts, the .venv
- Streamlit filters or theming - the grain selector is the only control

## Recording checklist

1. `.venv` active (or call `.venv\Scripts\streamlit.exe` directly).
2. `streamlit run streamlit/app.py` running and loaded once before the take.
3. Terminal width > 100 columns so `PASS=57` is visible.
4. Second monitor closed; notifications off.
5. `.streamlit/config.toml` pins the server to 127.0.0.1; do not override it.
