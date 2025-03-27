import cv2
import face_recognition
import pickle
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Import student images
folderPath = 'images'
pathList = os.listdir(folderPath)
imgList = []
studentIds = []

for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])

print(studentIds)

def findEncodings(imagesList):
    """Encodes face images into numerical data."""
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(img)
        if encodings:  # Ensure face is detected
            encodeList.append(encodings[0])
        else:
            print("⚠️ Warning: No face found in an image. Skipping...")
    return encodeList

print("Encoding Started....")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding Complete")

# Save encoded data locally
with open("EncodeFile.p", 'wb') as file:
    pickle.dump(encodeListKnownWithIds, file)

print("File saved successfully!")

# Store student data in Firestore
for student_id in studentIds:
    student_data = {
        "id": student_id,
        "name": "Unknown",  # Placeholder, can be updated later
        "major": "Unknown",  # Placeholder, can be updated later
        "starting_year": 2023,  # Placeholder, can be updated later
        "total_attendance": 0,
        "standing": "Unknown",  # Placeholder, can be updated later
        "year": 1,  # Placeholder, can be updated later
        "last_attendance_time": None
    }
    db.collection("Students").document(student_id).set(student_data)

print("Student data stored in Firestore!")
