# Loom script - NYC Yellow Taxi take-home

Target 4:55. Loom's free tier cuts at 5:00, so the last sentence lands with five
seconds to spare.
1440 px browser at 100%, terminal font 18+, terminal wider than 100 columns.
Pre-warm Streamlit once before recording (load the page, then start the take).
All figures below are the verified Q1 2024 numbers.

Window order for Alt+Tab: browser (app) -> terminal -> editor -> docs tab -> editor.

## 0:00 - Thanks, and what you will see (25 s)

> Thanks for taking the time to watch. This is 9 million NYC yellow taxi trips dashboard,
> from January to March 2024. I created this using dbt,
> DuckDB & streamlit. I've ran fifty-eight tests to ensure data quality.
>
> I'll start with the dashboard and what it shows, then i'll run the build that produces
> the it, then i'll open the bronze, silver & gold models that the numbers come from.
>
> Every number you see comes from one gold table.

## 0:25 - Dashboard tour (65 s)

| # | Gold model | Streamlit dashboard element |
|---|---|---|
| KPI | `gld_trip_summary` | KPI strip: `Trips`, `Total charged`, `Tip rate (fare-weighted)` |
| 1 | `gld_trips_daily` | `Trip volume over time` - Day line |
| 1 | `gld_trips_weekly` | `Trip volume over time` - Week line |
| 1 | `gld_trips_hourly` | `Trip volume over time` - Hour of day bars |
| 2 | `gld_trips_by_dow` | `Busiest day of week` bars |
| 3 | `gld_revenue_by_zone` | `Top pickup zones` bars |
| 4 | `gld_tip_behavior` | `Tip rate by trip distance` bars |
| 5 | `gld_payment_analysis` | `Payment mix` bars |
| 6 | `gld_payment_analysis` | `Payment behaviour` table |

> In Q1 2024 there were 9,076,422 trips, $249.57M charged & 17.94% fare-weighted tip.
> The main chart answers **when is demand high**. Three gold models back that
> selector - one row per day, per ISO week, per hour of day - and the selector
> swaps which table the chart reads. No aggregation happens in the app, so each
> grain is testable on its own.

### Chart 1 - Trip volume over time
Click Week, then Hour of day, then back to Day.

> Day shows the weekly rhythm and the holiday dips, three of the busiest days annotated;
> Week compresses it to thirteen points; hour of day peaks at 18:00, with 17:00
> just behind.

**Data source:** `gld_trips_daily` (Day), `gld_trips_weekly` (Week), `gld_trips_hourly` (Hour of day).

### Chart 2 - Busiest day of week
View the bar on the right.

> The weekday bar is its own model, one row per ISO weekday: Thursday is the
> busiest day of the quarter, Monday is the quietest.

**Data source:** `gld_trips_by_dow`.

### Chart 3 - Top pickup zones
> Zones: the metric selector re-ranks by revenue, average fare or trip count, and
> the slider covers five to thirty. The top-N slice lives in the app, so the model
> keeps one row per zone.

**Data source:** `gld_revenue_by_zone`.

### Chart 4 - Tip rate by trip distance
> Tips are fare-weighted.

**Data source:** `gld_tip_behavior`.

### Chart 5 - Payment mix
> Payments show mix and behaviour together: card is 78% of trips at a 22.54% tip
> rate, cash 14% at zero because the TLC records no cash tips, and Flex Fare - code
> 0 in the dictionary - 7% at 5.46%.

**Data source:** `gld_payment_analysis`.

### Chart 6 - Payment behaviour
> The table shows the behaviour half of that same gold row.

**Data source:** `gld_payment_analysis`.

### Downloads - all charts
> For you own local data copy you can click "Export this view as CSV" button in any dashboard view.
> Every view exports the frame it drew, straight from the gold layer.

## 1:30 - The build is the gate (40 s)

Terminal at repo root:

    cd dbt_project
    dbt build --profiles-dir .

> Everything you just saw was produced by this one command - no hand-made tables.
> Twelve models and fifty-eight tests in about twenty seconds over 9 million
> bronze rows. dbt counts each model and test, so the run ends at 70 of 70.

Highlight dbt last line of code `PASS=70 WARN=0 ERROR=0`.

> A failing test stops the build, so the dashboard cannot be served from a broken
> table.

## 2:10 - The layers (40 s)

In local Zed editor open `models/silver/slv_trips.sql`.

> Bronze is a straight copy of the parquet - no casts, no filters, no renames - so
> it diffs against the source column for column. Silver is the only place cleaning
> happens: the types, the bounds - 1 to 180 minutes, .1 to 100 miles, non-negative
> fares, 1 to 6 passengers with null allowed for Flex Fares - the pinned quarter,
> de-duplication, the zone lookup, and a surrogate trip_id, md5 of the dedupe key,
> tested not null and unique. It keeps 95.0% of bronze data.

## 2:50 - The same model, as documentation (15 s)

In dbt docs browser open the same documents slv_trips with trip_id row expanded to view its description and its tests.

> Same model, now as generated documentation. The description says what the grain
> is; expanding trip_id shows the column description and the generic tests it
> carries - **not null** & **unique**. dbt builds this page from the same yml the tests
> run from, so the documentation can **never** drift away from the code.

**Important Note**: the Constraints column stays empty because this project defines no database constraints
the tests live in the Data Tests column and in the expanded row. Do
not call them constraints on camera.

After viewing dbt docs browser re-open Zed editor.
--open gold model files--

## 3:05 - Trace three numbers (40 s)

Open `models/gold/gld_tip_behavior.sql`. powers **chart 6**

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

## 3:45 - Trade-offs (40 s)

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
> README - thanks for watching. One command, fifty-eight tests, one home for
> every decision.

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
7. Docs tab open before the take on the 2:50 screen: docs site -> Project ->
   models -> silver -> `slv_trips`, Columns visible, `trip_id` row expanded. Then
   that beat is one Alt+Tab.
