from __future__ import annotations

import streamlit as st

from src.ui_components import show_header


def render() -> None:
    show_header("SRCS Race Hub v2", "Public hub + operational backbone")

    st.markdown(
        """
        Welcome to the clean Race Hub v2.

        This rebuild separates the public Race Hub from the operational/admin layer:

        - Public pages: standings, season calendar, endurance events, entry lists.
        - Input pages: registrations, rookie intake, attendance confirmations.
        - Admin pages: pending submissions, approvals, classification, event management.
        - Data layer: JSON-first for now, GitHub/database-ready later.
        """
    )