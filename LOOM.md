# Loom script - NYC Yellow Taxi take-home

Target 4:55. Loom's free tier cuts at 5:00, so the last sentence lands with five
seconds to spare.
1440 px browser at 100%, terminal font 18+, terminal wider than 100 columns.
Pre-warm Streamlit once before recording (load the page, then start the take).
All figures below are the verified Q1 2024 numbers.

Window order for Alt+Tab: browser (app) -> terminal -> editor -> docs tab -> editor.

## 0:00 - What this is (20 s)

> Nine million NYC yellow taxi trips, January to March 2024, built as a dbt
> project on DuckDB - bronze, silver, gold - with fifty-eight data tests. Every
> number you are about to see is read from exactly one gold table. The app
> renders; it never calculates.

## 0:20 - Dashboard tour (65 s)

Read the strip: 9,076,422 trips, $249.57M charged, 17.94% fare-weighted tip.

> The main chart answers "when is demand high". Three gold models back that
> selector - one row per day, per ISO week, per hour of day - and the selector
> swaps which table the chart reads. No aggregation happens in the app, so each
> grain is testable on its own.

Click Week, then Hour of day, then back to Day.

> Day shows the weekly rhythm and the holiday dips, top three peaks annotated;
> Week compresses it to thirteen points; hour of day peaks at 18:00, with 17:00
> just behind.

Point at the bar on the right.

> The weekday bar is its own model, one row per ISO weekday: Thursday is the
> busiest day of the quarter, Monday the quietest.

Scroll to zones, tips, payments.

> Zones: the metric selector re-ranks by revenue, average fare or trip count, and
> the slider covers five to thirty. The top-N slice lives in the app, so the model
> keeps one row per zone. Tips are fare-weighted. Payments show mix and behaviour
> together: card is 78% of trips at a 22.54% tip rate, cash 14% at zero because the
> TLC records no cash tips, and Flex Fare - code 0 in the dictionary - 7% at 5.46%.

Click one "Export this view as CSV" button.

> Every view exports the frame it drew, straight from gold.

## 1:25 - The build is the gate (40 s)

Terminal at repo root:

    cd dbt_project
    dbt build --profiles-dir .

> Everything you just saw was produced by this one command - no hand-made tables.
> Twelve models and fifty-eight tests in about ten to twenty seconds over 9.5
> million bronze rows. dbt counts each model and test, so the run ends at 70 of 70.

Point at `PASS=70 WARN=0 ERROR=0`.

> A failing test stops the build, so the dashboard cannot be served from a broken
> table.

## 2:05 - The layers (40 s)

Open `models/silver/slv_trips.sql`.

> Bronze is a straight copy of the parquet - no casts, no filters, no renames - so
> it diffs against the source column for column. Silver is the only place cleaning
> happens: the types, the bounds - 1 to 180 minutes, 0.1 to 100 miles, non-negative
> fares, 1 to 6 passengers with null allowed for Flex Fare - the pinned quarter,
> de-duplication, the zone lookup, and a surrogate trip_id, md5 of the dedupe key,
> tested not null and unique. It keeps 95.0% of bronze.

## 2:45 - The same model, as documentation (15 s)

Alt+Tab to the published docs, already open on silver -> slv_trips, with the
trip_id row expanded (the chevron in MORE? opens its description and its tests).

> Same model, now as generated documentation. The description says what the grain
> is; expanding trip_id shows the column description and the generic tests it
> carries - not null and unique. dbt builds this page from the same yml the tests
> run from, so the documentation cannot drift away from the code.

Note: the Constraints column stays empty because this project defines no database
constraints; the tests live in the Data Tests column and in the expanded row. Do
not call them constraints on camera.

Alt+Tab back to the editor.

## 3:00 - Trace three numbers (40 s)

Open `models/gold/gld_tip_behavior.sql`.

> One row per distance bucket. tip_pct is sum of tips over sum of fares, not an
> average of per-trip percentages - otherwise a thousand 50-cent tips outweigh the
> long rides that carry the money. Cash trips record no tip, so this is a statement
> about card trips.

Open `models/gold/gld_revenue_by_zone.sql`.

> One row per zone: trips, revenue, average fare. The ranking and the top-N slice
> are the chart's job, not the model's.

Open `models/gold/gld_payment_analysis.sql`.

> Share, average fare and tip rate on one row per payment type, so the bar and the
> table read the same record.

## 3:40 - Trade-offs (45 s)

> One quarter, pinned: the brief allows one to three months, and a quarter is the
> smallest span where the week grain is a trend rather than five points. Silver's
> exclusions are opinionated and every view inherits them. Three grain models for
> one chart cost three scans but keep each grain explicit and testable. DuckDB
> instead of Snowflake is deliberate - no credentials on this machine, one profile
> swap away, and the SQL stays portable. The hosted copy reads a 2 MB gold-only
> snapshot, so it runs without rebuilding the warehouse. No orchestration or CI,
> because dbt build is the pipeline at this size.

## 4:25 - Close (30 s)

> Every number you saw came from one command, and fifty-eight tests decided
> whether that command was allowed to finish. The chart was never the deliverable -
> the pipeline behind it is, with exactly one place where each decision lives and
> is checked on the way out. Repo, generated docs and a live copy are all in the
> README. One command, fifty-eight tests, one home for every decision.

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
7. Docs tab open before the take on the 2:45 screen: docs site -> Project ->
   models -> silver -> `slv_trips`, Columns visible, `trip_id` row expanded. Then
   that beat is one Alt+Tab.
