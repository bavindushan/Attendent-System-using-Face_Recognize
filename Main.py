import os
import pickle
import cv2
import face_recognition

from EncodeGenerator import encodeListKnownWithIds

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread('resources/background.PNG')

# importing the mode images to list
folderModePath = 'resources/mode'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
# print(len(imgModeList))

# load the encoding file
print("Loading Encoded File..")
file = open('EncodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown,studentIds = encodeListKnownWithIds
# print(studentIds)
print(" Encoded File loaded")

while True:
    success, img = cap.read()

    imgS = cv2.resize(img,(0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurrentFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS,faceCurrentFrame)

    imgBackground[162:162+480,55:55+640] = img
    imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[1]

    for encodeFace, faceLoc in zip(encodeCurFrame,faceCurrentFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        print("Matches",matches)
        print("Face Distences",faceDis)
    # cv2.imshow("Webcam", img)
    cv2.imshow("Face Attendance", imgBackground)
    cv2.waitKey(1)
