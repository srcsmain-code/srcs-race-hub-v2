from __future__ import annotations

import streamlit as st

from config.settings import APP_NAME, APP_VERSION
from src.ui_components import show_header

st.set_page_config(
    page_title=APP_NAME,
    page_icon="assets/logos/srcs_favicon_256.png",
    layout="wide",
)

show_header("SRCS Race Hub v2", "Clean rebuild starter — public hub + operational backbone")

st.markdown(
    """
Welcome to the clean Race Hub v2 starter.

This rebuild separates the public Race Hub from the operational/admin layer:

- Public pages: standings, season calendar, endurance events, entry lists.
- Input pages: registrations, rookie intake, attendance confirmations.
- Admin pages: pending submissions, approvals, classification, event management.
- Data layer: JSON-first for now, GitHub/database-ready later.

Use the sidebar to open the starter pages.
"""
)

st.info(f"Version: {APP_VERSION}")
