from __future__ import annotations

import pandas as pd
import streamlit as st

from src.github_writer import github_configured, list_approved_spa_3h_registrations
from src.ui_components import show_header


def render_confirmed_entries() -> None:
    st.subheader("Confirmed entries")

    if not github_configured():
        st.info("Confirmed entries are not available yet.")
        return

    try:
        approved = list_approved_spa_3h_registrations()
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
    show_header("The SRCS Spa 3-hour Endurance", "GT3 team endurance event")

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

        Registration is handled through the Spa 3H registration form.
        """
    )

    st.divider()
    render_confirmed_entries()

    st.divider()
    st.subheader("Registration")

    st.markdown(
        """
        Teams can register through the dedicated Spa 3H registration form.

        After submission, the entry is reviewed by SRCS admin before being added to the confirmed entry list.
        """
    )