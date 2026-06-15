from __future__ import annotations

from pathlib import Path
import streamlit as st


def show_header(
    title: str,
    subtitle: str | None = None,
    banner_image: str | None = None,
) -> None:
    if banner_image:
        banner_path = Path(banner_image)
        if banner_path.exists():
            st.image(str(banner_path), use_container_width=True)
        else:
            st.warning(f"Banner image not found: {banner_image}")
    else:
        header_path = Path("assets/headers/header_HOME.png")
        if header_path.exists():
            st.image(str(header_path), use_container_width=True)

    st.title(title)
    if subtitle:
        st.caption(subtitle)