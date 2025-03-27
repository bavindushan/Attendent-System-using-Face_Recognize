import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta

# Initialize Firestore
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Load the encoding file
print("Loading Encoded File...")
with open('EncodeFile.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)

encodeListKnown, studentIds = encodeListKnownWithIds
print("Encoded File Loaded")

# Open Webcam
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('resources/background.PNG')

# Importing mode images to list
folderModePath = 'resources/mode'
modePathList = os.listdir(folderModePath)
imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]

modeType = 0
counter = 0
id = -1
imgStudent = []
attended_students = set()  # Track students who have marked attendance

while True:
    success, img = cap.read()
    if not success:
        print("⚠️ Error: Couldn't access webcam.")
        continue  # Skip this frame if there's an issue

    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrentFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurrentFrame)

    imgBackground[162:162 + 480, 55:55 + 640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)

        if not matches:
            continue  # Skip if no match found

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            student_id = studentIds[matchIndex]
            print(f"Recognized Student: {student_id}")

            # Fetch student data from Firestore
            student_ref = db.collection("Students").document(student_id)
            student_data = student_ref.get().to_dict()

            if student_data:
                # Prevent duplicate attendance within 5 minutes if not already attended
                last_attendance_time = student_data.get("last_attendance_time")
                if student_id in attended_students:
                    print(f"Attendance already marked for {student_id}. Skipping.")
                    continue  # Skip updating if attendance was already marked this session

                if last_attendance_time:
                    last_attendance_time = datetime.strptime(last_attendance_time, "%Y-%m-%d %H:%M:%S")
                    if datetime.now() - last_attendance_time < timedelta(minutes=5):
                        print(f"Skipping update for {student_id}, already marked recently.")
                        continue  # Skip updating if attendance was marked recently

                # Update Attendance
                new_attendance = student_data.get("total_attendance", 0) + 1
                student_ref.update({
                    "total_attendance": new_attendance,
                    "last_attendance_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
                print(f"Updated Attendance for {student_id}")
                attended_students.add(student_id)  # Add student to attended set
            else:
                print(f"⚠️ Student {student_id} not found in Firestore.")
                continue  # Skip if student data is not found in Firestore

            # Draw bounding box around detected face
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)
            id = studentIds[matchIndex]

            if counter == 0:
                counter = 1
                modeType = 1  # Change to the "attendance" mode

    if counter != 0:
        if counter == 1:
            # Get the Data
            studentInfo = db.collection("Students").document(id).get().to_dict()
            print(studentInfo)

            # Assuming you have a local image or a different image source
            imgStudent = cv2.imread(f'images/{id}.png')

            # Update the attendance data
            studentInfo['total_attendance'] += 1

            # Update Firestore
            db.collection("Students").document(id).update({
                'total_attendance': studentInfo['total_attendance']
            })

        # Display the updated student info on the screen
        cv2.putText(imgBackground, str(studentInfo['total_attendance']), (861, 125),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
        cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(imgBackground, str(studentInfo['name']), (1005, 493),
                    cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
        cv2.putText(imgBackground, str(studentInfo['year']), (1025, 625),
                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
        cv2.putText(imgBackground, str(studentInfo['starting_year']), (1125, 625),
                    cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

        (w, h), _ = cv2.getTextSize(studentInfo['name'], cv2.FONT_HERSHEY_COMPLEX, 1, 1)
        offset = (414 - w) // 2
        cv2.putText(imgBackground, str(studentInfo['name']), (808 + offset, 445),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

        imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

        counter += 1

    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
