from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import streamlit as st
import re
import uuid
from datetime import datetime, timezone

from src.registrations import build_submission_id
from src.validation import is_valid_email, required_fields_present

def slugify_for_submission_id(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = value.strip("_")
    return value or "registration"


def add_submission_metadata(event: dict, payload: dict) -> dict:
    event_id = event.get("event_id", "event")
    route = payload.get("registration_route", "registration")

    display_name = (
        payload.get("team_name")
        or payload.get("driver_name")
        or payload.get("name")
        or "registration"
    )

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    short_id = uuid.uuid4().hex[:7]
    slug = slugify_for_submission_id(display_name)

    payload = dict(payload)
    payload["event_id"] = event_id
    payload["submission_id"] = f"{timestamp}_{route}_{slug}_{short_id}"
    payload["submitted_at_utc"] = datetime.now(timezone.utc).isoformat()
    payload["status"] = "pending"

    return payload

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

    if registration_type == "multi_route":
        return render_multi_route_registration_form(event)
        
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

def render_multi_route_registration_form(event: dict):
    event_id = event.get("event_id", "")
    cars = event.get("cars", [])
    experience_options = event.get(
        "experience_options",
        ["New", "Casual", "Intermediate", "Fast", "Alien"],
    )

    st.subheader("Register for this event")

    registration_route_label = st.radio(
        "How would you like to register?",
        [
            "Register a complete 2-driver team",
            "Register as an individual driver looking for a teammate",
            "I’m interested — keep me updated",
        ],
        key=f"{event_id}_registration_route",
    )

    if registration_route_label == "Register a complete 2-driver team":
        registration_route = "team_2_driver"
    elif registration_route_label == "Register as an individual driver looking for a teammate":
        registration_route = "individual_driver"
    else:
        registration_route = "interest_only"

    with st.form(f"{event_id}_{registration_route}_registration_form"):
        if registration_route == "team_2_driver":
            st.markdown("### Team details")

            team_name = st.text_input("Team name")

            if cars:
                car_choice = st.selectbox("Preferred car", cars)
                backup_car_choice = st.selectbox("Backup car", cars)
            else:
                car_choice = st.text_input("Preferred car")
                backup_car_choice = st.text_input("Backup car")

            team_experience = st.selectbox(
                "Team experience level",
                experience_options,
            )

            st.markdown("### Driver 1")

            driver_1_name = st.text_input("Driver 1 name")
            driver_1_email = st.text_input("Driver 1 email")
            driver_1_phone = st.text_input("Driver 1 phone")

            st.markdown("### Driver 2")

            driver_2_name = st.text_input("Driver 2 name")
            driver_2_email = st.text_input("Driver 2 email")
            driver_2_phone = st.text_input("Driver 2 phone")

            notes = st.text_area("Notes / questions")

            submitted = st.form_submit_button("Submit team registration")

            if submitted:
                if not team_name or not driver_1_name or not driver_2_name:
                    return True, {}, ["Team name and both driver names are required."]

                payload = {
                    "registration_type": "multi_route",
                    "registration_route": "team_2_driver",
                    "team_name": team_name,
                    "car_choice": car_choice,
                    "backup_car_choice": backup_car_choice,
                    "experience": team_experience,
                    "driver_1_name": driver_1_name,
                    "driver_1_email": driver_1_email,
                    "driver_1_phone": driver_1_phone,
                    "driver_2_name": driver_2_name,
                    "driver_2_email": driver_2_email,
                    "driver_2_phone": driver_2_phone,
                    "notes": notes,
                }

                return True, add_submission_metadata(event, payload), []

        elif registration_route == "individual_driver":
            st.markdown("### Individual driver details")

            driver_name = st.text_input("Driver name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")

            experience = st.selectbox(
                "Experience level",
                experience_options,
            )

            if cars:
                preferred_car = st.selectbox("Preferred car", cars)
                backup_car = st.selectbox("Backup car", cars)
            else:
                preferred_car = st.text_input("Preferred car")
                backup_car = st.text_input("Backup car")

            can_be_team_captain = st.selectbox(
                "Are you willing to act as team captain if needed?",
                ["Yes", "No", "Maybe"],
            )

            preferred_teammate = st.text_input(
                "Preferred teammate, if any",
                help="Optional. Leave blank if you are happy to be paired by SRCS.",
            )

            notes = st.text_area("Notes / availability / questions")

            submitted = st.form_submit_button("Submit individual registration")

            if submitted:
                if not driver_name or not email:
                    st.error("Driver name and email are required.")
                    return True, {}, ["Driver name and email are required."]

                payload = {
                    "registration_type": "multi_route",
                    "registration_route": "individual_driver",
                    "driver_name": driver_name,
                    "email": email,
                    "phone": phone,
                    "experience": experience,
                    "preferred_car": preferred_car,
                    "backup_car": backup_car,
                    "can_be_team_captain": can_be_team_captain,
                    "preferred_teammate": preferred_teammate,
                    "pairing_status": "waiting",
                    "notes": notes,
                }

                return True, add_submission_metadata(event, payload), []

        else:
            st.markdown("### Keep me updated")

            name = st.text_input("Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone")

            interest_level = st.selectbox(
                "Interest level",
                [
                    "Just interested",
                    "Maybe want to race",
                    "Want to race but need more info",
                    "Want to watch / spectate",
                ],
            )

            experience = st.selectbox(
                "Sim racing experience",
                ["Not sure", *experience_options],
            )

            consent_to_contact = st.checkbox(
                "I agree that SRCS may contact me about this event.",
                value=True,
            )

            notes = st.text_area("Questions / notes")

            submitted = st.form_submit_button("Keep me updated")

            if submitted:
                if not name or not email:
                    return True, {}, ["Name and email are required."]

                if not consent_to_contact:
                    return True, {}, ["Please confirm that SRCS may contact you about this event."]

                payload = {
                    "registration_type": "multi_route",
                    "registration_route": "interest_only",
                    "name": name,
                    "email": email,
                    "phone": phone,
                    "interest_level": interest_level,
                    "experience": experience,
                    "consent_to_contact": consent_to_contact,
                    "lead_status": "new",
                    "contact_status": "not_contacted",
                    "follow_up_priority": "normal",
                    "notes": notes,
                }

                return True, add_submission_metadata(event, payload), []   

    return False, {}, []                