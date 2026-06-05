from __future__ import annotations

import streamlit as st

from src.ui_components import show_header


def render() -> None:
    show_header("SRCS Rookie Intake", "Lead generation and new driver intake")

    st.markdown(
        """
        Rookie intake form placeholder.

        This will support the Race Square / SRCS lead generation pilot and new-driver onboarding flow.
        """
    )