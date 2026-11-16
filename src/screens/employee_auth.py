
import streamlit as st
import bcrypt

from src.database.supabase_client import supabase


def employee_auth():

    st.title("Employee Login")

    action = st.radio(
        "Choose an option",
        ["Login", "Create Password"],
        horizontal=True
    )

    if action == "Create Password":

        st.subheader("First-Time Employee Registration")

        with st.form("create_password_form"):

            employee_id = st.text_input("Employee ID")
            email = st.text_input("Registered Email")
            password = st.text_input(
                "Create Password", type="password"
            )
            confirm_password = st.text_input(
                "Confirm Password", type="password"
            )

            submit = st.form_submit_button(
                "Create Password",
                width="stretch"
            )

            if submit:

                if not all([
                    employee_id, email, password, confirm_password
                ]):
                    st.error("Please fill all fields.")

                elif password != confirm_password:
                    st.error("Passwords do not match.")

                elif len(password) < 8:
                    st.error("Password must contain at least 8 characters.")

                else:
                    response = supabase.table("employees").select(
                        "id, email, password_hash"
                    ).eq(
                        "employee_id", employee_id
                    ).eq(
                        "email", email
                    ).execute()

                    if not response.data:
                        st.error("Employee ID or email is incorrect.")

                    elif response.data[0].get("password_hash"):
                        st.warning("Password has already been created.")

                    else:
                        password_hash = bcrypt.hashpw(
                            password.encode("utf-8"),
                            bcrypt.gensalt()
                        ).decode("utf-8")

                        supabase.table("employees").update({
                            "password_hash": password_hash
                        }).eq(
                            "id", response.data[0]["id"]
                        ).execute()

                        st.success(
                            "Password created successfully! Please log in."
                        )

    else:

        st.subheader("Employee Login")

        with st.form("employee_login_form"):

            employee_id = st.text_input("Employee ID")
            password = st.text_input(
                "Password", type="password"
            )

            submit = st.form_submit_button(
                "Login",
                width="stretch"
            )

            if submit:

                response = supabase.table("employees").select(
                    "id, employee_id, full_name, password_hash"
                ).eq(
                    "employee_id", employee_id
                ).execute()

                if not response.data:
                    st.error("Employee not found.")

                else:
                    employee = response.data[0]
                    stored_hash = employee.get("password_hash")

                    if not stored_hash:
                        st.warning(
                            "Please create your password first."
                        )

                    elif bcrypt.checkpw(
                        password.encode("utf-8"),
                        stored_hash.encode("utf-8")
                    ):
                        st.session_state["authenticated_employee"] = {
                            "id": employee["id"],
                            "employee_id": employee["employee_id"],
                            "full_name": employee["full_name"]
                        }

                        st.session_state["login_type"] = "employee"
                        st.success("Login successful!")
                        st.rerun()

                    else:
                        st.error("Incorrect password.")
