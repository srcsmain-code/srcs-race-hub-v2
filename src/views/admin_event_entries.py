from __future__ import annotations

import pandas as pd
import streamlit as st

from src.event_entries import (
    apply_team_payment_summary,
    create_single_driver_event_entry,
    create_team_2_driver_event_entry,
    list_event_entries,
    update_event_entry,
)
from src.events import get_event_label, list_events
from src.github_writer import github_configured
from src.ui_components import show_header


CONTACT_STATUS_OPTIONS = [
    "not_contacted",
    "contacted",
    "awaiting_response",
    "confirmed",
    "issue",
]

PAYMENT_METHOD_OPTIONS = [
    "",
    "bank_transfer",
    "tikkie",
    "cash",
    "card",
    "other",
]

DISCOUNT_REASON_OPTIONS = [
    "none",
    "guest_seat",
    "promo",
    "sponsor",
    "organiser_comp",
    "early_bird",
    "manual_discount",
    "other",
]

PRIMARY_CONTACT_OPTIONS = [
    "driver_1",
    "driver_2",
    "both",
    "external",
]

READY_STATUS_OPTIONS = [
    "not_ready",
    "waiting_payment",
    "waiting_confirmation",
    "ready",
    "issue",
]

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
    "part_paid",
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


def entries_to_dataframe(entries: list[dict], registration_type: str) -> pd.DataFrame:
    rows = []

    for item in entries:
        if registration_type == "team_2_driver" or item.get("entry_format") == "team_2_driver":
            rows.append(
                {
                    "Team": item.get("team_name", ""),
                    "Car": item.get("car_choice", ""),
                    "Backup Car": item.get("backup_car_choice", ""),
                    "Driver 1": item.get("driver_1_name", ""),
                    "Driver 1 Attendance": item.get("driver_1_attendance_status", ""),
                    "Driver 2": item.get("driver_2_name", ""),
                    "Driver 2 Attendance": item.get("driver_2_attendance_status", ""),
                    "Entry Type": item.get("entry_type", ""),
                                        "D1 Due": item.get("driver_1_amount_due", 0.0),
                    "D1 Paid": item.get("driver_1_amount_paid", 0.0),
                    "D1 Pay Status": item.get("driver_1_payment_status", ""),
                    "D1 Discount": item.get("driver_1_discount_amount", 0.0),
                    "D1 Discount Reason": item.get("driver_1_discount_reason", ""),
                    "D2 Due": item.get("driver_2_amount_due", 0.0),
                    "D2 Paid": item.get("driver_2_amount_paid", 0.0),
                    "D2 Pay Status": item.get("driver_2_payment_status", ""),
                    "D2 Discount": item.get("driver_2_discount_amount", 0.0),
                    "D2 Discount Reason": item.get("driver_2_discount_reason", ""),
                    "Team Due": item.get("team_amount_due", 0.0),
                    "Team Paid": item.get("team_amount_paid", 0.0),
                    "Team Payment": item.get("team_payment_status", ""),
                    "Primary Contact": item.get("primary_contact_driver", ""),
                    "Ready": item.get("ready_status", ""),
                    "Payment": item.get("payment_status", ""),
                    "Reserve": item.get("reserve_status", ""),
                    "Grid": item.get("grid_status", ""),
                    "Notes": item.get("notes", ""),
                    "Updated UTC": item.get("updated_at_utc", ""),
                    "Path": item.get("_github_path", ""),
                }
            )
        else:
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


def render_create_single_driver_entry(event_id: str) -> None:
    st.subheader("Create single-driver event entry")

    with st.form(f"{event_id}_create_single_driver_event_entry"):
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
            path = create_single_driver_event_entry(
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


def render_driver_payment_section(
    driver_label: str,
    prefix: str,
    standard_fee: float,
    selected: dict | None = None,
    key_scope: str = "entry",
) -> dict:
    selected = selected or {}

    st.markdown(f"#### {driver_label} payment/contact")

    col1, col2 = st.columns(2)

    with col1:
        email = st.text_input(
            f"{driver_label} email",
            value=selected.get(f"{prefix}_email", ""),
            key=f"{key_scope}_{prefix}_email",
        )
        phone = st.text_input(
            f"{driver_label} phone",
            value=selected.get(f"{prefix}_phone", ""),
            key=f"{key_scope}_{prefix}_phone",
        )
        contact_status = st.selectbox(
            f"{driver_label} contact status",
            CONTACT_STATUS_OPTIONS,
            index=option_index(
                CONTACT_STATUS_OPTIONS,
                selected.get(f"{prefix}_contact_status", ""),
                "not_contacted",
            ),
            key=f"{key_scope}_{prefix}_contact_status",
        )

        shown_standard_fee = float(
            selected.get(f"{prefix}_standard_fee", standard_fee) or standard_fee
        )

        st.number_input(
            f"{driver_label} standard fee",
            min_value=0.0,
            step=5.0,
            value=shown_standard_fee,
            disabled=True,
            key=f"{key_scope}_{prefix}_standard_fee_display",
        )

    with col2:
        discount_amount = st.number_input(
            f"{driver_label} discount amount",
            min_value=0.0,
            step=5.0,
            value=float(selected.get(f"{prefix}_discount_amount", 0.0) or 0.0),
            key=f"{key_scope}_{prefix}_discount_amount",
        )
        discount_reason = st.selectbox(
            f"{driver_label} discount reason",
            DISCOUNT_REASON_OPTIONS,
            index=option_index(
                DISCOUNT_REASON_OPTIONS,
                selected.get(f"{prefix}_discount_reason", ""),
                "none",
            ),
            key=f"{key_scope}_{prefix}_discount_reason",
        )
        amount_paid = st.number_input(
            f"{driver_label} amount paid",
            min_value=0.0,
            step=5.0,
            value=float(selected.get(f"{prefix}_amount_paid", 0.0) or 0.0),
            key=f"{key_scope}_{prefix}_amount_paid",
        )
        payment_method = st.selectbox(
            f"{driver_label} payment method",
            PAYMENT_METHOD_OPTIONS,
            index=option_index(
                PAYMENT_METHOD_OPTIONS,
                selected.get(f"{prefix}_payment_method", ""),
                "",
            ),
            key=f"{key_scope}_{prefix}_payment_method",
        )

    payment_note = st.text_area(
        f"{driver_label} payment note",
        value=selected.get(f"{prefix}_payment_note", ""),
        key=f"{key_scope}_{prefix}_payment_note",
    )

    return {
        f"{prefix}_email": email,
        f"{prefix}_phone": phone,
        f"{prefix}_contact_status": contact_status,
        f"{prefix}_discount_amount": discount_amount,
        f"{prefix}_discount_reason": discount_reason,
        f"{prefix}_amount_paid": amount_paid,
        f"{prefix}_payment_method": payment_method,
        f"{prefix}_payment_note": payment_note,
    }

def render_create_team_2_driver_entry(event_id: str, event: dict) -> None:
    st.subheader("Create 2-driver team event entry")

    cars = event.get("cars", [])
    pricing = event.get("pricing", {})
    standard_fee = float(pricing.get("standard_driver_entry_fee", 0.0) or 0.0)
    currency = pricing.get("currency", "EUR")

    with st.form(f"{event_id}_create_team_2_driver_event_entry"):
        st.markdown("### Team")
        team_name = st.text_input("Team name")

        if cars:
            car_choice = st.selectbox("Car", cars)
            backup_car_choice = st.selectbox("Backup car", cars)
        else:
            car_choice = st.text_input("Car")
            backup_car_choice = st.text_input("Backup car")

        st.markdown("### Drivers")

        col_d1, col_d2 = st.columns(2)

        with col_d1:
            driver_1_name = st.text_input("Driver 1 name")
            driver_1_attendance_status = st.selectbox(
                "Driver 1 attendance",
                ATTENDANCE_STATUS_OPTIONS,
                key=f"{event_id}_d1_attendance_create",
            )

        with col_d2:
            driver_2_name = st.text_input("Driver 2 name")
            driver_2_attendance_status = st.selectbox(
                "Driver 2 attendance",
                ATTENDANCE_STATUS_OPTIONS,
                key=f"{event_id}_d2_attendance_create",
            )

        st.markdown("### Payment / contact per driver")
        st.caption(f"Standard driver entry fee for this event: {currency} {standard_fee:.2f}")

        driver_1_payment_data = render_driver_payment_section(
            "Driver 1",
            "driver_1",
            standard_fee,
            key_scope=f"{event_id}_create",
        )

        driver_2_payment_data = render_driver_payment_section(
            "Driver 2",
            "driver_2",
            standard_fee,
            key_scope=f"{event_id}_create",
        )
        
        st.markdown("### Entry management")

        col1, col2 = st.columns(2)

        with col1:
            entry_type = st.selectbox("Entry type", ENTRY_TYPE_OPTIONS)
            reserve_status = st.selectbox("Reserve status", RESERVE_STATUS_OPTIONS)
            primary_contact_driver = st.selectbox("Primary contact", PRIMARY_CONTACT_OPTIONS)

        with col2:
            grid_status = st.selectbox("Grid status", GRID_STATUS_OPTIONS)
            ready_status = st.selectbox("Ready status", READY_STATUS_OPTIONS)

        notes = st.text_area("General notes")

        submitted = st.form_submit_button("Create / save team entry")

    if submitted:
        if not team_name:
            st.error("Team name is required.")
            return

        if not driver_1_name or not driver_2_name:
            st.error("Both driver names are required.")
            return

        try:
            path = create_team_2_driver_event_entry(
                event_id=event_id,
                team_name=team_name,
                car_choice=car_choice,
                backup_car_choice=backup_car_choice,
                driver_1_name=driver_1_name,
                driver_1_attendance_status=driver_1_attendance_status,
                driver_2_name=driver_2_name,
                driver_2_attendance_status=driver_2_attendance_status,
                entry_type=entry_type,
                reserve_status=reserve_status,
                grid_status=grid_status,
                notes=notes,
                event=event,
                primary_contact_driver=primary_contact_driver,
                ready_status=ready_status,
                **driver_1_payment_data,
                **driver_2_payment_data,
            )
            st.success("Team event entry saved.")
            st.code(path)
            st.rerun()
        except Exception as exc:
            st.error("Could not save team event entry.")
            st.exception(exc)


def render_update_single_driver_entry(event_id: str, selected: dict) -> None:
    with st.form(f"{event_id}_update_single_driver_event_entry"):
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
                    "entry_format": "single_driver",
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


def render_update_team_2_driver_entry(event_id: str, event: dict, selected: dict) -> None:
    cars = event.get("cars", [])

    pricing = event.get("pricing", {})
    standard_fee = float(pricing.get("standard_driver_entry_fee", 0.0) or 0.0)
    currency = pricing.get("currency", "EUR")

    with st.form(f"{event_id}_update_team_2_driver_event_entry"):
        st.markdown("### Team")

        team_name = st.text_input(
            "Team name",
            value=selected.get("team_name", ""),
        )

        if cars:
            car_choice = st.selectbox(
                "Car",
                cars,
                index=option_index(cars, selected.get("car_choice", ""), cars[0]),
            )
            backup_car_choice = st.selectbox(
                "Backup car",
                cars,
                index=option_index(cars, selected.get("backup_car_choice", ""), cars[0]),
            )
        else:
            car_choice = st.text_input(
                "Car",
                value=selected.get("car_choice", ""),
            )
            backup_car_choice = st.text_input(
                "Backup car",
                value=selected.get("backup_car_choice", ""),
            )

        st.markdown("### Drivers")

        col_d1, col_d2 = st.columns(2)

        with col_d1:
            driver_1_name = st.text_input(
                "Driver 1 name",
                value=selected.get("driver_1_name", ""),
            )
            driver_1_attendance_status = st.selectbox(
                "Driver 1 attendance",
                ATTENDANCE_STATUS_OPTIONS,
                index=option_index(
                    ATTENDANCE_STATUS_OPTIONS,
                    selected.get("driver_1_attendance_status", ""),
                    "expected",
                ),
            )

        with col_d2:
            driver_2_name = st.text_input(
                "Driver 2 name",
                value=selected.get("driver_2_name", ""),
            )
            driver_2_attendance_status = st.selectbox(
                "Driver 2 attendance",
                ATTENDANCE_STATUS_OPTIONS,
                index=option_index(
                    ATTENDANCE_STATUS_OPTIONS,
                    selected.get("driver_2_attendance_status", ""),
                    "expected",
                ),
            )

        st.markdown("### Payment / contact per driver")
        st.caption(f"Standard driver entry fee for this event: {currency} {standard_fee:.2f}")

        driver_1_payment_data = render_driver_payment_section(
            "Driver 1",
            "driver_1",
            standard_fee,
            selected,
            key_scope=f"{event_id}_update",
        )

        driver_2_payment_data = render_driver_payment_section(
            "Driver 2",
            "driver_2",
            standard_fee,
            selected,
            key_scope=f"{event_id}_update",
        )

        st.markdown("### Entry management")

        col1, col2 = st.columns(2)

        with col1:
            entry_type = st.selectbox(
                "Entry type",
                ENTRY_TYPE_OPTIONS,
                index=option_index(
                    ENTRY_TYPE_OPTIONS,
                    selected.get("entry_type", ""),
                    "regular",
                ),
            )
            reserve_status = st.selectbox(
                "Reserve status",
                RESERVE_STATUS_OPTIONS,
                index=option_index(
                    RESERVE_STATUS_OPTIONS,
                    selected.get("reserve_status", ""),
                    "not_applicable",
                ),
            )
            primary_contact_driver = st.selectbox(
                "Primary contact",
                PRIMARY_CONTACT_OPTIONS,
                index=option_index(
                    PRIMARY_CONTACT_OPTIONS,
                    selected.get("primary_contact_driver", ""),
                    "driver_1",
                ),
            )

        with col2:
            grid_status = st.selectbox(
                "Grid status",
                GRID_STATUS_OPTIONS,
                index=option_index(
                    GRID_STATUS_OPTIONS,
                    selected.get("grid_status", ""),
                    "not_assigned",
                ),
            )
            ready_status = st.selectbox(
                "Ready status",
                READY_STATUS_OPTIONS,
                index=option_index(
                    READY_STATUS_OPTIONS,
                    selected.get("ready_status", ""),
                    "not_ready",
                ),
            )

        notes = st.text_area(
            "General notes",
            value=selected.get("notes", ""),
        )

        submitted = st.form_submit_button("Update team entry")

    if submitted:
        if not team_name:
            st.error("Team name is required.")
            return

        if not driver_1_name or not driver_2_name:
            st.error("Both driver names are required.")
            return

        try:
            updates = {
                "entry_format": "team_2_driver",
                "team_name": team_name,
                "car_choice": car_choice,
                "backup_car_choice": backup_car_choice,
                "driver_1_name": driver_1_name,
                "driver_1_attendance_status": driver_1_attendance_status,
                "driver_2_name": driver_2_name,
                "driver_2_attendance_status": driver_2_attendance_status,
                "entry_type": entry_type,
                "reserve_status": reserve_status,
                "grid_status": grid_status,
                "primary_contact_driver": primary_contact_driver,
                "ready_status": ready_status,
                "notes": notes,
                **driver_1_payment_data,
                **driver_2_payment_data,
            }

            calculation_entry = dict(selected)
            calculation_entry.update(updates)

            if not calculation_entry.get("driver_1_standard_fee"):
                calculation_entry["driver_1_standard_fee"] = standard_fee

            if not calculation_entry.get("driver_2_standard_fee"):
                calculation_entry["driver_2_standard_fee"] = standard_fee

            calculation_entry = apply_team_payment_summary(calculation_entry)

            updates.update(
                {
                    "driver_1_standard_fee": calculation_entry.get("driver_1_standard_fee", standard_fee),
                    "driver_2_standard_fee": calculation_entry.get("driver_2_standard_fee", standard_fee),
                    "driver_1_amount_due": calculation_entry.get("driver_1_amount_due", 0.0),
                    "driver_2_amount_due": calculation_entry.get("driver_2_amount_due", 0.0),
                    "driver_1_payment_status": calculation_entry.get("driver_1_payment_status", ""),
                    "driver_2_payment_status": calculation_entry.get("driver_2_payment_status", ""),
                    "team_standard_fee": calculation_entry.get("team_standard_fee", 0.0),
                    "team_discount_amount": calculation_entry.get("team_discount_amount", 0.0),
                    "team_amount_due": calculation_entry.get("team_amount_due", 0.0),
                    "team_amount_paid": calculation_entry.get("team_amount_paid", 0.0),
                    "team_payment_status": calculation_entry.get("team_payment_status", ""),
                }
            )

            path = update_event_entry(
                event_id=event_id,
                existing_entry=selected,
                updates=updates,
            )

            st.success("Team event entry updated.")
            st.code(path)
            st.rerun()

        except Exception as exc:
            st.error("Could not update team event entry.")
            st.exception(exc)


def render_update_entry(event_id: str, event: dict, entries: list[dict]) -> None:
    st.subheader("Update event entry")

    if not entries:
        st.info("No entries yet.")
        return

    registration_type = event.get("registration_type", "")

    if registration_type == "team_2_driver":
        label_map = {
            f"{item.get('team_name', 'Unnamed team')} — {item.get('car_choice', '')}": item
            for item in entries
        }
    else:
        label_map = {
            f"{item.get('driver_name', 'Unnamed driver')} — {item.get('team_name', '')}": item
            for item in entries
        }

    selected_label = st.selectbox("Select entry", list(label_map.keys()))
    selected = label_map[selected_label]

    if registration_type == "team_2_driver" or selected.get("entry_format") == "team_2_driver":
        render_update_team_2_driver_entry(event_id, event, selected)
    else:
        render_update_single_driver_entry(event_id, selected)


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
    registration_type = selected_event.get("registration_type", "")

    st.caption(
        f"Event ID: {event_id} | "
        f"Category: {selected_event.get('category', '')} | "
        f"Type: {selected_event.get('event_type', '')} | "
        f"Registration type: {registration_type}"
    )

    if registration_type == "lead_form":
        st.info("This is a lead-generation event. Use Admin Dashboard for lead follow-up instead of Event Entries.")
        return

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
            df = entries_to_dataframe(entries, registration_type)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.download_button(
                label="Download event entries as CSV",
                data=df.to_csv(index=False).encode("utf-8"),
                file_name=f"{event_id}_event_entries.csv",
                mime="text/csv",
            )

    with tab_create:
        if registration_type == "team_2_driver":
            render_create_team_2_driver_entry(event_id, selected_event)
        else:
            render_create_single_driver_entry(event_id)

    with tab_update:
        render_update_entry(event_id, selected_event, entries)