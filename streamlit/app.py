"""NYC Yellow Taxi dashboard: Q1 2024, one view per gold model."""

from pathlib import Path

import altair as alt
import duckdb
import pandas as pd
import streamlit as st

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "nyc_taxi.duckdb"

st.set_page_config(page_title="NYC Yellow Taxi - Q1 2024", layout="wide")


@st.cache_data(ttl=600, show_spinner=False)
def query(sql: str) -> pd.DataFrame:
    """Read gold tables. read_only lets dbt rebuild while the app stays open."""
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        return con.execute(sql).df()


def has_rows(df: pd.DataFrame, label: str) -> bool:
    """Warn instead of drawing an empty chart when a gold table has no rows."""
    if df.empty:
        st.warning(f"{label} returned no rows. Run dbt build, then reload this page.")
        return False
    return True


def export_csv(df: pd.DataFrame, filename: str, label: str) -> None:
    """Download exactly the frame the chart was drawn from."""
    st.download_button(
        label=label,
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        key=filename,
    )


if not DB_PATH.exists():
    st.error("No DuckDB file yet. Run: cd dbt_project; dbt build --profiles-dir .")
    st.stop()

st.title("NYC Yellow Taxi - Q1 2024")
st.caption(
    "dbt bronze -> silver -> gold on DuckDB. Source: NYC TLC trip records "
    "(January-March 2024) and the taxi zone lookup. Every number below is read "
    "from a gold model; this page only renders."
)

kpi = query("select trips, total_revenue, tip_pct from gld_trip_summary")
if not has_rows(kpi, "gld_trip_summary"):
    st.stop()

trips = int(kpi.trips[0])
revenue = "$" + f"{kpi.total_revenue[0] / 1_000_000:,.2f}" + "M"
tip_rate = f"{kpi.tip_pct[0]:.2f}%"

left, mid, right = st.columns(3)
left.metric("Trips", f"{trips:,}")
mid.metric("Total charged", revenue)
right.metric("Tip rate (fare-weighted)", tip_rate)

st.divider()

st.subheader("Trip volume over time")
grain = st.radio(
    "Aggregation grain",
    ["Day", "Week", "Hour of day"],
    horizontal=True,
    label_visibility="collapsed",
)

if grain == "Hour of day":
    df = query(
        "select pickup_hour as bucket, trip_count from gld_trips_hourly order by pickup_hour"
    )
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("bucket:O", title="Hour of day"),
            y=alt.Y("trip_count:Q", title="Trips"),
            tooltip=[
                alt.Tooltip("bucket:O", title="Hour"),
                alt.Tooltip("trip_count:Q", format=","),
            ],
        )
        .properties(height=320)
    )
    caption = (
        "gld_trips_hourly - one row per hour of day (0-23), summed across the "
        "quarter. This is the demand profile: the peak sits at 17:00-18:00."
    )
    label = "gld_trips_hourly"
else:
    table = "gld_trips_daily" if grain == "Day" else "gld_trips_weekly"
    date_col = "pickup_date" if grain == "Day" else "week_start"
    df = query(f"select {date_col} as bucket, trip_count from {table} order by 1")
    chart = (
        alt.Chart(df)
        .mark_line(point=(grain == "Week"))
        .encode(
            x=alt.X("bucket:T", title=None, axis=alt.Axis(format="%b %d", tickCount=12)),
            y=alt.Y("trip_count:Q", title="Trips"),
            tooltip=[
                alt.Tooltip("bucket:T", title=date_col),
                alt.Tooltip("trip_count:Q", format=","),
            ],
        )
        .properties(height=320)
    )
    unit = "pickup date" if grain == "Day" else "ISO week start (Monday)"
    caption = f"{table} - one row per {unit}; the line plots that grain directly."
    label = table
    peaks = df.nlargest(3, "trip_count")
    peak_labels = (
        alt.Chart(peaks)
        .mark_text(align="left", dx=6, dy=-8, fontSize=11, color="#1f4e79")
        .encode(
            x=alt.X("bucket:T", title=None),
            y=alt.Y("trip_count:Q"),
            text=alt.Text("trip_count:Q", format=","),
        )
    )
    chart = chart + peak_labels

if has_rows(df, label):
    st.altair_chart(chart, width="stretch")
    st.caption(caption)
    export_csv(df, f"trip_volume_{label}.csv", "Export this view as CSV")

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
    st.caption(
        f"gld_revenue_by_zone - one row per zone; top {top_n} by {metric_label.lower()}"
    )
    zones = query(
        "select pickup_zone, trip_count, total_revenue, avg_fare from gld_revenue_by_zone "
        f"order by {field} desc limit {top_n}"
    )
    if has_rows(zones, "gld_revenue_by_zone"):
        zone_chart = (
            alt.Chart(zones)
            .mark_bar()
            .encode(
                x=alt.X(f"{field}:Q", title=axis_title),
                y=alt.Y("pickup_zone:N", title=None, sort="-x", axis=alt.Axis(labelLimit=0)),
                tooltip=[
                    alt.Tooltip("pickup_zone:N", title="Zone"),
                    alt.Tooltip("trip_count:Q", format=","),
                    alt.Tooltip("total_revenue:Q", format=",.2f"),
                    alt.Tooltip("avg_fare:Q", format=".2f"),
                ],
            )
            .properties(height=320)
        )
        st.altair_chart(zone_chart, width="stretch")
        export_csv(zones, "top_zones.csv", "Export this view as CSV")

with col2:
    st.subheader("Tip rate by trip distance")
    st.caption("gld_tip_behavior - one row per distance bucket, fare-weighted")
    tips = query("select distance_bucket, tip_pct from gld_tip_behavior")
    if has_rows(tips, "gld_tip_behavior"):
        st.bar_chart(tips.set_index("distance_bucket")["tip_pct"], sort=False, height=320)
        export_csv(tips, "tip_by_distance.csv", "Export this view as CSV")

col3, col4 = st.columns([3, 2])

with col3:
    st.subheader("Payment mix")
    st.caption("gld_payment_analysis - one row per payment type")
    payments = query(
        "select payment_type, trip_count, trip_share_pct, avg_fare, tip_pct "
        "from gld_payment_analysis order by trip_count desc"
    )
    if has_rows(payments, "gld_payment_analysis"):
        st.bar_chart(payments.set_index("payment_type")["trip_count"], sort=False, height=300)
        export_csv(payments, "payment_analysis.csv", "Export this view as CSV")

with col4:
    st.subheader("Payment behaviour")
    st.caption("same gold row, behaviour columns")
    if has_rows(payments, "gld_payment_analysis"):
        display = payments.assign(
            Trips=payments.trip_count.map(lambda v: f"{v:,}"),
            Share=payments.trip_share_pct.map(lambda v: f"{v:.2f}%"),
            AvgFare=payments.avg_fare.map(lambda v: "$" + f"{v:,.2f}"),
            Tip=payments.tip_pct.map(lambda v: f"{v:.2f}%"),
        )[["payment_type", "Trips", "Share", "AvgFare", "Tip"]].rename(
            columns={"payment_type": "Payment type", "AvgFare": "Avg fare"}
        )
        st.dataframe(display, hide_index=True, width="stretch")

st.divider()
st.caption(
    "Built with dbt + DuckDB. Gold grain, tests and trade-offs: README.md. "
    "Decisions and tool choices: prompts.txt."
)
