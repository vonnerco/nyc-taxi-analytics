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

The seven local tabs live in the same browser window and are numbered on camera:

| Tab | What it is | Backs |
|---|---|---|
| Tab 1 | Streamlit dashboard | Phase 1 |
| Tab 2 | PowerShell terminal | Terminal demo |
| Tab 3 | dbt docs, `slv_trips`, `trip_id` expanded | docs beat |
| Tab 4 | `slv_trips.sql` | every chart |
| Tab 5 | `gld_tip_behavior.sql` | Chart 4, Tip rate by trip distance |
| Tab 6 | `gld_revenue_by_zone.sql` | Chart 3, Top pickup zones |
| Tab 7 | `gld_payment_analysis.sql` | Charts 5-6, Payment mix / Payment behaviour |

The file tabs are served by the local file server from
`http://127.0.0.1:8000/<path>?edit=1` (the edit view carries the same colours as
the read-only view). For the silver beat click Tab 4. Do not open the file in
Zed on camera.

</details>

<details>
<summary>2:50 - dbt docs cue, `slv_trips`, `trip_id` expanded</summary>

In dbt docs browser open the same documents slv_trips with trip_id row expanded to view its description and its tests.

**Important Note**: the Constraints column stays empty because this project defines no database constraints
the tests live in the Data Tests column and in the expanded row. Do
not call them constraints on camera.

After viewing dbt docs, come back to the file tabs for the gold-model beat - do not go
to the editor.

</details>

<details>
<summary>3:05 - the three gold models, one tab each</summary>

Same window, now Tab 5, Tab 6 and Tab 7. One tab per model, one sentence per
tab, and say the chart name as the tab opens so the link is explicit:

| Click | File | Chart it backs |
|---|---|---|
| Tab 5 | `gld_tip_behavior.sql` | Chart 4, Tip rate by trip distance |
| Tab 6 | `gld_revenue_by_zone.sql` | Chart 3, Top pickup zones |
| Tab 7 | `gld_payment_analysis.sql` | Charts 5-6, Payment mix / Payment behaviour |

The narration covers Chart 3 (Tab 6) first, then Chart 4 (Tab 5), then Charts 5-6
(Tab 7) - click in that order.

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

Hi i'm Corderio Vonner. I will be showing an NYC yellow taxi trips dashboard I created using dbt, DuckDB & streamlit. I have run 69 tests to ensure data quality.

I'll start by explaining the dashboard, then i'll run the build that produces the dashboard, then i'll open the **bronze**, **silver** & **gold** models behind the dashboard numbers.

The numbers you see on this dashboard all come from one **gold** table.

I will present this demo in two phases: first I will explain the dashboard information and features, then I will interact with the dashboard so you can watch it work.

Phase 1
Every view reads from one shared gold table, the `gld_dashboard_facts` table, cut as a cube: the date, payment, zone, distance, weekday and hour filters update the main KPI strip and every chart is synced accordingly.

In Q1 2024 there were nine million, seventy-six thousand, four hundred and twenty-two trips, two hundred and forty-nine million, five hundred and seventy thousand dollars charged & an average 17.94% fare-weighted tip for these trips. That tip rate is total tips over total fares, not an average of per-trip percentages, so a fifty-cent tip cannot outweigh a long ride.

The main chart answers **when is demand highest**. The Day filter, the Week filter and the Hour of day filter are three grains of the same cube; choosing one rolls the cube up to that grain.

In Trip volume over time chart. The Day filter shows the weekly rhythm and the holiday dips. The Week filter compresses it to thirteen points. The Hour of day filter breaks the view into a 24 hour period, with 1800 hrs being the peak of the day.

The Busiest day of week chart is its own model, showing one row per ISO weekday: Thursday is the busiest day of the week for Q1 2024 and Monday is the quietest.

The Top pickup zones chart allows you to select the metric to re-sort the bars by **Total revenue**, **Average fare** &or **Trip count**. The slider chooses how many zones are shown. Clicking a bar filters the entire dashboard to that single zone.

The Tip rate by trip distance chart shows one bar per distance bucket. Cash trips record no tip, so read this whole chart as a card-trip statement. The rule behind the number lives in the model, not the chart - I will open that model later.

The Payment mix chart shows the mix of payment types. Credit cards account for 78% of trips, cash accounts for 14%, and Flex Fares account for 7%.

The Payment behaviour chart shows the same record tip amounts. Credit cards have a 22.54% tip rate. Flex Fare is 5.46%. Cash trips show 0% because the New York City Taxi and Limousine Commission (TLC) does not capture cash tips.

For your own local copy of the data, click **Export this view as CSV** for any chart. Every view exports structured data directly from the gold layer.

Also every filter combination you configure can be saved as a named view.

Now I will set a custom view with the filters, save it as a named view, and open that same view from the saved views list to show the easy of use for this feature.

For the next 20 seconds watch the dashboard function is the exact manner I briefly explained.

Next Phase: Terminal Demo
Everything you just saw was produced by this one command - no hand-made tables. It runs thirteen models and sixty-nine tests in about twenty seconds. dbt counts each model and test, so the run ends at 82 of 82. The build is the quality gate: a failing test stops it, so the dashboard cannot be served from a broken table.

**DISCLAIMER**
"I used web terminal to show the actual files dbt runs for this demo"
"If this was a PRODUCTION environment I would never show these files"

Bronze preserves the raw parquet data as-is: no casts, filters, renames or deduplication. It is loaded into DuckDB, but the data itself is unchanged, so it diffs against the source column for column.

Silver is the only place cleaning happens. It converts the raw columns to proper types. It keeps trips from 1 to 180 minutes and .1 to 100 miles, it drops negative fares, and keeps 1 to 6 passengers - or null values for Flex Fare.

Silver layer processing:
First it limits the data to Q1 2024
Then it removes duplicate trips, joins the zone lookup for names, and creates a trip_id by hashing the fields used to detect duplicates

dbt tests that ID for nulls and uniqueness. About 95% of bronze rows survive

The description says what the grain is; expanding trip_id shows the column description and the generic tests it carries - **not null** & **unique**

dbt builds this dbt Docs page from the same yml the tests run from, so the documentation can **never** drift away from the code. I use this similar structure when deploying SaaS & PaaS Software solutions to PRODUCTION***

Tab 4 silver_trips.sql is behind every chart in the dashboard*

Every gold model reads it: facts, summary, daily, weekly, hourly, day of week, zone, behavior & analysis.

Tab 6 is the model behind **Chart 3**, Top pickup zones. One row per zone: trips, revenue, average fare. The ranking and the top-N slice are the chart's job, not the model's.

Tab 5 is the model behind **Chart 4**, Tip rate by distance. One row per distance bucket. tip_pct is sum of tips over sum of fares, not an average of per-trip percentages - otherwise a thousand small tips outweigh the long rides that carry the money.
That weighting lives here in the SQL, so the chart inherits it instead of recomputing it.
Cash trips record no tip, so this is a statement about card trips.

Tab 7 is the model behind **Charts 5 & 6**, These charts share, Average fare and Tip rate on one row per Payment type, so the bar and the table read the same record.

---

I used DuckDB rather than Snowflake because it is the less complicated setup route, and I have no Snowflake credentials on this machine. I administer Snowflake reporting for servers and dashboards at Cox, so this build stays one profile swap away and the SQL stays portable. The hosted copy reads a 22 MB gold-only snapshot, so it runs without rebuilding the entire data warehouse.

No orchestration or CI, because dbt build is the pipeline at this size. Thirteen models in one command - an orchestrator would only add a second copy of the graph, and no CI run could say more than the build already does.

Every number you saw came from one command, and **sixty-nine tests** decided whether that command was allowed to finish. The chart was never the **deliverable** - the pipeline behind it is, with exactly one place where **every decision** lives and is checked on the way out. One command, **sixty-nine tests**, one home for every decision.

Thanks for watching.
