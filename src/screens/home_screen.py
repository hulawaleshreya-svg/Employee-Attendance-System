
import streamlit as st

from src.components.header import header_home
from src.ui.base_layout import style_base_layout, style_background_home


def home_screen():

    style_base_layout()
    style_background_home()

    header_home()

    st.markdown(
        "<p style='text-align:center; color:white; font-size:18px;'>"
        "Smart Employee Attendance and Working Hours Management"
        "</p>",
        unsafe_allow_html=True
    )

    st.write("")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Admin Portal", use_container_width=True):
            st.session_state["login_type"] = "admin"
            st.rerun()

    with col2:
        if st.button("Employee Portal", use_container_width=True):
            st.session_state["login_type"] = "employee"
            st.rerun()
