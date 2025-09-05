import streamlit as st
import pandas as pd
import datetime
import random
from collections import Counter

APP_VERSION = "ResQNet_v3_Advanced"
STARTED_AT = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

st.set_page_config(page_title=f"{APP_VERSION} - {STARTED_AT}", layout="wide")
st.markdown(f"## 🚨 {APP_VERSION}")
st.caption(f"Started at: {STARTED_AT}")

if "incidents" not in st.session_state:
    st.session_state.incidents = []
if "helpers" not in st.session_state:
    st.session_state.helpers = [
        {"name":"Aarav","points":0,"streak":0},
        {"name":"Neha","points":0,"streak":0},
        {"name":"Riya","points":0,"streak":0},
        {"name":"Vikram","points":0,"streak":0},
    ]
if "simulate_id" not in st.session_state:
    st.session_state.simulate_id = 0

def score_incident(itype, urgency):
    weights = {"Medical Emergency":3, "Flood":2, "Roadblock":1}
    return weights.get(itype, urgency)

def severity_label(s):
    return "🔴 High" if s==3 else ("🟠 Medium" if s==2 else "🟢 Low")

def icon(itype):
    return {"Medical Emergency":"🩺","Flood":"🌊","Roadblock":"🚧"}.get(itype,"⚠️")

def add_incident(name, itype, location, urgency):
    severity = score_incident(itype, urgency)
    base_lat = 28.61 + (hash(location) % 100)/2000.0
    base_lon = 77.23 + (hash(location[::-1]) % 100)/2000.0
    lat = base_lat + random.uniform(-0.02, 0.02)
    lon = base_lon + random.uniform(-0.02, 0.02)
    inc = {
        "id": f"INC{len(st.session_state.incidents)+1}_{st.session_state.simulate_id}",
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "reporter": name or "Anonymous",
        "type": itype,
        "location": location or "(no address)",
        "lat": lat, "lon": lon,
        "severity": severity,
        "status": "Pending"
    }
    st.session_state.incidents.append(inc)

def award_points(name, pts):
    for h in st.session_state.helpers:
        if h["name"] == name:
            h["points"] += pts
            h["streak"] += 1
            if h["streak"] % 3 == 0:
                h["points"] += 5

def rank(p):
    if p>=60:
        return "🏅 Hero"
    if p>=40:
        return "🥇 Gold"
    if p>=20:
        return "🥈 Silver"
    if p>=10:
        return "🥉 Bronze"
    return "🤍 Newbie"

st.sidebar.header("🧑‍🤝‍🧑 Citizen Report (Demo)")
with st.sidebar.form("report"):
    rname = st.text_input("Your name")
    rtype = st.selectbox("Type", ["Medical Emergency","Flood","Roadblock","Other"])
    rloc = st.text_input("Location (text)")
    rurg = st.slider("Urgency",1,3,2)
    if st.form_submit_button("Report"):
        add_incident(rname, rtype, rloc, rurg)
        st.sidebar.success("Reported ✔️")

if st.sidebar.checkbox("Auto-refresh (10s)"):
    st.experimental_autorefresh(interval=10_000, key="auto_refresh")

tab1, tab2, tab3, tab4 = st.tabs(["Dashboard","Admin","Leaderboard","Drill"])

with tab1:
    st.subheader("📋 Dashboard")
    if not st.session_state.incidents:
        st.info("No incidents — try reporting from the left or run a Drill.")
    else:
        df = pd.DataFrame(st.session_state.incidents)
        df_sorted = df.sort_values(by=["severity","time"], ascending=[False, True])
        for i, row in df_sorted.iterrows():
            c1,c2,c3,c4 = st.columns([1.2,3,2,2])
            c1.write(icon(row["type"]))
            c2.markdown(f"**{row['type']}** — {row['location']}")
            c3.markdown(f"Severity: **{severity_label(row['severity'])}**  \nReported: {row['time']}")
            c4.markdown(f"Status: **{row['status']}**")
            if row["status"] == "Pending":
                if c4.button("Resolve", key=f"resolve_{row['id']}"):
                    for inc in st.session_state.incidents:
                        if inc["id"] == row["id"]:
                            inc["status"] = "Resolved"
                            award_points("Responder", 15)
                            st.success("Marked Resolved — Responder +15 pts")
                            break
        st.subheader("Map (pins)")
        st.map(pd.DataFrame([{"lat":i["lat"], "lon":i["lon"]} for i in st.session_state.incidents]))

with tab2:
    st.subheader("🛠 Admin")
    df = pd.DataFrame(st.session_state.incidents) if st.session_state.incidents else pd.DataFrame()
    st.dataframe(df)
    if not df.empty:
        st.metric("Total incidents", len(df))
        st.metric("Pending", sum(df["status"]=="Pending"))
        st.metric("Resolved", sum(df["status"]=="Resolved"))
        st.markdown("**Type distribution**")
        st.bar_chart(pd.Series(df["type"].value_counts()))

with tab3:
    st.subheader("🏆 Helpers Leaderboard")
    helpers_sorted = sorted(st.session_state.helpers, key=lambda x: x["points"], reverse=True)
    for h in helpers_sorted:
        st.write(f"{h['name']} — {h['points']} pts — {rank(h['points'])} — streak: {h['streak']}")

with tab4:
    st.subheader("🎭 Drill Mode")
    if st.button("Launch Full Drill (50 incidents)"):
        st.session_state.simulate_id += 1
        for _ in range(50):
            add_incident(random.choice(["Ravi","Ananya","Local"]), random.choice(["Medical Emergency","Flood","Roadblock"]), random.choice(["Market","Highway","Colony","Hospital"]), random.randint(1,3))
        st.success("Drill launched: 50 incidents generated")