"""NYC Yellow Taxi dashboard: Q1 2024, interactive gold-cube views."""

from collections.abc import Mapping
from datetime import date, timedelta
from pathlib import Path

import altair as alt
import duckdb
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
# The pipeline writes data/nyc_taxi.duckdb. A gold-only snapshot ships with the
# repo so the app also runs on a host that never built the 1.4 GB database.
DB_CANDIDATES = [
    DATA_DIR / "nyc_taxi.duckdb",
    DATA_DIR / "demo" / "nyc_taxi_gold.duckdb",
]
DB_PATH = next((p for p in DB_CANDIDATES if p.exists()), DB_CANDIDATES[0])
USING_DEMO = DB_PATH.name == "nyc_taxi_gold.duckdb"

FILTER_KEYS = (
    "flt_dates",
    "flt_payments",
    "flt_zones",
    "flt_distances",
    "flt_dows",
    "flt_hours",
)
PENDING_FILTERS = "_pending_filter_updates"
RESET_FLAG = "_reset_filters"
CHART_KEY_PREFIX = "chart_"

DOW_LABELS = {
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
    7: "Sunday",
}

st.set_page_config(page_title="NYC Yellow Taxi - Q1 2024", layout="wide")


@st.cache_data(ttl=600, show_spinner=False)
def query(sql: str, params: tuple = ()) -> pd.DataFrame:
    """Read gold tables. read_only lets dbt rebuild while the app stays open."""
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        return con.execute(sql, params).df()


def has_rows(df: pd.DataFrame, label: str) -> bool:
    """Warn instead of drawing an empty chart when a filter excludes every row."""
    if df.empty:
        st.warning(f"{label} returned no rows for the current filters.")
        return False
    return True


VIEW_SEPARATOR = "|"


def view_from_params(params) -> dict:
    """Decode the filter state kept in the URL, so a view can be bookmarked."""
    view = {}
    raw_dates = str(params.get("dates", ""))
    if ":" in raw_dates:
        start, end = raw_dates.split(":", 1)
        try:
            view["flt_dates"] = (date.fromisoformat(start), date.fromisoformat(end))
        except ValueError:
            pass
    for key, param in (
        ("flt_payments", "payments"),
        ("flt_zones", "zones"),
        ("flt_distances", "distances"),
        ("flt_dows", "dows"),
        ("flt_hours", "hours"),
    ):
        raw = str(params.get(param, ""))
        items = [item for item in raw.split(VIEW_SEPARATOR) if item]
        if not items:
            continue
        if key in ("flt_dows", "flt_hours"):
            try:
                items = [int(item) for item in items]
            except ValueError:
                continue
        view[key] = items
    return view


def params_from_filters(filters: dict, min_date, max_date) -> dict:
    """Encode the current filter state for the address bar."""
    params = {}
    if filters["start"] != min_date or filters["end"] != max_date:
        params["dates"] = f"{filters['start']}:{filters['end']}"
    for param, key in (
        ("payments", "payments"),
        ("zones", "zones"),
        ("distances", "distances"),
        ("dows", "dows"),
        ("hours", "hours"),
    ):
        values = filters[key]
        if values:
            params[param] = VIEW_SEPARATOR.join(str(value) for value in values)
    return params


def export_csv(df: pd.DataFrame, filename: str, label: str) -> None:
    """Download exactly the frame the chart was drawn from."""
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        key=filename,
    )


def build_where(filters: dict, extra: tuple[str, ...] = ()) -> tuple[str, tuple]:
    """Return a parameterised WHERE clause for the shared gold cube."""
    clauses = ["pickup_date between ? and ?"]
    params = [filters["start"], filters["end"]]
    filter_columns = (
        ("payments", "payment_type"),
        ("zones", "pickup_zone"),
        ("distances", "distance_bucket"),
        ("dows", "dow_iso"),
        ("hours", "pickup_hour"),
    )
    for key, column in filter_columns:
        values = filters[key]
        if values:
            placeholders = ", ".join("?" for _ in values)
            clauses.append(f"{column} in ({placeholders})")
            params.extend(values)
    clauses.extend(extra)
    return " where " + " and ".join(clauses), tuple(params)


def event_values(event, parameter: str, field: str) -> tuple:
    """Extract selected field values from a Vega-Lite point selection."""
    if event is None:
        return ()
    try:
        selection = event["selection"]
    except (KeyError, TypeError):
        selection = getattr(event, "selection", {})
    try:
        rows = selection[parameter]
    except (KeyError, TypeError):
        rows = getattr(selection, parameter, [])
    if rows is None:
        return ()
    if isinstance(rows, Mapping):
        rows = [rows]
    values = []
    for row in rows:
        if not isinstance(row, Mapping) or field not in row:
            continue
        value = row[field]
        if value not in values:
            values.append(value)
    return tuple(values)


def event_rows(event) -> tuple[int, ...]:
    """Extract selected row indexes from a Streamlit dataframe."""
    if event is None:
        return ()
    try:
        selection = event["selection"]
    except (KeyError, TypeError):
        selection = getattr(event, "selection", {})
    try:
        rows = selection["rows"]
    except (KeyError, TypeError):
        rows = getattr(selection, "rows", [])
    return tuple(int(row) for row in rows)


def sync_filter(
    widget_key: str,
    target_key: str,
    values: tuple,
    empty_value,
) -> None:
    """Move a chart selection into its matching filter and rerun once."""
    state_key = f"_last_selection_{widget_key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = values
        return
    if tuple(st.session_state[state_key]) == tuple(values):
        return
    st.session_state[state_key] = values
    st.session_state[PENDING_FILTERS] = {
        target_key: list(values) if values else empty_value
    }
    st.rerun()


def sync_date_filter(
    widget_key: str,
    values: tuple,
    grain: str,
    min_date,
    max_date,
) -> None:
    """Translate a chart 1 point into the shared pickup-date range."""
    state_key = f"_last_selection_{widget_key}"
    if state_key not in st.session_state:
        st.session_state[state_key] = values
        return
    if tuple(st.session_state[state_key]) == tuple(values):
        return
    st.session_state[state_key] = values

    if values:
        parsed = []
        for value in values:
            if isinstance(value, (int, float)):
                parsed.append(pd.to_datetime(value, unit="ms").date())
            else:
                parsed.append(pd.Timestamp(value).date())
        start = min(parsed)
        end = max(parsed)
        if grain == "Week":
            end = end + timedelta(days=6)
        start = max(start, min_date)
        end = min(end, max_date)
        new_value = (start, end)
    else:
        new_value = (min_date, max_date)
    st.session_state[PENDING_FILTERS] = {"flt_dates": new_value}
    st.rerun()


def active_filter_labels(filters: dict, min_date, max_date) -> list[str]:
    labels = []
    if filters["start"] != min_date or filters["end"] != max_date:
        labels.append(
            f"Dates: {filters['start']} to {filters['end']}"
        )
    if filters["payments"]:
        labels.append("Payment: " + ", ".join(filters["payments"]))
    if filters["zones"]:
        shown = ", ".join(filters["zones"][:2])
        if len(filters["zones"]) > 2:
            shown += f" +{len(filters['zones']) - 2}"
        labels.append("Zone: " + shown)
    if filters["distances"]:
        labels.append("Distance: " + ", ".join(filters["distances"]))
    if filters["dows"]:
        labels.append(
            "Day: " + ", ".join(DOW_LABELS.get(int(v), str(v)) for v in filters["dows"])
        )
    if filters["hours"]:
        labels.append(
            "Hour: " + ", ".join(f"{int(v):02d}:00" for v in filters["hours"])
        )
    return labels


if not DB_PATH.exists():
    st.error(
        "No DuckDB file yet. Run: cd dbt_project; dbt build --profiles-dir . "
        "(or commit the gold-only snapshot at data/demo/nyc_taxi_gold.duckdb)."
    )
    st.stop()

st.title("NYC Yellow Taxi - Q1 2024")
st.caption("January-March 2024. Every number reads the shared gold dashboard cube.")

with st.expander("How this is built"):
    st.markdown(
        "dbt bronze -> silver -> gold on DuckDB. Source: NYC TLC trip records "
        "(January-March 2024) and the taxi zone lookup. "
        "The interactive dashboard filters one shared gold cube and rolls it up "
        "to the selected grain; the view-specific gold models below remain the "
        "tested definitions of each view."
    )
    st.markdown(
        "| # | Streamlit dashboard element | Gold model | Interactive source |\n"
        "|---|---|---|---|\n"
        "| KPI | KPI strip | `gld_trip_summary` | `gld_dashboard_facts` |\n"
        "| 1 | Trip volume over time - Day | `gld_trips_daily` | `gld_dashboard_facts` |\n"
        "| 1 | Trip volume over time - Week | `gld_trips_weekly` | `gld_dashboard_facts` |\n"
        "| 1 | Trip volume over time - Hour of day | `gld_trips_hourly` | `gld_dashboard_facts` |\n"
        "| 2 | Busiest day of week | `gld_trips_by_dow` | `gld_dashboard_facts` |\n"
        "| 3 | Top pickup zones | `gld_revenue_by_zone` | `gld_dashboard_facts` |\n"
        "| 4 | Tip rate by trip distance | `gld_tip_behavior` | `gld_dashboard_facts` |\n"
        "| 5 | Payment mix | `gld_payment_analysis` | `gld_dashboard_facts` |\n"
        "| 6 | Payment behaviour | `gld_payment_analysis` | `gld_dashboard_facts` |"
    )
    if USING_DEMO:
        size_mb = DB_PATH.stat().st_size / 1_000_000
        st.markdown(
            f"This hosted copy reads the committed gold-only snapshot "
            f"({size_mb:.1f} MB, nine gold tables), so it runs without rebuilding "
            "the 1.4 GB local database. Run the pipeline locally for the full "
            "bronze-to-gold rebuild."
        )
    else:
        st.markdown(
            "Running against the full local database built by the dbt pipeline."
        )

try:
    bounds = query(
        "select min(pickup_date) as min_date, max(pickup_date) as max_date "
        "from gld_dashboard_facts"
    ).iloc[0]
    metadata = {
        "min_date": pd.Timestamp(bounds["min_date"]).date(),
        "max_date": pd.Timestamp(bounds["max_date"]).date(),
        "payments": tuple(
            query(
                "select payment_type, sum(trip_count) as trips "
                "from gld_dashboard_facts group by 1 order by trips desc"
            )["payment_type"].tolist()
        ),
        "zones": tuple(
            query(
                "select pickup_zone, sum(trip_count) as trips "
                "from gld_dashboard_facts group by 1 order by trips desc"
            )["pickup_zone"].tolist()
        ),
        "distances": tuple(
            query(
                "select distance_bucket from gld_dashboard_facts group by 1 "
                "order by case distance_bucket "
                "when '0-1 mi' then 1 when '1-3 mi' then 2 "
                "when '3-5 mi' then 3 when '5-10 mi' then 4 else 5 end"
            )["distance_bucket"].tolist()
        ),
        "dows": tuple(
            query("select distinct dow_iso from gld_dashboard_facts order by 1")[
                "dow_iso"
            ].tolist()
        ),
        "hours": tuple(
            query(
                "select distinct pickup_hour from gld_dashboard_facts order by 1"
            )["pickup_hour"].tolist()
        ),
    }
except duckdb.Error as exc:
    st.error(
        "The interactive gold cube is missing. Rebuild the dbt project and, for "
        "the hosted demo, regenerate data/demo/nyc_taxi_gold.duckdb."
    )
    st.code(str(exc))
    st.stop()

if st.session_state.pop(RESET_FLAG, False):
    for key in list(st.session_state):
        if (
            key in FILTER_KEYS
            or key.startswith("_last_selection_")
            or key.startswith(CHART_KEY_PREFIX)
        ):
            del st.session_state[key]
    st.query_params.clear()

for key, value in view_from_params(st.query_params).items():
    if key not in st.session_state:
        st.session_state[key] = value

pending = st.session_state.pop(PENDING_FILTERS, None)
if pending:
    category_pick = any(
        key != "flt_dates" and value for key, value in pending.items()
    )
    if category_pick:
        # A bar pick shows every day it was drawn from, so start it from the
        # full window instead of whatever single day the date chart left behind.
        pending["flt_dates"] = (metadata["min_date"], metadata["max_date"])
    for key, value in pending.items():
        st.session_state[key] = value

defaults = {
    "flt_dates": (metadata["min_date"], metadata["max_date"]),
    "flt_payments": [],
    "flt_zones": [],
    "flt_distances": [],
    "flt_dows": [],
    "flt_hours": [],
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

with st.expander("Filters", expanded=True):
    filter_cols = st.columns(3)
    with filter_cols[0]:
        date_value = st.date_input(
            "Pickup date range",
            min_value=metadata["min_date"],
            max_value=metadata["max_date"],
            key="flt_dates",
        )
    with filter_cols[1]:
        payment_value = st.multiselect(
            "Payment type",
            options=metadata["payments"],
            key="flt_payments",
        )
    with filter_cols[2]:
        distance_value = st.multiselect(
            "Distance bucket",
            options=metadata["distances"],
            key="flt_distances",
        )
    filter_cols_2 = st.columns(3)
    with filter_cols_2[0]:
        zone_value = st.multiselect(
            "Pickup zone",
            options=metadata["zones"],
            key="flt_zones",
        )
    with filter_cols_2[1]:
        dow_value = st.multiselect(
            "Day of week",
            options=metadata["dows"],
            format_func=lambda value: DOW_LABELS.get(int(value), str(value)),
            key="flt_dows",
        )
    with filter_cols_2[2]:
        hour_value = st.multiselect(
            "Hour of day",
            options=metadata["hours"],
            format_func=lambda value: f"{int(value):02d}:00",
            key="flt_hours",
        )
    st.caption(
        "Click any bar, point or row to cross-filter every chart. Click it again "
        "to clear that selection, or reset all filters. The address bar always "
        "holds the current view, so a filtered dashboard can be bookmarked or "
        "shared as a link."
    )
    if st.button("Reset all filters"):
        st.session_state[RESET_FLAG] = True
        st.rerun()

if isinstance(date_value, (tuple, list)):
    if len(date_value) == 2:
        start_date, end_date = date_value
    elif date_value:
        start_date = end_date = date_value[0]
    else:
        start_date, end_date = metadata["min_date"], metadata["max_date"]
else:
    start_date = end_date = date_value
if start_date > end_date:
    start_date, end_date = end_date, start_date

filters = {
    "start": start_date,
    "end": end_date,
    "payments": tuple(payment_value),
    "zones": tuple(zone_value),
    "distances": tuple(distance_value),
    "dows": tuple(dow_value),
    "hours": tuple(hour_value),
}
where, params = build_where(filters)
desired_params = params_from_filters(filters, metadata["min_date"], metadata["max_date"])
if {k: str(v) for k, v in st.query_params.items()} != {
    k: str(v) for k, v in desired_params.items()
}:
    st.query_params.clear()
    for key, value in desired_params.items():
        st.query_params[key] = value
active_labels = active_filter_labels(filters, metadata["min_date"], metadata["max_date"])
window = f"{start_date:%Y-%m-%d} to {end_date:%Y-%m-%d}"
scope = [label for label in active_labels if not label.startswith("Dates:")]
if scope:
    view_text = f"**Viewing:** {window} · " + " · ".join(scope)
else:
    view_text = f"**Viewing:** all trips, {window}"
labels_col, reset_col = st.columns([5, 1])
labels_col.markdown(view_text)
if active_labels:
    if reset_col.button("Reset filters", key="reset_filters_row"):
        st.session_state[RESET_FLAG] = True
        st.rerun()

kpi = query(
    "select "
    "coalesce(sum(trip_count), 0) as trips, "
    "coalesce(sum(total_revenue), 0) as total_revenue, "
    "case when coalesce(sum(fare_amount), 0) > 0 "
    "then 100.0 * sum(tip_amount) / sum(fare_amount) else 0 end as tip_pct "
    f"from gld_dashboard_facts{where}",
    params,
)
trips_value = int(kpi["trips"].iloc[0])
revenue_value = float(kpi["total_revenue"].iloc[0])
tip_value = float(kpi["tip_pct"].iloc[0])

left, mid, right = st.columns(3)
left.metric("Trips", f"{trips_value:,}")
mid.metric("Total charged", "$" + f"{revenue_value / 1_000_000:,.2f}" + "M")
right.metric("Tip rate (fare-weighted)", f"{tip_value:.2f}%")

st.divider()

ts_col, dow_col = st.columns([2, 1])
with ts_col:
    st.subheader("Trip volume over time")
    grain = st.radio(
        "Aggregation grain",
        ["Day", "Week", "Hour of day"],
        horizontal=True,
        label_visibility="collapsed",
        key="trip_grain",
    )
    grain_slug = grain.lower().replace(" ", "_")

    if grain == "Hour of day":
        trip_df = query(
            "select pickup_hour as bucket, sum(trip_count) as trip_count "
            f"from gld_dashboard_facts{where} group by 1 order by 1",
            params,
        )
    else:
        bucket = "pickup_date" if grain == "Day" else "date_trunc('week', pickup_date)"
        trip_df = query(
            f"select {bucket} as bucket, sum(trip_count) as trip_count "
            f"from gld_dashboard_facts{where} group by 1 order by 1",
            params,
        )

    if has_rows(trip_df, "Trip volume over time"):
        trip_selection = alt.selection_point(
            name="pick", fields=["bucket"], toggle=True
        )
        if grain == "Hour of day":
            trip_chart = (
                alt.Chart(trip_df)
                .mark_bar(cursor="pointer")
                .encode(
                    x=alt.X("bucket:O", title="Hour of day"),
                    y=alt.Y("trip_count:Q", title="Trips"),
                    tooltip=[
                        alt.Tooltip("bucket:O", title="Hour of day"),
                        alt.Tooltip("trip_count:Q", title="Trips", format=","),
                    ],
                )
                .add_params(trip_selection)
                .properties(height=320)
            )
            trip_caption = (
                "One row per hour of day, summed to the selected filters. "
                "The demand profile peaks at 18:00, with 17:00 just behind."
            )
        else:
            x_title = None
            x_axis = alt.Axis(format="%b %d", tickCount=12)
            line = (
                alt.Chart(trip_df)
                .mark_line(point=True, cursor="pointer")
                .encode(
                    x=alt.X("bucket:T", title=x_title, axis=x_axis),
                    y=alt.Y("trip_count:Q", title="Trips"),
                    tooltip=[
                        alt.Tooltip(
                            "bucket:T",
                            title="Pickup date" if grain == "Day" else "Week start",
                        ),
                        alt.Tooltip("trip_count:Q", title="Trips", format=","),
                    ],
                )
                .add_params(trip_selection)
            )
            chosen = []
            for _, row in trip_df.sort_values("trip_count", ascending=False).iterrows():
                if all(abs((row["bucket"] - c["bucket"]).days) > 9 for c in chosen):
                    chosen.append(row)
                if len(chosen) == 3:
                    break
            peak_labels = (
                alt.Chart(pd.DataFrame(chosen))
                .mark_text(align="left", dx=6, dy=-8, fontSize=11)
                .encode(
                    x=alt.X("bucket:T", title=None),
                    y=alt.Y("trip_count:Q"),
                    text=alt.Text("trip_count:Q", format=","),
                )
            )
            trip_chart = (line + peak_labels).properties(height=320)
            trip_caption = (
                "One row per pickup date; the line plots the selected grain "
                "directly from the gold cube."
                if grain == "Day"
                else "One row per ISO week start; the line plots the selected grain "
                "directly from the gold cube."
            )
        trip_event = st.altair_chart(
            trip_chart,
            width="stretch",
            on_select="rerun",
            selection_mode="pick",
            key=f"chart_trip_{grain_slug}",
        )
        st.caption(trip_caption)
        export_csv(
            trip_df,
            f"trip_volume_{grain_slug}.csv",
            "Export this view as CSV",
        )
        if grain == "Hour of day":
            sync_filter(
                f"chart_trip_{grain_slug}",
                "flt_hours",
                tuple(int(v) for v in event_values(trip_event, "pick", "bucket")),
                [],
            )
        else:
            sync_date_filter(
                f"chart_trip_{grain_slug}",
                event_values(trip_event, "pick", "bucket"),
                grain,
                metadata["min_date"],
                metadata["max_date"],
            )

with dow_col:
    st.subheader("Busiest day of week")
    dow_df = query(
        "select dow_iso, "
        "case dow_iso "
        "when 1 then 'Monday' when 2 then 'Tuesday' when 3 then 'Wednesday' "
        "when 4 then 'Thursday' when 5 then 'Friday' when 6 then 'Saturday' "
        "else 'Sunday' end as day_name, "
        "sum(trip_count) as trip_count "
        f"from gld_dashboard_facts{where} group by 1, 2 order by 1",
        params,
    )
    if has_rows(dow_df, "Busiest day of week"):
        dow_selection = alt.selection_point(
            name="pick", fields=["dow_iso"], toggle=True
        )
        dow_chart = (
            alt.Chart(dow_df)
            .mark_bar(cursor="pointer")
            .encode(
                x=alt.X(
                    "day_name:N",
                    title=None,
                    sort=dow_df["day_name"].tolist(),
                ),
                y=alt.Y("trip_count:Q", title="Trips"),
                tooltip=[
                    alt.Tooltip("day_name:N", title="Day"),
                    alt.Tooltip("trip_count:Q", title="Trips", format=","),
                ],
            )
            .add_params(dow_selection)
            .properties(height=320)
        )
        dow_event = st.altair_chart(
            dow_chart,
            width="stretch",
            on_select="rerun",
            selection_mode="pick",
            key="chart_dow",
        )
        st.caption("One row per ISO weekday. Click a bar to filter the dashboard.")
        export_csv(dow_df, "trips_by_day_of_week.csv", "Export this view as CSV")
        sync_filter(
            "chart_dow",
            "flt_dows",
            tuple(int(v) for v in event_values(dow_event, "pick", "dow_iso")),
            [],
        )

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top pickup zones")
    metric_label = st.radio(
        "Zone metric",
        ["Total revenue", "Average fare", "Trip count"],
        horizontal=True,
        label_visibility="collapsed",
        key="zone_metric",
    )
    top_n = st.slider("Zones shown", 5, 30, 15, key="zone_top_n")
    field, axis_title = {
        "Total revenue": ("total_revenue", "Revenue ($)"),
        "Average fare": ("avg_fare", "Average fare ($)"),
        "Trip count": ("trip_count", "Trips"),
    }[metric_label]
    zones = query(
        "select pickup_zone, sum(trip_count) as trip_count, "
        "sum(total_revenue) as total_revenue, "
        "round(sum(fare_amount) / nullif(sum(trip_count), 0), 2) as avg_fare "
        f"from gld_dashboard_facts{where} group by pickup_zone "
        f"order by {field} desc limit ?",
        params + (top_n,),
    )
    st.caption(f"One row per zone; top {top_n} by {metric_label.lower()}")
    if has_rows(zones, "Top pickup zones"):
        zone_selection = alt.selection_point(
            name="pick", fields=["pickup_zone"], toggle=True
        )
        zone_chart = (
            alt.Chart(zones)
            .mark_bar(cursor="pointer")
            .encode(
                x=alt.X(f"{field}:Q", title=axis_title),
                y=alt.Y(
                    "pickup_zone:N",
                    title=None,
                    sort="-x",
                    axis=alt.Axis(labelLimit=0, labelOverlap=False),
                ),
                tooltip=[
                    alt.Tooltip("pickup_zone:N", title="Zone"),
                    alt.Tooltip("trip_count:Q", title="Trips", format=","),
                    alt.Tooltip("total_revenue:Q", title="Revenue ($)", format=",.2f"),
                    alt.Tooltip("avg_fare:Q", title="Average fare ($)", format=".2f"),
                ],
            )
            .add_params(zone_selection)
            .properties(height=max(320, 24 * len(zones)))
        )
        zone_event = st.altair_chart(
            zone_chart,
            width="stretch",
            on_select="rerun",
            selection_mode="pick",
            key="chart_zones",
        )
        export_csv(zones, "top_zones.csv", "Export this view as CSV")
        sync_filter(
            "chart_zones",
            "flt_zones",
            tuple(str(v) for v in event_values(zone_event, "pick", "pickup_zone")),
            [],
        )

with col2:
    st.subheader("Tip rate by trip distance")
    st.caption("One row per distance bucket, fare-weighted")
    tip_where = where + " and fare_amount > 0"
    tips = query(
        "select distance_bucket, "
        "round(100.0 * sum(tip_amount) / nullif(sum(fare_amount), 0), 2) as tip_pct "
        f"from gld_dashboard_facts{tip_where} group by 1 "
        "order by case distance_bucket "
        "when '0-1 mi' then 1 when '1-3 mi' then 2 when '3-5 mi' then 3 "
        "when '5-10 mi' then 4 else 5 end",
        params,
    )
    if has_rows(tips, "Tip rate by trip distance"):
        tips_selection = alt.selection_point(
            name="pick", fields=["distance_bucket"], toggle=True
        )
        tips_chart = (
            alt.Chart(tips)
            .mark_bar(cursor="pointer")
            .encode(
                x=alt.X(
                    "distance_bucket:N",
                    title=None,
                    sort=tips["distance_bucket"].tolist(),
                ),
                y=alt.Y("tip_pct:Q", title="Tip rate (%)"),
                tooltip=[
                    alt.Tooltip("distance_bucket:N", title="Distance"),
                    alt.Tooltip("tip_pct:Q", title="Tip rate (%)", format=".2f"),
                ],
            )
            .add_params(tips_selection)
            .properties(height=320)
        )
        tips_event = st.altair_chart(
            tips_chart,
            width="stretch",
            on_select="rerun",
            selection_mode="pick",
            key="chart_tips",
        )
        if not (tips["tip_pct"].fillna(0) > 0).any():
            st.caption(
                "Every bar is zero because cash trips record no tip: the TLC "
                "does not capture cash tips."
            )
        export_csv(tips, "tip_by_distance.csv", "Export this view as CSV")
        sync_filter(
            "chart_tips",
            "flt_distances",
            tuple(str(v) for v in event_values(tips_event, "pick", "distance_bucket")),
            [],
        )

col3, col4 = st.columns([3, 2])

with col3:
    st.subheader("Payment mix")
    st.caption("One row per payment type")
    payments = query(
        "select payment_type, sum(trip_count) as trip_count, "
        "round(100.0 * sum(trip_count) / sum(sum(trip_count)) over (), 2) "
        "as trip_share_pct, "
        "round(sum(fare_amount) / nullif(sum(trip_count), 0), 2) as avg_fare, "
        "round(100.0 * sum(tip_amount) / nullif(sum(fare_amount), 0), 2) as tip_pct "
        f"from gld_dashboard_facts{where} group by payment_type "
        "order by trip_count desc",
        params,
    )
    if has_rows(payments, "Payment mix"):
        payment_selection = alt.selection_point(
            name="pick", fields=["payment_type"], toggle=True
        )
        pay_chart = (
            alt.Chart(payments)
            .mark_bar(cursor="pointer")
            .encode(
                x=alt.X(
                    "payment_type:N",
                    title=None,
                    sort=payments["payment_type"].tolist(),
                ),
                y=alt.Y("trip_count:Q", title="Trips"),
                tooltip=[
                    alt.Tooltip("payment_type:N", title="Payment type"),
                    alt.Tooltip("trip_count:Q", title="Trips", format=","),
                    alt.Tooltip(
                        "trip_share_pct:Q",
                        title="Share of trips (%)",
                        format=".2f",
                    ),
                ],
            )
            .add_params(payment_selection)
            .properties(height=300)
        )
        pay_event = st.altair_chart(
            pay_chart,
            width="stretch",
            on_select="rerun",
            selection_mode="pick",
            key="chart_payments",
        )
        export_csv(payments, "payment_analysis.csv", "Export this view as CSV")
        sync_filter(
            "chart_payments",
            "flt_payments",
            tuple(str(v) for v in event_values(pay_event, "pick", "payment_type")),
            [],
        )

with col4:
    st.subheader("Payment behaviour")
    st.caption("Same gold row, behaviour columns; select a row to filter")
    if has_rows(payments, "Payment behaviour"):
        display = payments.assign(
            Trips=payments.trip_count.map(lambda v: f"{v:,}"),
            Share=payments.trip_share_pct.map(lambda v: f"{v:.2f}%"),
            AvgFare=payments.avg_fare.map(lambda v: "$" + f"{v:,.2f}"),
            Tip=payments.tip_pct.map(lambda v: f"{v:.2f}%"),
        )[["payment_type", "Trips", "Share", "AvgFare", "Tip"]].rename(
            columns={"payment_type": "Payment type", "AvgFare": "Avg fare"}
        )
        table_event = st.dataframe(
            display,
            hide_index=True,
            width="stretch",
            on_select="rerun",
            selection_mode="multi-row",
            key="chart_payment_behaviour",
        )
        rows = event_rows(table_event)
        selected_payments = tuple(
            str(payments.iloc[row]["payment_type"])
            for row in rows
            if 0 <= row < len(payments)
        )
        sync_filter(
            "chart_payment_behaviour",
            "flt_payments",
            selected_payments,
            [],
        )

st.divider()
st.caption(
    "Built with dbt + DuckDB. Filters apply to the KPI strip, every chart and "
    "every CSV export. Gold grain, tests and trade-offs: README.md."
)