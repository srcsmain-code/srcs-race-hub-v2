from __future__ import annotations

import streamlit as st

from src.ui_components import show_header


def render() -> None:
    show_header("SRCS Standings", "Drivers and teams championship tables")

    st.markdown(
        """
        Standings module placeholder.

        The next version will connect to the existing 2026 results JSON files and standings logic.
        """
    )
