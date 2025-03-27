  **Attendance System Using Face Recognition**

This is a Face Recognition-based Attendance System that automates student attendance marking using facial recognition technology. The system captures and processes student images to identify them and mark attendance efficiently.

🔹 Features
Face Detection & Recognition: Uses OpenCV and face recognition algorithms.

Real-time Attendance Marking: Automatically updates attendance when a registered face is detected.

Database Integration: Stores attendance records for future reference.

Duplicate Check: Prevents multiple attendance markings for the same session.

User-friendly Interface: Simple and easy-to-use UI for managing students and attendance.

🔹 Technologies Used
Python

OpenCV & Face Recognition (for image processing)

Firebase (for database and storage)


🔹 How It Works
Student Registration: Add students with their images to the database.

Face Detection: The system captures a real-time image and compares it with stored data.

Attendance Marking: If a match is found, attendance is marked; otherwise, it's flagged as unknown.

View Records: Admin can monitor attendance reports.

🔹 Setup Instructions
1.Clone the repository:
git clone https://github.com/bavindushan/Attendent-System-using-Face_Recognize.git

2.Install dependencies:
pip install -r requirements.txt

3.Add your Firebase Service Key (serviceAccountKey.json) in a secure location.

4.Run the application:
python app.py

🔹 License
This project is open-source and free to use.
