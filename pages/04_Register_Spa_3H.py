from __future__ import annotations

import streamlit as st

from config.constants import ENDURANCE_CAR_CHOICES
from src.registrations import create_pending_spa_entry
from src.validation import is_valid_email, required_fields_present
from src.ui_components import show_header

st.set_page_config(page_title="Register — Spa 3H", layout="wide")
show_header("Register for The SRCS Spa 3-hour Endurance", "Creates a pending registration submission")

st.warning(
    "Starter mode: submissions are saved locally into data/registrations/pending. "
    "GitHub writes can be enabled later via Streamlit secrets."
)

with st.form("spa_3h_registration"):
    st.subheader("Team details")
    team_name = st.text_input("Team name")
    car_choice = st.selectbox("Preferred car", ENDURANCE_CAR_CHOICES)
    backup_car_choice = st.selectbox("Backup car", ENDURANCE_CAR_CHOICES)

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
    consent = st.checkbox("I confirm SRCS may contact us about this event and registration.")

    submitted = st.form_submit_button("Submit registration")

if submitted:
    payload = {
        "event_id": "spa_3h_endurance_2026",
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
    else:
        path = create_pending_spa_entry(payload)
        st.success("Registration submitted as pending.")
        st.code(str(path))
