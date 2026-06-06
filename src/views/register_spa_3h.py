from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

from src.events import load_event
from src.github_writer import commit_json_to_github, github_configured, registration_folder
from src.registrations import build_submission_id
from src.ui_components import show_header
from src.validation import is_valid_email, required_fields_present


DEFAULT_EVENT_ID = "2026_spa_3h_endurance"


def get_event_id() -> str:
    return st.query_params.get("event_id", DEFAULT_EVENT_ID)


def render() -> None:
    event_id = get_event_id()
    event = load_event(event_id)

    event_name = event.get("event_name", "SRCS Event")
    event_short_name = event.get("event_short_name", event_name)
    cars = event.get("cars", [])

    show_header(f"Register for {event_name}", "Creates a pending registration submission")

    if not event.get("registration_open", False):
        st.warning("Registration for this event is currently closed.")
        return

    if github_configured():
        st.success("Registration storage is connected to GitHub.")
    else:
        st.warning("GitHub storage is not configured yet. Add Streamlit secrets before accepting live registrations.")

    with st.form(f"{event_id}_registration"):
        st.subheader("Team details")
        team_name = st.text_input("Team name")

        if cars:
            car_choice = st.selectbox("Preferred car", cars)
            backup_car_choice = st.selectbox("Backup car", cars)
        else:
            car_choice = st.text_input("Preferred car / class")
            backup_car_choice = st.text_input("Backup car / class")

        st.subheader("Driver 1 / Team captain")
        driver_1_name = st.text_input("Driver 1 full name")
        driver_1_email = st.text_input("Driver 1 email")
        driver_1_phone = st.text_input("Driver 1 phone / WhatsApp")

        st.subheader("Driver 2")
        driver_2_name = st.text_input("Driver 2 full name")
        driver_2_email = st.text_input("Driver 2 email")
        driver_2_phone = st.text_input("Driver 2 phone / WhatsApp")

        experience = st.selectbox("Team experience level", ["New", "Casual", "Intermediate", "Fast", "Alien"])
        notes = st.text_area("Notes / requests")
        consent = st.checkbox(f"I confirm SRCS may contact us about {event_short_name} and this registration.")

        submitted = st.form_submit_button("Submit registration")

    if submitted:
        submission_id = build_submission_id(team_name)

        payload = {
            "submission_id": submission_id,
            "submitted_at_utc": datetime.now(timezone.utc).isoformat(),
            "status": "pending",
            "event_id": event_id,
            "event_name": event_name,
            "category": event.get("category", ""),
            "event_type": event.get("event_type", ""),
            "registration_type": event.get("registration_type", ""),
            "team_name": team_name,
            "car_choice": car_choice,
            "backup_car_choice": backup_car_choice,
            "driver_1_name": driver_1_name,
            "driver_1_email": driver_1_email,
            "driver_1_phone": driver_1_phone,
            "driver_2_name": driver_2_name,
            "driver_2_email": driver_2_email,
            "driver_2_phone": driver_2_phone,
            "experience": experience,
            "notes": notes,
            "consent": consent,
        }

        required = ["team_name", "driver_1_name", "driver_1_email", "driver_2_name", "driver_2_email"]
        ok, missing = required_fields_present(payload, required)

        if not ok:
            st.error("Missing required fields: " + ", ".join(missing))
        elif not is_valid_email(driver_1_email) or not is_valid_email(driver_2_email):
            st.error("Please enter valid email addresses for both drivers.")
        elif not consent:
            st.error("Consent is required to submit the registration.")
        elif not github_configured():
            st.error("GitHub storage is not configured. Please check Streamlit secrets.")
        else:
            github_path = f"{registration_folder(event_id, 'pending')}/{submission_id}.json"

            try:
                commit_json_to_github(
                    path=github_path,
                    payload=payload,
                    message=f"Add pending registration for {event_short_name}: {team_name}",
                )
                st.success("Registration submitted as pending.")
                st.code(github_path)
            except Exception as exc:
                st.error("Registration could not be saved to GitHub.")
                st.exception(exc)