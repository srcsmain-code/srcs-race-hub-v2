from __future__ import annotations

import pandas as pd
import streamlit as st

from src.github_writer import (
    github_configured,
    list_approved_spa_3h_registrations,
    list_pending_spa_3h_registrations,
    list_rejected_spa_3h_registrations,
    update_registration_status,
)
from src.ui_components import show_header


def registrations_to_dataframe(registrations: list[dict]) -> pd.DataFrame:
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

    return pd.DataFrame(table_rows)


def render_registration_details(selected: dict) -> None:
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

    if selected.get("admin_note"):
        st.markdown("### Admin note")
        st.write(selected.get("admin_note", ""))

    st.markdown("### Source file")
    st.code(selected.get("_github_path", ""))


def render_registration_table(title: str, registrations: list[dict], filename: str) -> None:
    st.subheader(title)

    if not registrations:
        st.info("No registrations found.")
        return

    df = registrations_to_dataframe(registrations)

    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        label=f"Download {title.lower()} as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )


def render() -> None:
    show_header("Race Hub Admin", "Pending submissions and operational review")

    if not github_configured():
        st.error("GitHub storage is not configured. Check Streamlit secrets.")
        st.stop()

    tab_pending, tab_approved, tab_rejected, tab_notes = st.tabs(
        [
            "Pending Spa 3H",
            "Approved Spa 3H",
            "Rejected Spa 3H",
            "Admin Notes",
        ]
    )

    with tab_pending:
        st.subheader("Pending Spa 3H registrations")

        if st.button("Refresh pending registrations"):
            st.rerun()

        try:
            registrations = list_pending_spa_3h_registrations()
        except Exception as exc:
            st.error("Could not load pending registrations from GitHub.")
            st.exception(exc)
            st.stop()

        actionable = [
            item for item in registrations
            if item.get("status") == "pending"
        ]

        copied = [
            item for item in registrations
            if item.get("status") != "pending"
        ]

        if not actionable:
            st.info("No pending Spa 3H registrations awaiting review.")
        else:
            df = registrations_to_dataframe(actionable)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.download_button(
                label="Download pending registrations as CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name="spa_3h_pending_registrations.csv",
                mime="text/csv",
            )

            st.divider()
            st.subheader("Review registration")

            selected_label_map = {
                f"{item.get('team_name', 'Unnamed team')} — {item.get('submitted_at_utc', '')}": item
                for item in actionable
            }

            selected_label = st.selectbox(
                "Select a registration to inspect",
                list(selected_label_map.keys()),
            )

            selected = selected_label_map[selected_label]
            render_registration_details(selected)

            st.divider()
            st.subheader("Decision")

            admin_note = st.text_area("Admin note", placeholder="Optional note, e.g. payment confirmed, contacted captain, duplicate entry, etc.")

            col_approve, col_reject = st.columns(2)

            with col_approve:
                if st.button("Approve registration", type="primary"):
                    try:
                        destination = update_registration_status(
                            selected,
                            status="approved",
                            admin_note=admin_note,
                        )
                        st.success("Registration approved.")
                        st.code(destination)
                        st.rerun()
                    except Exception as exc:
                        st.error("Could not approve registration.")
                        st.exception(exc)

            with col_reject:
                if st.button("Reject registration"):
                    try:
                        destination = update_registration_status(
                            selected,
                            status="rejected",
                            admin_note=admin_note,
                        )
                        st.warning("Registration rejected.")
                        st.code(destination)
                        st.rerun()
                    except Exception as exc:
                        st.error("Could not reject registration.")
                        st.exception(exc)

        if copied:
            with st.expander("Already processed pending files"):
                df_copied = registrations_to_dataframe(copied)
                st.dataframe(df_copied, use_container_width=True, hide_index=True)

    with tab_approved:
        try:
            approved = list_approved_spa_3h_registrations()
        except Exception as exc:
            st.error("Could not load approved registrations from GitHub.")
            st.exception(exc)
            st.stop()

        render_registration_table(
            "Approved Spa 3H registrations",
            approved,
            "spa_3h_approved_registrations.csv",
        )

    with tab_rejected:
        try:
            rejected = list_rejected_spa_3h_registrations()
        except Exception as exc:
            st.error("Could not load rejected registrations from GitHub.")
            st.exception(exc)
            st.stop()

        render_registration_table(
            "Rejected Spa 3H registrations",
            rejected,
            "spa_3h_rejected_registrations.csv",
        )

    with tab_notes:
        st.subheader("Admin roadmap")
        st.write(
            """
            Next admin upgrades:

            1. Show approved teams publicly on the Spa 3H event page.
            2. Add payment status tracking.
            3. Add contact status tracking.
            4. Add edit registration functionality.
            5. Add true archive/move behaviour for processed pending files.
            """
        )