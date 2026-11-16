
import streamlit as st
from src.database.supabase_client import supabase

def employee_registration():

    st.title("Register New Employee")
    st.write("Enter the employee details below.")

    with st.form("employee_registration_form"):

        employee_id = st.text_input("Employee ID")
        full_name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        phone = st.text_input("Phone Number")
        department = st.text_input("Department")
        designation = st.text_input("Designation")
        hourly_rate = st.number_input(
            "Hourly Rate (₹)",
            min_value=0.0,
            step=10.0
        )

        submitted = st.form_submit_button(
            "Register Employee",
            use_container_width=True
        )

        if submitted:

            if not employee_id or not full_name or not email:
                st.error("Please fill in Employee ID, Name and Email.")

            else:
                try:
                    supabase.table("employees").insert({
                        "employee_id": employee_id,
                        "full_name": full_name,
                        "email": email,
                        "phone": phone,
                        "department": department,
                        "designation": designation,
                        "hourly_rate": hourly_rate
                    }).execute()

                    st.success("Employee registered successfully!")

                except Exception as e:
                    st.error(f"Registration failed: {e}")
