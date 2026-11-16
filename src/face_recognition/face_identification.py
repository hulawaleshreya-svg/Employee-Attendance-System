
import cv2
import face_recognition
from src.database.supabase_client import supabase


def identify_employee():

    # Fetch registered employees and their face encodings
    response = supabase.table("employees").select(
        "id, employee_id, full_name, face_encoding"
    ).execute()

    employees = [
        employee for employee in response.data
        if employee.get("face_encoding")
    ]

    if not employees:
        print("No registered employee faces found!")
        return

    known_encodings = [
        employee["face_encoding"] for employee in employees
    ]

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("Camera not detected!")
        return

    print("Look at the camera. Press Q to exit.")

    while True:
        success, frame = camera.read()

        if not success:
            print("Camera capture failed!")
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)

        if len(face_locations) == 1:
            face_encodings = face_recognition.face_encodings(
                rgb_frame, face_locations
            )

            if face_encodings:
                matches = face_recognition.compare_faces(
                    known_encodings,
                    face_encodings[0],
                    tolerance=0.5
                )

                distances = face_recognition.face_distance(
                    known_encodings,
                    face_encodings[0]
                )

                if any(matches):
                    best_match = distances.argmin()

                    if matches[best_match]:
                        employee = employees[best_match]
                        label = employee["full_name"]
                    else:
                        label = "Unknown Employee"
                else:
                    label = "Unknown Employee"

                cv2.putText(
                    frame, label, (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1, (0, 255, 0), 2
                )

        elif len(face_locations) > 1:
            label = "Multiple faces detected"
            cv2.putText(
                frame, label, (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8, (0, 0, 255), 2
            )

        cv2.imshow("Employee Face Identification", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    identify_employee()
