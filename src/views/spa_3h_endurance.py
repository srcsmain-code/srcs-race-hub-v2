from __future__ import annotations

import pandas as pd
import streamlit as st

from src.events import load_event
from src.github_writer import github_configured, list_registrations
from src.ui_components import show_header


DEFAULT_EVENT_ID = "2026_spa_3h_endurance"


def render_confirmed_entries(event_id: str) -> None:
    st.subheader("Confirmed entries")

    if not github_configured():
        st.info("Confirmed entries are not available yet.")
        return

    try:
        approved = list_registrations(event_id, "approved")
    except Exception:
        st.warning("Confirmed entries could not be loaded right now.")
        return

    if not approved:
        st.info("No confirmed teams yet.")
        return

    rows = []

    for index, item in enumerate(approved, start=1):
        rows.append(
            {
                "#": index,
                "Team": item.get("team_name", ""),
                "Car": item.get("car_choice", ""),
                "Driver 1": item.get("driver_1_name", ""),
                "Driver 2": item.get("driver_2_name", ""),
                "Experience": item.get("experience", ""),
            }
        )

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.caption(
        "Confirmed entries are updated after SRCS admin approval. "
        "Car choice may still be subject to final balancing or event-admin confirmation."
    )


def render() -> None:
    event_id = st.query_params.get("event_id", DEFAULT_EVENT_ID)
    event = load_event(event_id)

    show_header(event.get("event_name", "SRCS Event"), event.get("description", ""))

    st.markdown(
        f"""
        **Event information**

        - Category: {event.get("category", "")}
        - Type: {event.get("event_type", "")}
        - Track: {event.get("track", "")}
        - Venue: {event.get("venue", "")}
        - Date: {event.get("event_date", "")}
        - Registration open: {event.get("registration_open", False)}
        """
    )

    if event.get("event_id") == "2026_spa_3h_endurance":
        st.markdown(
            """
            **Format**

            - 2 drivers per team/car
            - Cars: Porsche, Mercedes, Lamborghini, Ferrari
            - Tire wear: On
            - Pitstops: On
            - Collision: On
            - Penalties: On
            - Damage: On
            - Race duration: 3 hours
            - 24h setting: day-night-day
            - Track: Spa-Francorchamps
            """
        )

    st.divider()
    render_confirmed_entries(event_id)

    st.divider()
    st.subheader("Registration")

    if event.get("registration_open", False):
        st.markdown(
            f"""
            Registration is open for this event.

            Use registration mode with:

            `?mode=register&event_id={event_id}`
            """
        )
    else:
        st.info("Registration is currently closed for this event.")