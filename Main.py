import os
import pickle
import cv2
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
import time

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
imgStudent = np.zeros((216, 216, 3), dtype=np.uint8)  # Initialize with a blank image

# Variable to track last update time for imgModeList[2] (3.png)
last_update_time = 0

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

        if not any(matches):
            continue  # Skip if no match found

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            student_id = str(studentIds[matchIndex])
            print(f"Recognized Student: {student_id}")

            if id != student_id:
                id = student_id
                counter = 1  # Reset counter when a new student is recognized
                modeType = 1  # Change to the "attendance" mode

            # Fetch student data from Firestore
            student_ref = db.collection("Students").document(student_id)
            student_doc = student_ref.get()

            if not student_doc.exists:
                print(f"⚠️ Student ID {student_id} not found in Firestore.")
                continue

            student_data = student_doc.to_dict()

            last_attendance_time = student_data.get("last_attendance_time")

            if last_attendance_time:
                last_attendance_time = datetime.strptime(last_attendance_time, "%Y-%m-%d %H:%M:%S")
                if datetime.now() - last_attendance_time < timedelta(minutes=5):
                    print(f"Skipping update for {student_id}, already marked recently.")
                    # Load imgModeList[3] (4.png) image
                    imgBackground[87:87 + 633, 808:808 + 414] = imgModeList[3]
                else:
                    # Update Attendance
                    new_attendance = student_data.get("total_attendance", 0) + 1
                    student_ref.update({
                        "total_attendance": new_attendance,
                        "last_attendance_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    print(f"✅ Updated Attendance for {student_id}")
                    # Add imgModeList[2] (3.png) with 2-second delay
                    if time.time() - last_update_time > 2:
                        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[2]
                        last_update_time = time.time()  # Update the last update time

            # Draw bounding box around detected face
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55 + x1, 162 + y1, x2 - x1, y2 - y1
            imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

            # Load student image from local storage
            imgStudentPath = f'images/{id}.png'

            if os.path.exists(imgStudentPath):
                imgStudent = cv2.imread(imgStudentPath)
                imgStudent = cv2.resize(imgStudent, (216, 216))  # Resize to fit allocated space
                print(f"✅ Loaded student image: {imgStudentPath}")
            else:
                print(f"⚠️ No image found for student {id}")
                imgStudent = np.zeros((216, 216, 3), dtype=np.uint8)  # Blank image if not found

    if counter != 0:
        studentInfo = db.collection("Students").document(id).get().to_dict()
        if studentInfo:
            imgBackground[175:175 + 216, 909:909 + 216] = imgStudent

            cv2.putText(imgBackground, str(studentInfo.get('total_attendance', 'N/A')), (861, 125),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo.get('major', 'Unknown')), (1006, 550),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo.get('name', 'No Name')), (1005, 493),
                        cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(imgBackground, str(studentInfo.get('standing', 'N/A')), (910, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
            cv2.putText(imgBackground, str(studentInfo.get('year', 'N/A')), (1025, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
            cv2.putText(imgBackground, str(studentInfo.get('starting_year', 'N/A')), (1125, 625),
                        cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
        counter += 1

    cv2.imshow("Face Attendance", imgBackground)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()
