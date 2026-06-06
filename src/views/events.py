from __future__ import annotations

import pandas as pd
import streamlit as st

from src.events import list_public_events
from src.ui_components import show_header


def status_label(event: dict) -> str:
    if event.get("registration_open", False):
        return "Registration open"
    return "Registration closed"


def render() -> None:
    show_header("SRCS Events", "Championship rounds, one-off events, endurance races and intake events")

    events = list_public_events()

    if not events:
        st.info("No public events available yet.")
        return

    rows = []

    for event in events:
        event_id = event.get("event_id", "")
        event_url = f"?mode=event&event_id={event_id}"
        register_url = f"?mode=register&event_id={event_id}"

        rows.append(
            {
                "Event": event.get("event_name", ""),
                "Category": event.get("category", ""),
                "Type": event.get("event_type", ""),
                "Date": event.get("event_date", ""),
                "Track": event.get("track", ""),
                "Registration": status_label(event),
                "Event URL": event_url,
                "Register URL": register_url if event.get("registration_open", False) else "",
            }
        )

    df = pd.DataFrame(rows)

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Event quick links")

    for event in events:
        event_id = event.get("event_id", "")
        event_name = event.get("event_name", "Unnamed event")
        category = event.get("category", "")
        event_type = event.get("event_type", "")
        event_date = event.get("event_date", "")

        with st.container(border=True):
            st.markdown(f"### {event_name}")
            st.write(f"**Category:** {category}")
            st.write(f"**Type:** {event_type}")
            st.write(f"**Date:** {event_date}")
            st.write(f"**Track:** {event.get('track', '')}")
            st.write(f"**Registration:** {status_label(event)}")

            st.code(f"?mode=event&event_id={event_id}")

            if event.get("registration_open", False):
                st.markdown("Registration link:")
                st.code(f"?mode=register&event_id={event_id}")