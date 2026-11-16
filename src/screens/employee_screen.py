
import streamlit as st
import pandas as pd

from datetime import date
from src.ui.base_layout import style_background_dashboard
from src.database.supabase_client import supabase


def employee_screen():

    style_background_dashboard()

    # Get logged-in employee
    employee = st.session_state.get("authenticated_employee")

    if not employee:
        st.warning("Please log in first.")
        st.session_state["login_type"] = None
        st.rerun()
        return

    employee_db_id = employee["id"]

    st.title("Employee Dashboard")
    st.write(f"Welcome, {employee['full_name']}!")

    st.write(f"Employee ID: {employee['employee_id']}")

    st.divider()

    # ---------------- ATTENDANCE HISTORY ----------------

    st.subheader("My Attendance Records")

    attendance_response = supabase.table("attendance").select(
        "attendance_date, check_in, check_out, working_hours, status"
    ).eq(
        "employee_id", employee_db_id
    ).order(
        "attendance_date", desc=True
    ).execute()

    attendance_records = attendance_response.data

    if attendance_records:

        attendance_df = pd.DataFrame(attendance_records)

        for column in ["check_in", "check_out"]:
            attendance_df[column] = attendance_df[column].apply(
                lambda value: (
                    pd.to_datetime(value, utc=True)
                    .tz_convert("Asia/Kolkata")
                    .strftime("%I:%M:%S %p")
                    if value else None
                )
            )

        attendance_df = attendance_df.rename(columns={
            "attendance_date": "Date",
            "check_in": "Check-in",
            "check_out": "Check-out",
            "working_hours": "Working Hours",
            "status": "Status"
        })

        st.dataframe(
            attendance_df,
            width="stretch",
            hide_index=True
        )

    else:
        st.info("No attendance records found.")

    st.divider()

    # ---------------- MONTHLY SUMMARY ----------------

    st.subheader("My Monthly Summary")

    today = date.today()

    first_day = date(today.year, today.month, 1)

    if today.month == 12:
        next_month = date(today.year + 1, 1, 1)
    else:
        next_month = date(today.year, today.month + 1, 1)

    monthly_response = supabase.table("attendance").select(
        "working_hours"
    ).eq(
        "employee_id", employee_db_id
    ).gte(
        "attendance_date", first_day.isoformat()
    ).lt(
        "attendance_date", next_month.isoformat()
    ).execute()

    total_hours = sum(
        float(record["working_hours"] or 0)
        for record in monthly_response.data
    )

    st.metric(
        "Total Working Hours",
        f"{total_hours:.2f} Hours"
    )

    st.divider()

    # ---------------- PAYROLL DETAILS ----------------

    st.subheader("My Salary Details")

    payroll_response = supabase.table("payroll").select(
        "month, year, total_working_hours, hourly_rate, "
        "total_salary, payment_status, payment_date"
    ).eq(
        "employee_id", employee_db_id
    ).order(
        "year", desc=True
    ).execute()

    if payroll_response.data:

        payroll_df = pd.DataFrame(payroll_response.data)

        st.dataframe(
            payroll_df,
            width="stretch",
            hide_index=True
        )

    else:
        st.info("No payroll records found.")

    st.divider()

    # ---------------- LOGOUT ----------------

    if st.button("Logout", width="stretch"):

        st.session_state["authenticated_employee"] = None
        st.session_state["login_type"] = None

        st.rerun()
