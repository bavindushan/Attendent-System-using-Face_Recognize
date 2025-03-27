import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Student Data
data = {
    "101": {
        "name": "Bavindu Shan",
        "major": "Software Engineering",
        "starting_year": 2020,
        "total_attendance": 7,
        "standing": "G",
        "year": 4,
        "last_attendance_time": "2025-03-27 00:54:34"
    },
    "102": {
        "name": "Ronaldo",
        "major": "Data Science",
        "starting_year": 2021,
        "total_attendance": 6,
        "standing": "G",
        "year": 1,
        "last_attendance_time": "2025-03-27 00:54:34"
    }
}

# Store data in Firestore
for student_id, details in data.items():
    db.collection("Students").document(student_id).set(details)

print("Data added to Firestore!")
