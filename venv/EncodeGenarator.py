from codecs import EncodedFile
from uu import encode

import cv2
import face_recognition
import pickle
import os

from jinja2.compiler import generate

# importing Students Images
folderModePath = 'images'
modePathList = os.listdir(folderModePath)
print(modePathList)
imgModeList = []
studentIds = []

for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))
    studentIds.append(os.path.splitext(path)[0])
    # print(path)
    # print(os.path.splitext(path))
    print(studentIds)

# define from here

def findEncoding(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)

        return encodeList
    print("Encoding Start............")
    encodeListKnown = findEncoding(imgList)
    encodeListKnownWithIds = [encodeListKnown, studentIds]
    print("Encoding Complete")

    #pickle file generate()

    file = open("EncodeFile.p", "wb")
    pickle.dump(encodeListKnownWithIds, file)
    file.close()
    print("File Saved")