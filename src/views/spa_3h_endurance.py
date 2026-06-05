from __future__ import annotations

import streamlit as st

from src.ui_components import show_header


def render() -> None:
    show_header("The SRCS Spa 3-hour Endurance", "GT3 team endurance event")

    st.markdown(
        """
        **Format**

        - 2 drivers per team/car
        - Cars: Porsche, Mercedes, Lamborghini, Ferrari
        - Tire wear: On
        - Pitstops: On
        - Collision: On
        - Penalties: On
        - Damage: On
        - Race duration: 3 hours
        - 24h setting: day-night-day
        - Track: Spa-Francorchamps

        Registration is handled through the Spa 3H registration form.
        """
    )
