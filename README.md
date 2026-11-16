# Employee Attendance System

## Project Overview
The Employee Attendance System is a Python-based application that uses face recognition to manage employee attendance and payroll records. It provides separate portals for administrators and employees.

## Features

### Admin Portal
- Register new employees.
- View, search, update and manage employee details.
- View and filter attendance records.
- Download attendance records as CSV.
- Calculate monthly working hours.
- Generate and manage employee payroll.
- Track payment status.

### Employee Portal
- Create an employee password and log in.
- View personal attendance history.
- Check monthly working hours.
- View salary and payroll details.

### Face Recognition
- Register employee faces using a webcam.
- Identify registered employees through face recognition.
- Record employee check-in and check-out times.
- Calculate working hours automatically.

## Technologies Used

- **Programming Language:** Python
- **Frontend:** Streamlit
- **Face Recognition:** OpenCV, face_recognition
- **Database:** Supabase
- **Authentication:** bcrypt
- **Data Processing:** Pandas
- **Configuration:** python-dotenv

## Project Structure

```text
Employee-Attendance-System/
│
├── src/
│   ├── components/
│   ├── database/
│   ├── face_recognition/
│   ├── screens/
│   └── ui/
│
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/hulawaleshreya-svg/Employee-Attendance-System.git
```

### 2. Open the Project Folder

```bash
cd Employee-Attendance-System
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

For Windows:

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the project root and add your Supabase project URL and API key:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
```

Use your own Supabase credentials. Never upload the `.env` file to GitHub.

### 7. Run the Application

```bash
streamlit run app.py
```

## Database

The application uses Supabase to store:
- Employee details
- Face encodings
- Attendance records
- Payroll information

## Future Enhancements

- Email OTP verification for employee registration.
- Improved biometric security and liveness detection.
- More detailed attendance and payroll reports.

## Author

**Shreya Hulawale**

GitHub: https://github.com/hulawaleshreya-svg
