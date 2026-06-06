from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st

from src.registrations import build_submission_id
from src.validation import is_valid_email, required_fields_present


def base_payload(event: dict[str, Any], submission_id: str, status: str = "pending") -> dict[str, Any]:
    return {
        "submission_id": submission_id,
        "submitted_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "event_id": event.get("event_id", ""),
        "event_name": event.get("event_name", ""),
        "category": event.get("category", ""),
        "event_type": event.get("event_type", ""),
        "registration_type": event.get("registration_type", ""),
    }


def validate_email_fields(payload: dict[str, Any], fields: list[str]) -> tuple[bool, str]:
    for field in fields:
        email = payload.get(field, "")
        if not is_valid_email(email):
            return False, field
    return True, ""


def render_team_2_driver_form(event: dict[str, Any]) -> tuple[bool, dict[str, Any] | None, list[str]]:
    event_id = event.get("event_id", "event")
    event_name = event.get("event_name", "SRCS Event")
    event_short_name = event.get("event_short_name", event_name)
    cars = event.get("cars", [])

    with st.form(f"{event_id}_team_2_driver_registration"):
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

        experience = st.selectbox(
            "Team experience level",
            ["New", "Casual", "Intermediate", "Fast", "Alien"],
        )

        notes = st.text_area("Notes / requests")
        consent = st.checkbox(f"I confirm SRCS may contact us about {event_short_name} and this registration.")

        submitted = st.form_submit_button("Submit registration")

    if not submitted:
        return False, None, []

    submission_id = build_submission_id(team_name)

    payload = base_payload(event, submission_id)
    payload.update(
        {
            "entry_type": "team",
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
    )

    errors: list[str] = []

    required = ["team_name", "driver_1_name", "driver_1_email", "driver_2_name", "driver_2_email"]
    ok, missing = required_fields_present(payload, required)

    if not ok:
        errors.append("Missing required fields: " + ", ".join(missing))

    email_ok, bad_field = validate_email_fields(payload, ["driver_1_email", "driver_2_email"])
    if not email_ok:
        errors.append(f"Invalid email address: {bad_field}")

    if not consent:
        errors.append("Consent is required to submit the registration.")

    return True, payload, errors


def render_single_driver_form(event: dict[str, Any]) -> tuple[bool, dict[str, Any] | None, list[str]]:
    event_id = event.get("event_id", "event")
    event_name = event.get("event_name", "SRCS Event")
    event_short_name = event.get("event_short_name", event_name)
    cars = event.get("cars", [])

    with st.form(f"{event_id}_single_driver_registration"):
        st.subheader("Driver details")
        driver_name = st.text_input("Driver full name")
        driver_email = st.text_input("Driver email")
        driver_phone = st.text_input("Driver phone / WhatsApp")

        if cars:
            car_choice = st.selectbox("Preferred car / class", cars)
        else:
            car_choice = st.text_input("Preferred car / class", placeholder="Optional")

        experience = st.selectbox(
            "Experience level",
            ["New", "Casual", "Intermediate", "Fast", "Alien"],
        )

        notes = st.text_area("Notes / requests")
        consent = st.checkbox(f"I confirm SRCS may contact me about {event_short_name} and this registration.")

        submitted = st.form_submit_button("Submit registration")

    if not submitted:
        return False, None, []

    submission_id = build_submission_id(driver_name)

    payload = base_payload(event, submission_id)
    payload.update(
        {
            "entry_type": "single_driver",
            "driver_name": driver_name,
            "driver_email": driver_email,
            "driver_phone": driver_phone,
            "car_choice": car_choice,
            "experience": experience,
            "notes": notes,
            "consent": consent,
        }
    )

    errors: list[str] = []

    required = ["driver_name", "driver_email"]
    ok, missing = required_fields_present(payload, required)

    if not ok:
        errors.append("Missing required fields: " + ", ".join(missing))

    email_ok, bad_field = validate_email_fields(payload, ["driver_email"])
    if not email_ok:
        errors.append(f"Invalid email address: {bad_field}")

    if not consent:
        errors.append("Consent is required to submit the registration.")

    return True, payload, errors


def render_lead_form(event: dict[str, Any]) -> tuple[bool, dict[str, Any] | None, list[str]]:
    event_id = event.get("event_id", "event")
    event_name = event.get("event_name", "SRCS Event")
    event_short_name = event.get("event_short_name", event_name)

    venue_options = event.get(
        "venue_options",
        [
            "Utrecht",
            "Rotterdam",
            "Zandvoort",
            "Zwolle",
            "Amsterdam",
            "Eindhoven",
            "No preference yet",
        ],
    )

    interest_options = event.get(
        "interest_options",
        [
            "F1",
            "GT3",
            "Both F1 and GT3",
            "Not sure yet",
        ],
    )

    source_options = event.get(
        "source_options",
        [
            "Race Square email",
            "Race Square venue / narrowcasting",
            "QR code",
            "WhatsApp",
            "Friend / referral",
            "Social media",
            "Other",
        ],
    )

    with st.form(f"{event_id}_lead_form"):
        st.subheader("Your details")
        name = st.text_input("Full name")
        email = st.text_input("Email")
        phone = st.text_input("Phone / WhatsApp")

        st.subheader("SRCS interest")
        preferred_venue = st.selectbox("Preferred Race Square venue", venue_options)
        interest = st.selectbox("Interested in", interest_options)
        experience = st.selectbox(
            "Sim racing / racing experience",
            [
                "Never raced before",
                "Casual",
                "Some experience",
                "Experienced",
                "Very fast / competitive",
            ],
        )

        source = st.selectbox("How did you hear about SRCS?", source_options)
        notes = st.text_area("Anything else we should know?")
        consent = st.checkbox(f"I confirm SRCS may contact me about {event_short_name} and future SRCS events.")

        submitted = st.form_submit_button("Submit interest")

    if not submitted:
        return False, None, []

    submission_id = build_submission_id(name)

    payload = base_payload(event, submission_id)
    payload.update(
        {
            "entry_type": "lead",
            "name": name,
            "email": email,
            "phone": phone,
            "preferred_venue": preferred_venue,
            "interest": interest,
            "experience": experience,
            "source": source,
            "notes": notes,
            "consent": consent,
        }
    )

    errors: list[str] = []

    required = ["name", "email", "phone"]
    ok, missing = required_fields_present(payload, required)

    if not ok:
        errors.append("Missing required fields: " + ", ".join(missing))

    email_ok, bad_field = validate_email_fields(payload, ["email"])
    if not email_ok:
        errors.append(f"Invalid email address: {bad_field}")

    if not consent:
        errors.append("Consent is required to submit the form.")

    return True, payload, errors


def render_registration_form(event: dict[str, Any]) -> tuple[bool, dict[str, Any] | None, list[str]]:
    registration_type = event.get("registration_type", "")

    if registration_type == "team_2_driver":
        return render_team_2_driver_form(event)

    if registration_type == "single_driver":
        return render_single_driver_form(event)

    if registration_type == "lead_form":
        return render_lead_form(event)

    return (
        False,
        None,
        [
            f"Unsupported registration type: {registration_type}. "
            "Supported types are team_2_driver, single_driver, and lead_form."
        ],
    )