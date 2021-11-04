import os
import time

import cv2
import Performance_stats as perf
import face_DS as DS

show = True
detailed = True
source = "VIDEO"
path = "video3.mp4"

faceCascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")
img = cv2.imread("Resources/foto1.jpg")
window = "Salida"

cv2.namedWindow(window)
cv2.moveWindow(window, 40,30)

if source=="VIDEO":
    cap = cv2.VideoCapture("Resources/" + path)
elif source == "CAM":
    cap = cv2.VideoCapture(0)

cap.set(3,640)
cap.set(4,480)

#f_Found = []
list = DS.dataList(None)

founds = 0
iterations = 0

list_x = []
list_y = []

while True and iterations <= 0:
    iterations += 1
    ret, frame = cap.read()
    frame = cv2.resize(frame, (540, 380), fx = 0, fy = 0, interpolation = cv2.INTER_CUBIC)
    GrayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(GrayFrame,1.1,4)
    Updated = False

    for (x, y, w, h) in faces:
        if list.countItems() == 0:
            founds += 1
            newFace = DS.face(x, y, w, h, founds)
            list.item = newFace
        else:
            print("Todo bien")
            """
            for obj in f_Found:
                if obj.equal(0.25, x, y, frame):
                    print("Coincidence found")
                    obj = faceFound
                else:
                    f_Found.append(faceFound)
                    founds += 1
                    print("Added new")
            """

        if detailed:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
            imgCropped = frame[y:y + h, x:x + w]
            imgCropped = cv2.resize(imgCropped, (320,240))
        else: pass

        if show:
            cv2.imshow("Gepeto", imgCropped)
            cv2.imshow(window, frame)
        else: pass

        print("Found faces: " + str(founds))
        time.sleep(0)

    list_y.append(founds)
    list_x.append(iterations)


    if cv2.waitKey(1) & 0xFF == ord('q'):
        while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        break


perf.isolation_performance_plot(list_x, list_y, "iterations", "founds", "Performance - isolation")

"""
for (x,y,w,h) in faces:
    count += 1
    cv2.rectangle(img,(x,y),(x+w,y+h), (255,0,0), 2)
    imgCropped = img[y:y+h,x:x+w]
    print(x,x+w,y,y+h)
    cv2.imshow(str(count), imgCropped)

cv2.imshow("Salida", img)
cv2.waitKey(0)
"""




