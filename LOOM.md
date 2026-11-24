# Loom script - NYC Yellow Taxi take-home

<details>
<summary>Screen notes, setup and checklist (not narrated)</summary>

<details>
<summary>Recording setup</summary>

Target 4:55. Loom's free tier cuts at 5:00, so the last sentence lands with five
seconds to spare.
1440 px browser at 100%, terminal font 18+, terminal wider than 100 columns.
Pre-warm Streamlit once before recording (load the page, then start the take).
All figures below are the verified Q1 2024 numbers.

Window order for Alt+Tab: browser (dashboard) -> terminal -> file tabs -> docs tab -> file tabs.

Tooltip view on this machine: http://127.0.0.1:8000/LOOM.md - each narration block
then shows a bold hover hint naming the screen to switch to. It needs the local
file server running (`python serve.py "<repo>" 8000` from
`%LOCALAPPDATA%\local-file-server`); the address only works on the machine that
runs it, so it is not a link for readers of this file.

</details>

<details>
<summary>Beat timings</summary>

| Time | Beat | Length |
|---|---|---|
| 0:00 | Thanks, and what you will see | 25 s |
| 0:25 | Dashboard tour | 65 s |
| 0:25 | Charts 1-6 and downloads | inside the tour |
| 1:30 | The build is the gate | 40 s |
| 2:10 | The layers | 40 s |
| 2:50 | The same model, as documentation | 15 s |
| 3:05 | Trace three numbers | 40 s |
| 3:45 | Trade-offs | 40 s |
| 4:25 | Close | 30 s |

</details>

<details>
<summary>0:25 - chart-to-model map</summary>

| # | View-definition model | Streamlit dashboard element |
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

</details>

<details>
<summary>0:25 Chart 1 - Trip volume over time, cue and data source</summary>

Click Week, then Hour of day, then back to Day.

**Data source:** `gld_dashboard_facts`; view definition: `gld_trips_daily` (Day), `gld_trips_weekly` (Week), `gld_trips_hourly` (Hour of day).

</details>

<details>
<summary>0:25 Chart 2 - Busiest day of week, cue and data source</summary>

View the bar on the right.

**Data source:** `gld_dashboard_facts`; view definition: `gld_trips_by_dow`.

</details>

<details>
<summary>0:25 Chart 3 - Top pickup zones, data source</summary>

**Data source:** `gld_dashboard_facts`; view definition: `gld_revenue_by_zone`.

</details>

<details>
<summary>0:25 Chart 4 - Tip rate by trip distance, data source</summary>

**Data source:** `gld_dashboard_facts`; view definition: `gld_tip_behavior`.

</details>

<details>
<summary>0:25 Chart 5 - Payment mix, data source</summary>

**Data source:** `gld_dashboard_facts`; view definition: `gld_payment_analysis`.

</details>

<details>
<summary>0:25 Chart 6 - Payment behaviour, data source</summary>

**Data source:** `gld_dashboard_facts`; view definition: `gld_payment_analysis`.

</details>

<details>
<summary>1:30 - terminal commands and highlight</summary>

Terminal at repo root:

    cd dbt_project
    dbt build --profiles-dir .

Highlight dbt last line of code `PASS=82 WARN=0 ERROR=0`.

</details>

<details>
<summary>2:10 - Silver tab, `models/silver/slv_trips.sql`</summary>

The file tabs live in the same browser window, served by the local file server:
`http://127.0.0.1:8000/<path>?edit=1` (edit view carries the same colours as the
read-only view). Tab order left to right matches the recording order:

1. `slv_trips.sql` - 2:10
2. `gld_tip_behavior.sql` - 3:05, Chart 4
3. `gld_revenue_by_zone.sql` - 3:05, Chart 3
4. `gld_payment_analysis.sql` - 3:05, Charts 5-6

At 2:10 click the Silver tab (tab 1). Do not open it in Zed on camera.

</details>

<details>
<summary>2:50 - dbt docs cue, `slv_trips`, `trip_id` expanded</summary>

In dbt docs browser open the same documents slv_trips with trip_id row expanded to view its description and its tests.

**Important Note**: the Constraints column stays empty because this project defines no database constraints
the tests live in the Data Tests column and in the expanded row. Do
not call them constraints on camera.

After viewing dbt docs, come back to the file tabs for the 3:05 beat - do not go
to the editor.

</details>

<details>
<summary>3:05 - the three gold models, one tab each</summary>

Same file tabs as 2:10, tabs 2-4. One tab per model, one sentence per tab, and
say the chart name as the tab opens so the link is explicit:

| Click | File | Chart it backs |
|---|---|---|
| tab 2 | `gld_tip_behavior.sql` | Chart 4, Tip rate by trip distance |
| tab 3 | `gld_revenue_by_zone.sql` | Chart 3, Top pickup zones |
| tab 4 | `gld_payment_analysis.sql` | Charts 5-6, Payment mix / Payment behaviour |

Each tab has its own `**Show:**` line in the narration below, so the on-screen
cue and the spoken reason always name the same file.

</details>

<details>
<summary>Do not show on camera</summary>

- `prompts.txt` contents (say what it is, do not scroll it)
- The local dbt docs opened from `target/` (the published site is fine to name);
  the .venv and target/ artefacts
- Theming or Streamlit's own toolbar - the grain selector, zone controls and
  export buttons are the only controls to touch

</details>

<details>
<summary>Recording checklist</summary>

1. `.venv` active (or call `.venv\Scripts\streamlit.exe` directly).
2. `streamlit run streamlit/app.py` running and loaded once before the take.
3. Terminal width > 100 columns so `PASS=82` is visible.
4. Second monitor closed; notifications off.
5. `.streamlit/config.toml` pins the server to 127.0.0.1; do not override it.
6. Published links: docs https://vonnerco.github.io/nyc-taxi-analytics/ and the
   live app https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app -
   always with `https://`, since a bare domain does not auto-link in mail or chat.
   The repository homepage points at the live app; both are linked in the README.
7. Docs tab open before the take on the 2:50 screen: docs site -> Project ->
   models -> silver -> `slv_trips`, Columns visible, `trip_id` row expanded. Then
   that beat is one Alt+Tab.

</details>

</details>

## Narration script

**Show:** [Dashboard](https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app "Show the Main Dashboard")

> Thanks for watching my 9 million NYC yellow taxi trips dashboard,
> from January to March 2024. I created this using dbt,
> DuckDB & streamlit. I've run 69 tests to ensure data quality.
>
> I'll start with the dashboard, then i'll run the build that produces
> it, then i'll open the **bronze**, **silver** & **gold** models that the numbers come from.
>
> Every number you see comes from one **gold** table.

---

**Show:** [Dashboard](https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app "Show the Main Dashboard")

> Every view reads from one shared gold table, the `gld_dashboard_facts` table, cut
> as a cube: the date, payment, zone, distance, weekday and hour filters update the
> KPI strip and every chart together. The row-level models named below are the
> tested grain definitions behind each view.
>
> In Q1 2024 there were nine million, seventy-six thousand, four hundred and
> twenty-two trips, $249.57 million dollars charged & a 17.94% fare-weighted tip.
> That tip rate is total tips over total fares, not an average of per-trip
> percentages, so a fifty-cent tip cannot outweigh a long ride.
> The main chart answers **when is demand the highest**. The Day filter, the Week filter
> and the Hour of day filter are three grains of the same cube; choosing one rolls
> the cube up to that grain.

---

**Show:** [Chart 1](https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app "Show Trip volume over time - Day filter")

> The Day filter shows the weekly rhythm and the holiday dips. The Week filter
> compresses it to thirteen points. The Hour of day filter breaks the view into a
> 24 hour period, with 1800 hrs being the peak of the day and over six hundred
> and fifty-seven thousand trips taken.

---

**Show:** [Chart 2](https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app "Show Busiest day of week")

> The weekday bar is its own model, one row per ISO weekday: Thursday is the
> busiest day of the week for Q1 2024, Monday is the quietest.

---

**Cue:** Scroll down to view Top pickup zones and Tip rate by distance charts

**Show:** [Chart 3](https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app "Show Top pickup zones")

> The metric selector re-sorts the bars by **Total revenue**, **Average
> fare** or **Trip count**. The slider chooses how many zones are shown - five to
> thirty. Clicking a bar filters the entire dashboard to that zone.

---

**Show:** [Chart 4](https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app "Show Tip rate by trip distance")

> Tips are fare-weighted.

---

**Show:** [Chart 5](https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app "Show Payment mix")

> Payments show the mix of payment types. Card accounts for 78% of trips, cash
> 14%, and Flex Fare - payment-type code 0, a separate category from cash or card
> - accounts for 7%.

---

**Show:** [Chart 6](https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app "Show Payment behaviour")

> The table shows behaviour for that same gold row. Card has a 22.54% tip rate.
> Cash records 0% because the New York City Taxi and Limousine Commission (TLC)
> does not capture cash tips. Flex Fare is 5.46%.

---

**Show:** [Any chart](https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app "Show any chart")

> For your own local copy of the data, click **Export this view as CSV** in any chart.
> Every view exports the frame it drew, straight from the gold layer.

---

**Show:** [Terminal](http://127.0.0.1:7681 "Show the Terminal tab, run the build")

> Everything you just saw was produced by this one command - no hand-made tables.
> It runs thirteen models and sixty-nine tests in about twenty seconds over 9
> million bronze rows. dbt counts each model and test, so the run ends at 82 of
> 82. The build is the quality gate: a failing test stops it, so the dashboard
> cannot be served from a broken table.

---

**Show:** [Silver](http://127.0.0.1:8000/dbt_project/models/silver/slv_trips.sql "Show the Silver tab: slv_trips.sql")

> Bronze preserves the raw parquet data as-is: no casts, filters, renames or
> deduplication. It is loaded into DuckDB, but the data itself is unchanged, so it
> diffs against the source column for column. Silver is the only place cleaning
> happens. It converts the raw columns to proper types. It keeps trips from 1 to
> 180 minutes and 0.1 to 100 miles, drops negative fares, and keeps 1 to 6
> passengers - or null for Flex Fare. It limits the data to Q1 2024, removes
> duplicate trips, joins the zone lookup for names, and creates a trip_id by
> hashing the fields used to detect duplicates. dbt tests that ID for nulls and
> uniqueness. About 95% of bronze rows survive.

---

**Show:** [Docs](https://vonnerco.github.io/nyc-taxi-analytics/ "Show the dbt docs tab, slv_trips with trip_id expanded")

> Same model, now as generated documentation. The description says what the grain
> is; expanding trip_id shows the column description and the generic tests it
> carries - **not null** & **unique**. dbt builds this page from the same yml the tests
> run from, so the documentation can **never** drift away from the code.

---

**Show:** [Gold - Tip rate](http://127.0.0.1:8000/dbt_project/models/gold/gld_tip_behavior.sql "Show tab 2 of 4 - Chart 4: Tip rate by trip distance, from gld_tip_behavior.sql")

> This tab is the model behind **Chart 4**, tip rate by distance. One row per
> distance bucket. tip_pct is sum of tips over sum of fares, not an average of
> per-trip percentages - otherwise a thousand 50-cent tips outweigh the long rides
> that carry the money. Cash trips record no tip, so this is a statement about
> card trips.

---

**Show:** [Gold - Top pickup zones](http://127.0.0.1:8000/dbt_project/models/gold/gld_revenue_by_zone.sql "Show tab 3 of 4 - Chart 3: Top pickup zones, from gld_revenue_by_zone.sql")

> This tab backs **Chart 3**, the zone bars. One row per zone: trips, revenue,
> average fare. The ranking and the top-N slice are the chart's job, not the
> model's.

---

**Show:** [Gold - Payment mix](http://127.0.0.1:8000/dbt_project/models/gold/gld_payment_analysis.sql "Show tab 4 of 4 - Charts 5-6: Payment mix and Payment behaviour, from gld_payment_analysis.sql")

> This last tab backs **Charts 5 and 6**. Share, average fare and tip rate on one
> row per payment type, so the bar and the table read the same record.

---

**Show:** [Dashboard](https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app "Show the Main Dashboard")

> One quarter, pinned: the brief allows one to three months, and a quarter is the
> smallest span where the week grain is a trend rather than five points. Silver's
> exclusions are opinionated and every view inherits them. Three grain models for
> one chart cost three scans but keep each grain explicit and testable. DuckDB
> instead of Snowflake is deliberate - no credentials on this machine, one profile
> swap away, and the SQL stays portable. The hosted copy reads a 22 MB gold-only
> snapshot, so it runs without rebuilding the warehouse. No orchestration or CI,
> because dbt build is the pipeline at this size.

---

**Show:** [Dashboard](https://vonnerco-nyc-taxi-analytics-streamlitapp-idkoou.streamlit.app "Show the Main Dashboard")

> Every number you saw came from one command, and **sixty-nine tests** decided
> whether that command was allowed to finish. The chart was never the
> **deliverable** - the pipeline behind it is, with exactly one place where
> **every decision** lives and is checked on the way out. Repo, **generated docs**
> and a live copy are all in the README. One command, **sixty-nine tests**, one
> home for every decision.
>
> Thanks for watching.
