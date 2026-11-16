
import cv2
import face_recognition
import streamlit as st
from datetime import datetime
from src.database.supabase_client import supabase


def mark_attendance(employee):

    now = datetime.now().astimezone()
    today = now.date().isoformat()

    # Check existing attendance record
    response = supabase.table("attendance").select("*").eq(
        "employee_id", employee["id"]
    ).eq(
        "attendance_date", today
    ).execute()

    if not response.data:

        # First scan: Check-in
        supabase.table("attendance").insert({
            "employee_id": employee["id"],
            "attendance_date": today,
            "check_in": now.isoformat(),
            "status": "Present"
        }).execute()

        st.success(
            f"Check-in successful: {now.strftime('%I:%M:%S %p')}"
        )

    else:

        attendance = response.data[0]

        if attendance.get("check_out"):
            st.warning("You have already checked out today!")
            return

        # Second scan: Check-out
        check_in = datetime.fromisoformat(attendance["check_in"])

        working_hours = round(
            (now - check_in).total_seconds() / 3600, 2
        )

        supabase.table("attendance").update({
            "check_out": now.isoformat(),
            "working_hours": working_hours
        }).eq("id", attendance["id"]).execute()

        st.success(
            f"Check-out successful: {now.strftime('%I:%M:%S %p')}"
        )

        st.info(f"Total working hours: {working_hours}")


def employee_attendance():

    response = supabase.table("employees").select(
        "id, employee_id, full_name, face_encoding"
    ).execute()

    employees = [
        emp for emp in response.data
        if emp.get("face_encoding")
    ]

    if not employees:
        st.error("No registered employee faces found!")
        return

    known_encodings = [
        emp["face_encoding"] for emp in employees
    ]

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        st.error("Camera not detected!")
        return

    st.info("Look at the camera to mark attendance.")
    st.caption("Press Q in the camera window to exit.")

    attendance_marked = False

    try:
        while True:

            success, frame = camera.read()

            if not success:
                st.error("Camera capture failed!")
                break

            rgb_frame = cv2.cvtColor(
                frame, cv2.COLOR_BGR2RGB
            )

            face_locations = face_recognition.face_locations(
                rgb_frame
            )

            label = "No face detected"

            if len(face_locations) == 1:

                encodings = face_recognition.face_encodings(
                    rgb_frame, face_locations
                )

                if encodings:

                    distances = face_recognition.face_distance(
                        known_encodings, encodings[0]
                    )

                    best_match = distances.argmin()

                    if distances[best_match] < 0.5:

                        employee = employees[best_match]
                        label = employee["full_name"]

                        if not attendance_marked:
                            mark_attendance(employee)
                            attendance_marked = True

                    else:
                        label = "Unknown Employee"

            elif len(face_locations) > 1:
                label = "Only one person at a time"

            cv2.putText(
                frame,
                label,
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2
            )

            cv2.imshow("Employee Attendance", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    employee_attendance()
