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
window = "Preprocesado"
window2 = "postprocesado"

cv2.namedWindow(window)
cv2.moveWindow(window, 40,30)
cv2.namedWindow(window2)
cv2.moveWindow(window2, 40,30)

if source=="VIDEO":
    cap = cv2.VideoCapture("Resources/" + path)
elif source == "CAM":
    cap = cv2.VideoCapture(0)

cap.set(3,640)
cap.set(4,480)

#f_Found = []
list = {}
list_AUX = {}

founds = 0
iterations = 0
ratio = 0.4
prop = 0.25

list_x = []
list_y = []

while (cap.isOpened()):
    iterations += 1
    ret, frame = cap.read()

    if ret:
        frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        GrayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(GrayFrame, 1.1, 4)

        for (x, y, w, h) in faces:
            newFace = DS.face(x, y, w, h)
            newFound = True

            print(list)

            if len(list) == 0:
                founds += 1
                list[str(founds)] = newFace
                print("Added first")
            else:
                for k, v in list.items():
                    if newFace.equal(prop, list[k], frame):
                        print("Coincidence found")

                        newFace.occurs += list[k].occurs + 1
                        if newFace.occurs >= int(iterations*ratio): newFace.valid = True
                        else: newFace.valid = False

                        print(newFace.occurs)

                        list[k] = newFace
                        print(list)
                        newFound = False
                        break

            if newFound and len(list) > 0:
                founds += 1
                list[str(founds)] = newFace

            if detailed:
                if newFace.valid:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                    cv2.putText(frame, "Face", (int(x + (w*prop)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                else:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    cv2.putText(frame, "Face?", (int(x + (w*prop)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                imgCropped = frame[y:y + h, x:x + w]
                imgCropped = cv2.resize(imgCropped, (320,240))
            else: pass

            if show:
                #cv2.imshow("Gepeto", imgCropped)
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
    else:break

cleanList = {}
cleanList = DS.noiseOut(list)

for k in cleanList:
    print(cleanList[k])

#ERROR, TODO:
# AL LIMPIAR LA LISTA DE CARAS DETECTADAS,
# SE OBTIENE LA ULTIMA X E Y DE DICHAS CARAS "VALIDAS",
# ES DECIR, HAY QUE HACER UNA LISTA QUE ALMACENE
# LAS OCURRENCIAS DE CADA CARA PARA ASI OBTENER
# UNA IMAGEN COMPLETA EN CADA FOTOGRAMA

"""

if source=="VIDEO":
    cap2 = cv2.VideoCapture("Resources/" + path)
elif source == "CAM":
    cap2 = cv2.VideoCapture(0)

cap2.set(3,640)
cap2.set(4,480)

while (cap2.isOpened()):
    ret, frame = cap2.read()
    if ret:
        frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        for k, v in cleanList.items():
            face = cleanList[k]
            cv2.rectangle(frame, (face.x, face.y), (face.x + face.w, face.y + face.h), (255, 0, 0), 2)
            cv2.putText(frame, "Face: " + k, (int(face.x + (face.w * prop)) + 5, face.y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1,
                        cv2.LINE_AA)
            imgCropped = frame[face.y:face.y + face.h, face.x:face.x + face.w]
            imgCropped = cv2.resize(imgCropped, (320, 240))
            cv2.imshow("Gepeto" + k, imgCropped)
            cv2.imshow(window2, frame)
    else: break

cap2.release()
perf.isolation_performance_plot(list_x, list_y, "iterations", "founds", "Performance - isolation")
"""

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




