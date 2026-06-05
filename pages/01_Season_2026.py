from __future__ import annotations

import pandas as pd
import streamlit as st

from src.data_loader import load_json
from src.ui_components import show_header

st.set_page_config(page_title="SRCS 2026 Season", layout="wide")
show_header("SRCS 2026 Season", "Calendar and race structure")

calendar = load_json("data/championships/2026/season_calendar.json", default=[])
if calendar:
    st.dataframe(pd.DataFrame(calendar), use_container_width=True, hide_index=True)
else:
    st.warning("No season calendar data found yet.")
