from __future__ import annotations

import streamlit as st

from src.data_loader import load_json
from src.standings import calculate_driver_standings
from src.ui_components import show_header

st.set_page_config(page_title="SRCS Standings", layout="wide")
show_header("SRCS Standings", "Driver standings generated from result files")

results = load_json("data/results/2026/results.json", default=[])
standings = calculate_driver_standings(results)

if standings.empty:
    st.info("No result data loaded yet. Add race result JSON files to populate standings.")
else:
    st.dataframe(standings, use_container_width=True, hide_index=True)
