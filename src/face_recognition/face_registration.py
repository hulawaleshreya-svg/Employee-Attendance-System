
import cv2
import face_recognition
from src.database.supabase_client import supabase


def register_employee_face(employee_id):

    # Check whether employee exists
    response = supabase.table("employees") \
        .select("id, employee_id, full_name") \
        .eq("employee_id", employee_id) \
        .execute()

    if not response.data:
        print("Employee not found!")
        return

    employee = response.data[0]

    # Open external USB webcam
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():
        print("Camera not detected!")
        return

    print("Look at the camera. Press SPACE to capture.")
    print("Press Q to cancel.")

    face_encoding = None

    while True:
        success, frame = camera.read()

        if not success:
            print("Camera capture failed!")
            break

        cv2.imshow("Employee Face Registration", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord('q'):
            break

        if key == 32:  # SPACE key
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_frame)

            if len(face_locations) != 1:
                print("Please ensure exactly one face is visible.")
                continue

            encodings = face_recognition.face_encodings(
                rgb_frame, face_locations
            )

            if len(encodings) == 1:
                face_encoding = encodings[0].tolist()
                print("Face captured successfully!")
                break

    camera.release()
    cv2.destroyAllWindows()

    if face_encoding is None:
        print("Face registration cancelled.")
        return

    # Save encoding in Supabase
    result = supabase.table("employees").update({
        "face_encoding": face_encoding
    }).eq("id", employee["id"]).execute()

    print("Face registered successfully for:", employee["full_name"])


if __name__ == "__main__":
    emp_id = input("Enter Employee ID: ")
    register_employee_face(emp_id)
