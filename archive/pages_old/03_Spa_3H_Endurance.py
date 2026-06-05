from __future__ import annotations

import streamlit as st

from src.data_loader import load_json
from src.registrations import load_confirmed_spa_entries
from src.ui_components import show_header

st.set_page_config(page_title="SRCS Spa 3-hour Endurance", layout="wide")
show_header("The SRCS Spa 3-hour Endurance", "GT3 team event — registration-ready module")

event = load_json("data/events/spa_3h_endurance/event.json", default={})

left, right = st.columns(2)
with left:
    st.subheader("Event format")
    st.write(f"**Track:** {event.get('track', 'TBC')}")
    st.write(f"**Duration:** {event.get('duration_minutes', 0)} minutes")
    st.write(f"**Drivers per car:** {event.get('drivers_per_car', 2)}")
    st.write("**Cars:** " + ", ".join(event.get("car_choices", [])))

with right:
    st.subheader("Race settings")
    for key, value in event.get("settings", {}).items():
        st.write(f"{'✅' if value else '❌'} {key.replace('_', ' ').title()}")

st.divider()
st.subheader("Confirmed entries")
entries = load_confirmed_spa_entries()
if entries:
    st.dataframe(entries, use_container_width=True, hide_index=True)
else:
    st.info("No confirmed entries yet.")
