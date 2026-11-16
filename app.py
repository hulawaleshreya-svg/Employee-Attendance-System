
import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.admin_screen import admin_screen
from src.screens.employee_screen import employee_screen
from src.screens.employee_auth import employee_auth


st.set_page_config(
    page_title="Employee Attendance System",
    page_icon="👩‍💻",
    layout="wide"
)

if "login_type" not in st.session_state:
    st.session_state["login_type"] = None

if "authenticated_employee" not in st.session_state:
    st.session_state["authenticated_employee"] = None


if st.session_state["login_type"] is None:
    home_screen()

elif st.session_state["login_type"] == "admin":
    admin_screen()

elif st.session_state["login_type"] == "employee":

    if st.session_state["authenticated_employee"]:
        employee_screen()
    else:
        employee_auth()
