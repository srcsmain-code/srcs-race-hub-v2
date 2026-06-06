from __future__ import annotations

import pandas as pd
import streamlit as st

from src.events import get_event_label, list_events
from src.github_writer import (
    github_configured,
    list_registrations,
    update_registration_status,
)
from src.ui_components import show_header


def get_registration_type(event: dict) -> str:
    return event.get("registration_type", "")


def team_2_driver_rows(registrations: list[dict]) -> list[dict]:
    rows = []

    for item in registrations:
        rows.append(
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

    return rows


def single_driver_rows(registrations: list[dict]) -> list[dict]:
    rows = []

    for item in registrations:
        rows.append(
            {
                "Submitted UTC": item.get("submitted_at_utc", ""),
                "Driver": item.get("driver_name", ""),
                "Email": item.get("driver_email", ""),
                "Phone": item.get("driver_phone", ""),
                "Preferred Car/Class": item.get("car_choice", ""),
                "Experience": item.get("experience", ""),
                "Status": item.get("status", ""),
                "GitHub Path": item.get("_github_path", ""),
            }
        )

    return rows


def lead_form_rows(registrations: list[dict]) -> list[dict]:
    rows = []

    for item in registrations:
        rows.append(
            {
                "Submitted UTC": item.get("submitted_at_utc", ""),
                "Name": item.get("name", ""),
                "Email": item.get("email", ""),
                "Phone": item.get("phone", ""),
                "Preferred Venue": item.get("preferred_venue", ""),
                "Interest": item.get("interest", ""),
                "Experience": item.get("experience", ""),
                "Source": item.get("source", ""),
                "Status": item.get("status", ""),
                "GitHub Path": item.get("_github_path", ""),
            }
        )

    return rows


def registrations_to_dataframe(registrations: list[dict], registration_type: str) -> pd.DataFrame:
    if registration_type == "team_2_driver":
        rows = team_2_driver_rows(registrations)
    elif registration_type == "single_driver":
        rows = single_driver_rows(registrations)
    elif registration_type == "lead_form":
        rows = lead_form_rows(registrations)
    else:
        rows = generic_rows(registrations)

    return pd.DataFrame(rows)


def generic_rows(registrations: list[dict]) -> list[dict]:
    rows = []

    for item in registrations:
        rows.append(
            {
                "Submitted UTC": item.get("submitted_at_utc", ""),
                "Event": item.get("event_name", item.get("event_id", "")),
                "Entry Type": item.get("entry_type", ""),
                "Registration Type": item.get("registration_type", ""),
                "Status": item.get("status", ""),
                "GitHub Path": item.get("_github_path", ""),
            }
        )

    return rows


def get_registration_label(item: dict, registration_type: str) -> str:
    submitted = item.get("submitted_at_utc", "")

    if registration_type == "team_2_driver":
        name = item.get("team_name", "Unnamed team")
    elif registration_type == "single_driver":
        name = item.get("driver_name", "Unnamed driver")
    elif registration_type == "lead_form":
        name = item.get("name", "Unnamed lead")
    else:
        name = item.get("submission_id", "Unnamed submission")

    return f"{name} — {submitted}"


def render_team_2_driver_details(selected: dict) -> None:
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


def render_single_driver_details(selected: dict) -> None:
    left, right = st.columns(2)

    with left:
        st.markdown("### Driver")
        st.write(f"**Driver:** {selected.get('driver_name', '')}")
        st.write(f"**Email:** {selected.get('driver_email', '')}")
        st.write(f"**Phone:** {selected.get('driver_phone', '')}")

    with right:
        st.markdown("### Entry")
        st.write(f"**Preferred car/class:** {selected.get('car_choice', '')}")
        st.write(f"**Experience:** {selected.get('experience', '')}")
        st.write(f"**Status:** {selected.get('status', '')}")


def render_lead_form_details(selected: dict) -> None:
    left, right = st.columns(2)

    with left:
        st.markdown("### Lead")
        st.write(f"**Name:** {selected.get('name', '')}")
        st.write(f"**Email:** {selected.get('email', '')}")
        st.write(f"**Phone:** {selected.get('phone', '')}")

    with right:
        st.markdown("### Interest")
        st.write(f"**Preferred venue:** {selected.get('preferred_venue', '')}")
        st.write(f"**Interest:** {selected.get('interest', '')}")
        st.write(f"**Experience:** {selected.get('experience', '')}")
        st.write(f"**Source:** {selected.get('source', '')}")
        st.write(f"**Status:** {selected.get('status', '')}")


def render_registration_details(selected: dict, registration_type: str) -> None:
    if registration_type == "team_2_driver":
        render_team_2_driver_details(selected)
    elif registration_type == "single_driver":
        render_single_driver_details(selected)
    elif registration_type == "lead_form":
        render_lead_form_details(selected)
    else:
        st.json(selected)

    st.markdown("### Notes")
    st.write(selected.get("notes", ""))

    if selected.get("admin_note"):
        st.markdown("### Admin note")
        st.write(selected.get("admin_note", ""))

    st.markdown("### Source file")
    st.code(selected.get("_github_path", ""))


def render_registration_table(
    title: str,
    registrations: list[dict],
    filename: str,
    registration_type: str,
) -> None:
    st.subheader(title)

    if not registrations:
        st.info("No registrations found.")
        return

    df = registrations_to_dataframe(registrations, registration_type)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.download_button(
        label=f"Download {title.lower()} as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )


def render() -> None:
    show_header("Race Hub Admin", "Event registrations and operational review")

    if not github_configured():
        st.error("GitHub storage is not configured. Check Streamlit secrets.")
        st.stop()

    events = list_events()

    if not events:
        st.error("No event configs found in data/events.")
        st.stop()

    event_label_map = {
        get_event_label(event): event
        for event in events
    }

    selected_event_label = st.selectbox(
        "Select event",
        list(event_label_map.keys()),
    )

    selected_event = event_label_map[selected_event_label]
    event_id = selected_event["event_id"]
    registration_type = get_registration_type(selected_event)

    st.caption(
        f"Category: {selected_event.get('category', '')} | "
        f"Type: {selected_event.get('event_type', '')} | "
        f"Registration type: {registration_type} | "
        f"Registration open: {selected_event.get('registration_open', False)}"
    )

    tab_pending, tab_approved, tab_rejected, tab_notes = st.tabs(
        [
            "Pending",
            "Approved",
            "Rejected",
            "Admin Notes",
        ]
    )

    with tab_pending:
        if st.button("Refresh pending registrations"):
            st.rerun()

        try:
            registrations = list_registrations(event_id, "pending")
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
            st.info("No pending registrations awaiting review for this event.")
        else:
            df = registrations_to_dataframe(actionable, registration_type)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.download_button(
                label="Download pending registrations as CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"{event_id}_pending_registrations.csv",
                mime="text/csv",
            )

            st.divider()
            st.subheader("Review registration")

            selected_label_map = {
                get_registration_label(item, registration_type): item
                for item in actionable
            }

            selected_label = st.selectbox(
                "Select a registration to inspect",
                list(selected_label_map.keys()),
            )

            selected = selected_label_map[selected_label]
            render_registration_details(selected, registration_type)

            st.divider()
            st.subheader("Decision")

            admin_note = st.text_area(
                "Admin note",
                placeholder="Optional note, e.g. contacted lead, payment confirmed, duplicate entry, etc.",
            )

            col_approve, col_reject = st.columns(2)

            with col_approve:
                if st.button("Approve registration", type="primary"):
                    try:
                        destination = update_registration_status(
                            event_id,
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
                            event_id,
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
                df_copied = registrations_to_dataframe(copied, registration_type)
                st.dataframe(df_copied, use_container_width=True, hide_index=True)

    with tab_approved:
        try:
            approved = list_registrations(event_id, "approved")
        except Exception as exc:
            st.error("Could not load approved registrations from GitHub.")
            st.exception(exc)
            st.stop()

        render_registration_table(
            "Approved registrations",
            approved,
            f"{event_id}_approved_registrations.csv",
            registration_type,
        )

    with tab_rejected:
        try:
            rejected = list_registrations(event_id, "rejected")
        except Exception as exc:
            st.error("Could not load rejected registrations from GitHub.")
            st.exception(exc)
            st.stop()

        render_registration_table(
            "Rejected registrations",
            rejected,
            f"{event_id}_rejected_registrations.csv",
            registration_type,
        )

    with tab_notes:
        st.subheader("Admin roadmap")
        st.write(
            """
            Next admin upgrades:

            1. Add lead follow-up status.
            2. Add contact priority.
            3. Add payment status for paid events.
            4. Add event entry management for championship events.
            5. Add edit registration functionality.
            """
        )