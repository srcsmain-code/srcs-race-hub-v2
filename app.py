from __future__ import annotations

import streamlit as st

from src.views.home import render as render_home
from src.views.season_2026 import render as render_season_2026
from src.views.standings import render as render_standings
from src.views.register_event import render as render_register_event
from src.views.rookie_intake import render as render_rookie_intake
from src.views.admin import render as render_admin


st.set_page_config(page_title="SRCS Race Hub v2", layout="wide")


def is_admin_logged_in() -> bool:
    return bool(st.session_state.get("admin_logged_in", False))


def admin_login_box() -> None:
    st.sidebar.divider()
    st.sidebar.subheader("Admin")

    if is_admin_logged_in():
        st.sidebar.success("Admin mode active")
        if st.sidebar.button("Log out"):
            st.session_state["admin_logged_in"] = False
            st.rerun()
        return

    with st.sidebar.form("admin_login_form"):
        password = st.text_input("Admin password", type="password")
        submitted = st.form_submit_button("Unlock admin")

    if submitted:
        expected = st.secrets.get("ADMIN_PASSWORD", "")
        if expected and password == expected:
            st.session_state["admin_logged_in"] = True
            st.rerun()
        else:
            st.sidebar.error("Incorrect password")


def get_url_mode() -> str:
    mode = st.query_params.get("mode", "public")
    allowed_modes = {"public", "register", "register_spa_3h", "admin", "event"}
    return mode if mode in allowed_modes else "public"


def render_registration_only_mode() -> None:
    render_register_event()


def render_admin_mode() -> None:
    if not is_admin_logged_in():
        st.title("SRCS Race Hub Admin")
        st.warning("Admin access required.")
        st.info("Enter the admin password in the sidebar to continue.")
        admin_login_box()
        return

    admin_pages = {
        "Admin Dashboard": render_admin,
        "Event Registration Form": render_register_event,
        "Events": render_events,
        "Event Detail": render_event_detail,
        "Rookie Intake": render_rookie_intake,
        "Standings": render_standings,
    }

    st.sidebar.title("SRCS Admin")
    selected = st.sidebar.radio("Admin menu", list(admin_pages.keys()))
    admin_login_box()
    admin_pages[selected]()


def render_public_mode() -> None:
    public_pages = {
        "Home": render_home,
        "Season 2026": render_season_2026,
        "Standings": render_standings,
        "Events": render_events,
        "Register Event": render_register_event,
        "Rookie Intake": render_rookie_intake,
    }

    st.sidebar.title("SRCS Race Hub")
    selected = st.sidebar.radio("Menu", list(public_pages.keys()))
    admin_login_box()

    if is_admin_logged_in():
        st.sidebar.divider()
        if st.sidebar.button("Go to Admin mode"):
            st.query_params["mode"] = "admin"
            st.rerun()

    public_pages[selected]()


mode = get_url_mode()

if mode in {"register", "register_spa_3h"}:
    render_registration_only_mode()
elif mode == "event":
    render_event_detail()
elif mode == "admin":
    render_admin_mode()
else:
    render_public_mode()