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
    hourly = query(
        "select pickup_hour as bucket, trip_count from gld_trips_hourly order by pickup_hour"
    )
    chart = (
        alt.Chart(hourly)
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
else:
    table = "gld_trips_daily" if grain == "Day" else "gld_trips_weekly"
    date_col = "pickup_date" if grain == "Day" else "week_start"
    series = query(f"select {date_col} as bucket, trip_count from {table} order by 1")
    chart = (
        alt.Chart(series)
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

st.altair_chart(chart, width="stretch")
st.caption(caption)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 pickup zones by revenue")
    st.caption("gld_revenue_by_zone - one row per zone; top 10 sliced here")
    zones = query(
        "select pickup_zone, total_revenue from gld_revenue_by_zone "
        "order by total_revenue desc limit 10"
    )
    zone_chart = (
        alt.Chart(zones)
        .mark_bar()
        .encode(
            x=alt.X("total_revenue:Q", title="Revenue ($)"),
            y=alt.Y("pickup_zone:N", title=None, sort="-x", axis=alt.Axis(labelLimit=0)),
        )
        .properties(height=320)
    )
    st.altair_chart(zone_chart, width="stretch")

with col2:
    st.subheader("Tip rate by trip distance")
    st.caption("gld_tip_behavior - one row per distance bucket, fare-weighted")
    tips = query("select distance_bucket, tip_pct from gld_tip_behavior")
    st.bar_chart(tips.set_index("distance_bucket")["tip_pct"], sort=False, height=320)

col3, col4 = st.columns([3, 2])

with col3:
    st.subheader("Payment mix")
    st.caption("gld_payment_analysis - one row per payment type")
    payments = query(
        "select payment_type, trip_count, trip_share_pct, avg_fare, tip_pct "
        "from gld_payment_analysis order by trip_count desc"
    )
    st.bar_chart(payments.set_index("payment_type")["trip_count"], sort=False, height=300)

with col4:
    st.subheader("Payment behaviour")
    st.caption("same gold row, behaviour columns")
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
