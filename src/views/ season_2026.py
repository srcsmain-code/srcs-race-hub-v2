from __future__ import annotations

import streamlit as st

from src.ui_components import show_header


def render() -> None:
    show_header("SRCS Grand Prix Season 2026", "Season calendar and championship overview")

    st.markdown(
        """
        Race Hub v2 season page.

        This page will be rebuilt with the official 2026 SRCS calendar, event details, and round links.
        """
    )