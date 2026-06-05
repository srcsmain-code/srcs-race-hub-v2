from __future__ import annotations

import json
from pathlib import Path
import streamlit as st

from src.ui_components import show_header

st.set_page_config(page_title="SRCS Admin", layout="wide")
show_header("SRCS Admin", "Pending submissions review — starter version")

pending_dir = Path("data/registrations/pending/spa_3h_endurance")
files = sorted(pending_dir.glob("*.json")) if pending_dir.exists() else []

st.subheader("Pending Spa 3H registrations")
if not files:
    st.info("No pending registration files found.")
else:
    for file in files:
        with file.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        with st.expander(payload.get("team_name", file.name)):
            st.json(payload)
            st.caption("Approval workflow will be added in the next build step.")
