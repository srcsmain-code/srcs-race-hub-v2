from __future__ import annotations

from pathlib import Path
import streamlit as st


def show_header(title: str, subtitle: str | None = None) -> None:
    header_path = Path("assets/headers/header_HOME.png")
    if header_path.exists():
        st.image(str(header_path), use_container_width=True)
    st.title(title)
    if subtitle:
        st.caption(subtitle)
