from __future__ import annotations

import streamlit as st

from config.constants import DRIVER_PATHWAYS
from src.ui_components import show_header

st.set_page_config(page_title="SRCS Rookie Intake", layout="wide")
show_header("SRCS Rookie Intake", "Placeholder for August lead-generation pilot")

st.markdown(
    """
This page is reserved for the Race Square / SRCS lead-generation pilot.

Planned fields:
- Name
- Email / WhatsApp
- Venue preference
- Experience level
- Interest area
- Driver pathway preference
- Lead source: QR, RS mailer, narrowcasting, staff referral, friend, social
- Consent and follow-up status
"""
)

with st.form("rookie_intake_placeholder"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    venue = st.selectbox("Preferred venue", ["Utrecht", "Rotterdam", "Zandvoort", "Zwolle", "Amsterdam", "Eindhoven", "Kerkrade"])
    pathway = st.selectbox("Interest", DRIVER_PATHWAYS)
    st.form_submit_button("Placeholder submit")
