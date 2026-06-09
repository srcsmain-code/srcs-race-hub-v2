from __future__ import annotations

import pandas as pd
import streamlit as st

from src.event_entries import (
    create_event_entry,
    list_event_entries,
    update_event_entry,
)
from src.events import get_event_label, list_events
from src.github_writer import github_configured
from src.ui_components import show_header


ENTRY_TYPE_OPTIONS = [
    "regular",
    "reserve",
    "guest",
    "wildcard",
]

ATTENDANCE_STATUS_OPTIONS = [
    "expected",
    "confirmed",
    "absent",
    "no_show",
    "reserve_available",
    "reserve_used",
]

PAYMENT_STATUS_OPTIONS = [
    "not_requested",
    "pending",
    "paid",
    "comped",
    "refunded",
    "not_applicable",
]

RESERVE_STATUS_OPTIONS = [
    "not_applicable",
    "available",
    "used",
    "standby",
]

GRID_STATUS_OPTIONS = [
    "not_assigned",
    "assigned",
    "checked_in",
    "racing",
    "withdrawn",
]


def option_index(options: list[str], value: str, default: str) -> int:
    selected = value or default
    if selected in options:
        return options.index(selected)
    return options.index(default)


def entries_to_dataframe(entries: list[dict]) -> pd.DataFrame:
    rows = []

    for item in entries:
        rows.append(
            {
                "Driver": item.get("driver_name", ""),
                "Team": item.get("team_name", ""),
                "Entry Type": item.get("entry_type", ""),
                "Attendance": item.get("attendance_status", ""),
                "Payment": item.get("payment_status", ""),
                "Reserve": item.get("reserve_status", ""),
                "Grid": item.get("grid_status", ""),
                "Notes": item.get("notes", ""),
                "Updated UTC": item.get("updated_at_utc", ""),
                "Path": item.get("_github_path", ""),
            }
        )

    return pd.DataFrame(rows)


def render_create_entry(event_id: str) -> None:
    st.subheader("Create event entry")

    with st.form(f"{event_id}_create_event_entry"):
        driver_name = st.text_input("Driver name")
        team_name = st.text_input("Team name")

        col1, col2 = st.columns(2)

        with col1:
            entry_type = st.selectbox("Entry type", ENTRY_TYPE_OPTIONS)
            attendance_status = st.selectbox("Attendance status", ATTENDANCE_STATUS_OPTIONS)

        with col2:
            payment_status = st.selectbox("Payment status", PAYMENT_STATUS_OPTIONS)
            reserve_status = st.selectbox("Reserve status", RESERVE_STATUS_OPTIONS)

        grid_status = st.selectbox("Grid status", GRID_STATUS_OPTIONS)
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Create / save entry")

    if submitted:
        if not driver_name:
            st.error("Driver name is required.")
            return

        try:
            path = create_event_entry(
                event_id=event_id,
                driver_name=driver_name,
                team_name=team_name,
                entry_type=entry_type,
                attendance_status=attendance_status,
                payment_status=payment_status,
                reserve_status=reserve_status,
                grid_status=grid_status,
                notes=notes,
            )
            st.success("Event entry saved.")
            st.code(path)
            st.rerun()
        except Exception as exc:
            st.error("Could not save event entry.")
            st.exception(exc)


def render_update_entry(event_id: str, entries: list[dict]) -> None:
    st.subheader("Update event entry")

    if not entries:
        st.info("No entries yet.")
        return

    label_map = {
        f"{item.get('driver_name', 'Unnamed driver')} — {item.get('team_name', '')}": item
        for item in entries
    }

    selected_label = st.selectbox("Select entry", list(label_map.keys()))
    selected = label_map[selected_label]

    with st.form(f"{event_id}_update_event_entry"):
        driver_name = st.text_input("Driver name", value=selected.get("driver_name", ""))
        team_name = st.text_input("Team name", value=selected.get("team_name", ""))

        col1, col2 = st.columns(2)

        with col1:
            entry_type = st.selectbox(
                "Entry type",
                ENTRY_TYPE_OPTIONS,
                index=option_index(ENTRY_TYPE_OPTIONS, selected.get("entry_type", ""), "regular"),
            )
            attendance_status = st.selectbox(
                "Attendance status",
                ATTENDANCE_STATUS_OPTIONS,
                index=option_index(ATTENDANCE_STATUS_OPTIONS, selected.get("attendance_status", ""), "expected"),
            )

        with col2:
            payment_status = st.selectbox(
                "Payment status",
                PAYMENT_STATUS_OPTIONS,
                index=option_index(PAYMENT_STATUS_OPTIONS, selected.get("payment_status", ""), "pending"),
            )
            reserve_status = st.selectbox(
                "Reserve status",
                RESERVE_STATUS_OPTIONS,
                index=option_index(RESERVE_STATUS_OPTIONS, selected.get("reserve_status", ""), "not_applicable"),
            )

        grid_status = st.selectbox(
            "Grid status",
            GRID_STATUS_OPTIONS,
            index=option_index(GRID_STATUS_OPTIONS, selected.get("grid_status", ""), "not_assigned"),
        )

        notes = st.text_area("Notes", value=selected.get("notes", ""))

        submitted = st.form_submit_button("Update entry")

    if submitted:
        if not driver_name:
            st.error("Driver name is required.")
            return

        try:
            path = update_event_entry(
                event_id=event_id,
                existing_entry=selected,
                updates={
                    "driver_name": driver_name,
                    "team_name": team_name,
                    "entry_type": entry_type,
                    "attendance_status": attendance_status,
                    "payment_status": payment_status,
                    "reserve_status": reserve_status,
                    "grid_status": grid_status,
                    "notes": notes,
                },
            )
            st.success("Event entry updated.")
            st.code(path)
            st.rerun()
        except Exception as exc:
            st.error("Could not update event entry.")
            st.exception(exc)


def render() -> None:
    show_header("Admin Event Entries", "Attendance, payment, reserves and grid management")

    if not github_configured():
        st.error("GitHub storage is not configured. Check Streamlit secrets.")
        st.stop()

    events = list_events()

    if not events:
        st.error("No event configs found.")
        st.stop()

    event_label_map = {
        get_event_label(event): event
        for event in events
    }

    selected_event_label = st.selectbox("Select event", list(event_label_map.keys()))
    selected_event = event_label_map[selected_event_label]
    event_id = selected_event["event_id"]

    st.caption(
        f"Event ID: {event_id} | "
        f"Category: {selected_event.get('category', '')} | "
        f"Type: {selected_event.get('event_type', '')}"
    )

    entries = list_event_entries(event_id)

    tab_overview, tab_create, tab_update = st.tabs(
        [
            "Entry Overview",
            "Create Entry",
            "Update Entry",
        ]
    )

    with tab_overview:
        st.subheader("Event entries")

        if not entries:
            st.info("No event entries found for this event.")
        else:
            df = entries_to_dataframe(entries)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.download_button(
                label="Download event entries as CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"{event_id}_event_entries.csv",
                mime="text/csv",
            )

    with tab_create:
        render_create_entry(event_id)

    with tab_update:
        render_update_entry(event_id, entries)