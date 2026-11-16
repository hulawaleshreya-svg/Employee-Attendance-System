
import streamlit as st
import pandas as pd

from datetime import date
from src.ui.base_layout import style_background_dashboard
from src.screens.employee_registration import employee_registration
from src.database.supabase_client import supabase


# ---------------- ATTENDANCE MANAGEMENT ----------------

def view_attendance_records():

    st.subheader("Employee Attendance Records")

    response = supabase.table("attendance").select("*").order(
        "attendance_date", desc=True
    ).execute()

    attendance_records = response.data

    if not attendance_records:
        st.info("No attendance records found.")
        return

    employee_response = supabase.table("employees").select(
        "id, employee_id, full_name"
    ).execute()

    employees = {emp["id"]: emp for emp in employee_response.data}

    records = []

    for attendance in attendance_records:

        employee = employees.get(attendance["employee_id"], {})

        check_in = attendance.get("check_in")
        check_out = attendance.get("check_out")

        if check_in:
            check_in = pd.to_datetime(check_in, utc=True).tz_convert(
                "Asia/Kolkata"
            ).strftime("%I:%M:%S %p")

        if check_out:
            check_out = pd.to_datetime(check_out, utc=True).tz_convert(
                "Asia/Kolkata"
            ).strftime("%I:%M:%S %p")

        records.append({
            "Employee ID": employee.get("employee_id", "N/A"),
            "Employee Name": employee.get("full_name", "N/A"),
            "Date": attendance.get("attendance_date"),
            "Check-in": check_in,
            "Check-out": check_out,
            "Working Hours": attendance.get("working_hours"),
            "Status": attendance.get("status")
        })

    df = pd.DataFrame(records)

    st.markdown("### Search Employee")

    search_name = st.text_input(
        "Enter employee name",
        placeholder="Search by employee name..."
    )

    if search_name:
        df = df[df["Employee Name"].str.contains(
            search_name, case=False, na=False
        )]

    st.markdown("### Filter by Date")

    selected_date = st.date_input(
        "Select attendance date",
        value=None
    )

    if selected_date:
        df = df[
            pd.to_datetime(df["Date"]).dt.date == selected_date
        ]

    st.markdown("### Attendance Details")

    st.dataframe(df, width="stretch", hide_index=True)

    st.success(f"Total attendance records: {len(df)}")

    csv_data = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Download Attendance Report (CSV)",
        data=csv_data,
        file_name="employee_attendance_report.csv",
        mime="text/csv"
    )


# ---------------- PAYROLL MANAGEMENT ----------------

def manage_payroll():

    st.subheader("Employee Payroll Management")

    employee_response = supabase.table("employees").select(
        "id, employee_id, full_name, hourly_rate"
    ).execute()

    employees = employee_response.data

    if not employees:
        st.warning("No employees registered.")
        return

    employee_options = {
        f'{emp["full_name"]} (ID: {emp["employee_id"]})': emp
        for emp in employees
    }

    selected_employee = st.selectbox(
        "Select Employee",
        list(employee_options.keys())
    )

    employee = employee_options[selected_employee]

    col1, col2 = st.columns(2)

    with col1:
        selected_month = st.selectbox(
            "Select Month",
            list(range(1, 13)),
            index=date.today().month - 1
        )

    with col2:
        selected_year = st.number_input(
            "Select Year",
            min_value=2020,
            max_value=2100,
            value=date.today().year,
            step=1
        )

    next_month = date(
        int(selected_year) + (selected_month // 12),
        (selected_month % 12) + 1,
        1
    )

    response = supabase.table("attendance").select(
        "working_hours"
    ).eq(
        "employee_id", employee["id"]
    ).gte(
        "attendance_date",
        f"{int(selected_year)}-{int(selected_month):02d}-01"
    ).lt(
        "attendance_date",
        next_month.isoformat()
    ).execute()

    total_hours = sum(
        float(record["working_hours"] or 0)
        for record in response.data
    )

    hourly_rate = float(employee["hourly_rate"] or 0)
    total_salary = round(total_hours * hourly_rate, 2)

    st.divider()

    st.metric("Total Working Hours", f"{total_hours:.2f} Hours")
    st.metric("Hourly Rate", f"₹{hourly_rate:.2f}")
    st.metric("Total Salary", f"₹{total_salary:.2f}")

    st.divider()

    if st.button("Generate Payroll", width="stretch"):

        existing = supabase.table("payroll").select("id").eq(
            "employee_id", employee["id"]
        ).eq(
            "month", selected_month
        ).eq(
            "year", selected_year
        ).execute()

        if existing.data:

            supabase.table("payroll").update({
                "total_working_hours": total_hours,
                "hourly_rate": hourly_rate,
                "total_salary": total_salary
            }).eq("id", existing.data[0]["id"]).execute()

            st.success("Payroll updated successfully!")

        else:

            supabase.table("payroll").insert({
                "employee_id": employee["id"],
                "month": selected_month,
                "year": selected_year,
                "total_working_hours": total_hours,
                "hourly_rate": hourly_rate,
                "total_salary": total_salary,
                "payment_status": "Pending"
            }).execute()

            st.success("Payroll generated successfully!")

    st.divider()

    st.markdown("### Payroll Records")

    payroll_response = supabase.table("payroll").select("*").eq(
        "employee_id", employee["id"]
    ).order("year", desc=True).execute()

    if payroll_response.data:

        payroll_df = pd.DataFrame(payroll_response.data)

        st.dataframe(payroll_df, width="stretch", hide_index=True)

        payroll_ids = {
            f'Payroll ID: {record["id"]} - '
            f'{record["month"]}/{record["year"]}': record
            for record in payroll_response.data
        }

        selected_payroll = st.selectbox(
            "Select payroll to update payment status",
            list(payroll_ids.keys())
        )

        record = payroll_ids[selected_payroll]

        new_status = st.selectbox(
            "Payment Status",
            ["Pending", "Paid"],
            index=0 if record["payment_status"] == "Pending" else 1
        )

        if st.button("Update Payment Status"):
            supabase.table("payroll").update({
                "payment_status": new_status,
                "payment_date": (
                    date.today().isoformat()
                    if new_status == "Paid" else None
                )
            }).eq("id", record["id"]).execute()

            st.success("Payment status updated!")
            st.rerun()

    else:
        st.info("No payroll records found for this employee.")


# ---------------- EMPLOYEE MANAGEMENT ----------------

def manage_employee_details():

    st.subheader("Manage Employee Details")

    response = supabase.table("employees").select(
        "id, employee_id, full_name, email, phone, department, designation, hourly_rate"
    ).execute()

    employees = response.data

    if not employees:
        st.info("No employees registered.")
        return

    df = pd.DataFrame(employees)

    st.markdown("### Search Employees")

    search = st.text_input(
        "Search by employee name or ID",
        placeholder="Enter name or employee ID..."
    )

    filtered_df = df.copy()

    if search:
        filtered_df = filtered_df[
            filtered_df["full_name"].astype(str).str.contains(
                search, case=False, na=False
            ) |
            filtered_df["employee_id"].astype(str).str.contains(
                search, case=False, na=False
            )
        ]

    st.dataframe(
        filtered_df.drop(columns=["id"]),
        width="stretch",
        hide_index=True
    )

    st.success(f"Total employees: {len(filtered_df)}")

    st.divider()

    st.markdown("### Edit Employee Details")

    employee_options = {
        f'{emp["full_name"]} (ID: {emp["employee_id"]})': emp
        for emp in employees
    }

    selected = st.selectbox(
        "Select employee to edit",
        list(employee_options.keys())
    )

    employee = employee_options[selected]

    with st.form("edit_employee_form"):

        full_name = st.text_input(
            "Full Name", value=employee.get("full_name") or ""
        )

        email = st.text_input(
            "Email", value=employee.get("email") or ""
        )

        phone = st.text_input(
            "Phone", value=employee.get("phone") or ""
        )

        department = st.text_input(
            "Department", value=employee.get("department") or ""
        )

        designation = st.text_input(
            "Designation", value=employee.get("designation") or ""
        )

        hourly_rate = st.number_input(
            "Hourly Rate (₹)",
            min_value=0.0,
            value=float(employee.get("hourly_rate") or 0),
            step=10.0
        )

        update_button = st.form_submit_button(
            "Update Employee Details",
            width="stretch"
        )

        if update_button:

            if not full_name.strip():
                st.error("Employee name cannot be empty.")

            else:
                supabase.table("employees").update({
                    "full_name": full_name.strip(),
                    "email": email.strip(),
                    "phone": phone.strip(),
                    "department": department.strip(),
                    "designation": designation.strip(),
                    "hourly_rate": hourly_rate
                }).eq("id", employee["id"]).execute()

                st.success("Employee details updated successfully!")
                st.rerun()

    st.divider()

    st.markdown("### Delete Employee")

    delete_confirm = st.checkbox(
        f"I confirm that I want to delete {employee['full_name']}."
    )

    if st.button("Delete Employee", width="stretch"):

        if not delete_confirm:
            st.warning("Please confirm before deleting.")

        else:

            attendance_check = supabase.table("attendance").select(
                "id"
            ).eq("employee_id", employee["id"]).limit(1).execute()

            payroll_check = supabase.table("payroll").select(
                "id"
            ).eq("employee_id", employee["id"]).limit(1).execute()

            if attendance_check.data or payroll_check.data:
                st.error(
                    "This employee has attendance or payroll records. "
                    "Deletion is blocked to preserve historical records."
                )

            else:
                supabase.table("employees").delete().eq(
                    "id", employee["id"]
                ).execute()

                st.success("Employee deleted successfully!")
                st.rerun()


# ---------------- ADMIN DASHBOARD ----------------

def admin_screen():

    style_background_dashboard()

    st.title("Admin Dashboard")
    st.write("Welcome to the Admin Portal.")

    st.subheader("Admin Activities")

    if st.button("Register New Employee", width="stretch"):
        st.session_state["admin_page"] = "register"

    if st.button("Manage Employee Details", width="stretch"):
        st.session_state["admin_page"] = "manage"

    if st.button("View Attendance Records", width="stretch"):
        st.session_state["admin_page"] = "attendance"

    if st.button("Manage Payroll", width="stretch"):
        st.session_state["admin_page"] = "payroll"

    st.divider()

    page = st.session_state.get("admin_page")

    if page == "register":
        employee_registration()

    elif page == "manage":
        manage_employee_details()
        st.success("Employee Management Function Opened!")
    elif page == "attendance":
        view_attendance_records()

    elif page == "payroll":
        manage_payroll()

    if st.button("Back to Home"):
        st.session_state["login_type"] = None
        st.session_state["admin_page"] = None
        st.rerun()
