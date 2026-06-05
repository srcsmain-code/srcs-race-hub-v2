from __future__ import annotations

import pandas as pd
import streamlit as st

from src.github_writer import github_configured, list_pending_spa_3h_registrations
from src.ui_components import show_header


def render() -> None:
    show_header("Race Hub Admin", "Pending submissions and operational review")

    if not github_configured():
        st.error("GitHub storage is not configured. Check Streamlit secrets.")
        st.stop()

    tab_spa, tab_notes = st.tabs(["Spa 3H Pending Registrations", "Admin Notes"])

    with tab_spa:
        st.subheader("Pending Spa 3H registrations")

        if st.button("Refresh pending registrations"):
            st.rerun()

        try:
            registrations = list_pending_spa_3h_registrations()
        except Exception as exc:
            st.error("Could not load pending registrations from GitHub.")
            st.exception(exc)
            st.stop()

        if not registrations:
            st.info("No pending Spa 3H registrations found yet.")
        else:
            table_rows = []

            for item in registrations:
                table_rows.append(
                    {
                        "Submitted UTC": item.get("submitted_at_utc", ""),
                        "Team": item.get("team_name", ""),
                        "Preferred Car": item.get("car_choice", ""),
                        "Backup Car": item.get("backup_car_choice", ""),
                        "Driver 1": item.get("driver_1_name", ""),
                        "Driver 1 Email": item.get("driver_1_email", ""),
                        "Driver 1 Phone": item.get("driver_1_phone", ""),
                        "Driver 2": item.get("driver_2_name", ""),
                        "Driver 2 Email": item.get("driver_2_email", ""),
                        "Driver 2 Phone": item.get("driver_2_phone", ""),
                        "Experience": item.get("experience", ""),
                        "Status": item.get("status", ""),
                        "GitHub Path": item.get("_github_path", ""),
                    }
                )

            df = pd.DataFrame(table_rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.download_button(
                label="Download pending registrations as CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="spa_3h_pending_registrations.csv",
                mime="text/csv",
            )

            st.divider()
            st.subheader("Registration details")

            selected_team = st.selectbox(
                "Select a registration to inspect",
                [item.get("team_name", "Unnamed team") for item in registrations],
            )

            selected = next(
                item for item in registrations if item.get("team_name", "Unnamed team") == selected_team
            )

            left, right = st.columns(2)

            with left:
                st.markdown("### Team")
                st.write(f"**Team:** {selected.get('team_name', '')}")
                st.write(f"**Preferred car:** {selected.get('car_choice', '')}")
                st.write(f"**Backup car:** {selected.get('backup_car_choice', '')}")
                st.write(f"**Experience:** {selected.get('experience', '')}")
                st.write(f"**Status:** {selected.get('status', '')}")

            with right:
                st.markdown("### Drivers")
                st.write(f"**Driver 1:** {selected.get('driver_1_name', '')}")
                st.write(f"**Driver 1 email:** {selected.get('driver_1_email', '')}")
                st.write(f"**Driver 1 phone:** {selected.get('driver_1_phone', '')}")
                st.write(f"**Driver 2:** {selected.get('driver_2_name', '')}")
                st.write(f"**Driver 2 email:** {selected.get('driver_2_email', '')}")
                st.write(f"**Driver 2 phone:** {selected.get('driver_2_phone', '')}")

            st.markdown("### Notes")
            st.write(selected.get("notes", ""))

            st.markdown("### Source file")
            st.code(selected.get("_github_path", ""))

    with tab_notes:
        st.subheader("Admin roadmap")
        st.write(
            """
            Next admin upgrades:

            1. Add approve / reject workflow.
            2. Move approved entries into confirmed event entries.
            3. Add payment status tracking.
            4. Add contact status tracking.
            """
        )