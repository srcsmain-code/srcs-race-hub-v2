from __future__ import annotations

import streamlit as st

from src.events import load_event
from src.github_writer import commit_json_to_github, github_configured, registration_folder
from src.registration_forms import render_registration_form
from src.ui_components import show_header


DEFAULT_EVENT_ID = "2026_spa_3h_endurance"


def get_event_id() -> str:
    return st.query_params.get("event_id", DEFAULT_EVENT_ID)


def render() -> None:
    event_id = get_event_id()
    event = load_event(event_id)

    event_name = event.get("event_name", "SRCS Event")
    event_short_name = event.get("event_short_name", event_name)

    show_header(
    f"Register for {event_name}",
    "Creates a pending registration submission",
    banner_image=event.get("banner_image"),
)

    if not event.get("registration_open", False):
        st.warning("Registration for this event is currently closed.")
        return

    if github_configured():
        st.success("Registration storage is connected to GitHub.")
    else:
        st.warning("GitHub storage is not configured yet. Add Streamlit secrets before accepting live registrations.")

    submitted, payload, errors = render_registration_form(event)

    if not submitted:
        return

    if errors:
        for error in errors:
            st.error(error)
        return

    if payload is None:
        st.error("Registration could not be prepared.")
        return

    if not github_configured():
        st.error("GitHub storage is not configured. Please check Streamlit secrets.")
        return

    submission_id = payload.get("submission_id", "")

    if not submission_id:
        st.error("Registration is missing a submission ID.")
        return

    github_path = f"{registration_folder(event_id, 'pending')}/{submission_id}.json"

    try:
        commit_json_to_github(
            path=github_path,
            payload=payload,
            message=f"Add pending registration for {event_short_name}: {submission_id}",
        )
        st.success("Registration submitted as pending.")
        st.code(github_path)
    except Exception as exc:
        st.error("Registration could not be saved to GitHub.")
        st.exception(exc)