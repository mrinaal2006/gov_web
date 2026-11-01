import sqlite3
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
import pydeck as pdk
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))
from hotspots import village_spikes
from score import DB, score_complaint

st.set_page_config(page_title="Samasya Radar", layout="wide")

PORTAL_DB = Path(__file__).resolve().parents[1] / "portal" / "portal.db"

@st.cache_data(ttl=30)
def load():
    with sqlite3.connect(DB) as con:
        df = pd.read_sql("select * from complaints", con,
                         parse_dates=["received_at", "resolved_at"])
    if not PORTAL_DB.exists():
        return df
    # Complaints filed on the local website, leaving out its copy of the simulated data
    with sqlite3.connect(PORTAL_DB) as con:
        web = pd.read_sql("select id as complaint_id, text, language, channel, received_at, resolved_at, district, "
                          "block, village, lat, lon, department, urgency from complaints "
                          "where id not like 'DEMO-%'", con)
    local = datetime.now().astimezone().tzinfo
    for col in ["received_at", "resolved_at"]:
        web[col] = pd.to_datetime(web[col], utc=True).dt.tz_convert(local).dt.tz_localize(None)
    return pd.concat([df, web], ignore_index=True) if len(web) else df

df = load()
now = pd.Timestamp.now()
st.title("Samasya Radar: District Dashboard")

depts = sorted(df.department.dropna().unique())
pick = st.sidebar.multiselect("Department", depts, default=depts)
days = st.sidebar.slider("Last N days", 7, 90, 30)
view = df[df.department.isin(pick) & (df.received_at >= now - pd.Timedelta(days=days))]
pending = view.resolved_at.isna() | (view.resolved_at > now)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Complaints", len(view))
c2.metric("High urgency (70+)", int((view.urgency >= 70).sum()))
c3.metric("Pending", int(pending.sum()))
c4.metric("Avg days to resolve",
          f"{(view.resolved_at - view.received_at).dt.days[~pending].mean():.1f}")

st.subheader("Hotspot alerts (last 48 hours)")
spikes = village_spikes(view[view.received_at >= now - pd.Timedelta(hours=48)])
if spikes.empty:
    st.success("No hotspots right now")
else:
    st.error(f"{len(spikes)} hotspot(s) need attention")
    st.dataframe(spikes.sort_values("peak_count", ascending=False))

st.subheader("Complaint heat map")
pts = view.dropna(subset=["lat", "lon"])
st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(latitude=pts.lat.mean(), longitude=pts.lon.mean(), zoom=9),
    layers=[pdk.Layer("HeatmapLayer", data=pts, get_position="[lon, lat]", get_weight="urgency")]))

st.subheader("Latest complaints")
st.dataframe(view.sort_values("received_at", ascending=False)
             [["complaint_id", "text", "department", "village", "block", "urgency", "received_at"]]
             .head(10))

st.subheader("Priority list: pending, most urgent first")
st.dataframe(view[pending].sort_values("urgency", ascending=False)
             [["complaint_id", "text", "department", "village", "block", "urgency", "received_at"]]
             .head(25))

st.subheader("Department scorecard")
card = (view.assign(days_taken=(view.resolved_at - view.received_at).dt.days)
            .groupby(["block", "department"])
            .agg(complaints=("complaint_id", "count"),
                 avg_days=("days_taken", "mean"),
                 high_urgency=("urgency", lambda s: int((s >= 70).sum())))
            .round(1).sort_values("avg_days", ascending=False))
st.dataframe(card)
st.line_chart(view.set_index("received_at").resample("D").size())

st.sidebar.subheader("Try a complaint")
text = st.sidebar.text_area("Type in Bengali, English or Banglish")
if st.sidebar.button("Analyse") and text.strip():
    st.session_state.result = score_complaint(text)
    st.cache_data.clear()
    st.rerun()  # redraw from the top so a new hotspot shows at once
if "result" in st.session_state:
    r = st.session_state.result
    st.sidebar.write(f"Department: **{r['department']}** ({r['confidence']:.0%})")
    st.sidebar.write(f"Place: **{r['village'] or 'not found'}**")
    st.sidebar.write(f"Urgency: **{r['urgency']}/100**")
