from __future__ import print_function

import os
import sys
import time
import cv2
import Performance_stats as perf
import face_DS as DS

show = False
detailed = True
source = "VIDEO"
path = "video3.mp4"
model = "Resources/haarcascade_frontalface_default.xml"

faceCascade = cv2.CascadeClassifier(model)
window = "Preprocesado"

cv2.namedWindow(window)
cv2.moveWindow(window, 40,30)

if source=="VIDEO":
    cap = cv2.VideoCapture("Resources/" + path)
elif source == "CAM":
    cap = cv2.VideoCapture(0)

cap.set(3,640)
cap.set(4,480)

#f_Found = []
list = {}
list_AUX = {}

postProcessing = True
videoLenght = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

founds = 0
iterations = 0
postIterations = 0
ratio = 0.4
prop = 0.25

list_x = []
list_y = []

print(" |___________")
print(" | AIWake ...")
if source=="VIDEO":
    print(" | Video source [" + source + "] -> Resources/" + path)
elif source == "CAM":
    print(" | Video source [" + source + "] -> CAM")
print(" | Data model -> " + model)
print(" |___________")
print(" | Processing...")



def showStats(iterations, postIterations, lenght):
    if postProcessing:
        perc = (iterations/lenght) * 100
        print('\r', "| Preprocessing... " + str(int(perc)) + "%", end='')
    elif not postProcessing:
        perc = (postIterations / lenght) * 100
        print('\r', "| Postprocessing... " + str(int(perc)) + "%", end='')

while (cap.isOpened()):

    showStats(iterations, postIterations, videoLenght)

    if iterations == videoLenght:
        cleanList = {}
        coincidences = 0
        cleanList = DS.noiseOut(list)
        print("\n | Found items...")
        for k in cleanList:
            print(" | " + str(cleanList[k]))
            coincidences += 1
        occRation = (coincidences/founds) * 100
        print(" | Found " + str(coincidences) + " valid items out of " + str(founds) +
              " | Acceptation ratio -> " + str(ratio))
        print(" | Hit ratio -> " + str(round(occRation, 2)) + "%")
        postProcessing = False
        _ = cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    iterations += 1
    ret, frame = cap.read()

    if ret and postProcessing:
        frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        GrayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(GrayFrame, 1.1, 4)

        for (x, y, w, h) in faces:
            newFace = DS.face(x, y, w, h, iterations)
            newFound = True
            #print(list)

            if len(list) == 0:
                founds += 1
                list[str(founds)] = newFace
                newFace.queue(newFace, None)
                #print("Added first")
            else:
                for k, v in list.items():
                    if newFace.equal(prop, list[k], frame):
                        #print("Coincidence found")
                        newFace.occurs += list[k].occurs + 1
                        if newFace.occurs >= int(iterations*ratio): newFace.valid = True
                        else: newFace.valid = False
                        #print(newFace.occurs)
                        newFace.queue(newFace, list[k].list)
                        list[k] = newFace
                        #print(list)
                        newFound = False
                        break

            if newFound and len(list) > 0:
                founds += 1
                newFace.queue(newFace, None)
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
                #cv2.imshow(window, frame)
                pass
            else: pass

            #print("Found faces: " + str(founds))
            time.sleep(0)

        list_y.append(founds)
        list_x.append(iterations)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            while True:
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            break
    elif ret and not postProcessing:
        #print("again")
        postIterations += 1
        frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        for k, v in cleanList.items():
            faceItem = cleanList[k]
            if postIterations in faceItem.list:
                validFace = faceItem.list[postIterations]
                cv2.rectangle(frame, (validFace.x, validFace.y), (validFace.x + validFace.w, validFace.y + validFace.h),
                              (255, 0, 0), 2)
                cv2.putText(frame, "Face: " + k, (int(validFace.x + (validFace.w * prop)) + 5, validFace.y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1,
                            cv2.LINE_AA)
                #imgCropped = frame[validFace.y:validFace.y + validFace.h, validFace.x:validFace.x + validFace.w]
                #imgCropped = cv2.resize(imgCropped, (320, 240))
                #cv2.imshow("Gepeto" + k, imgCropped)
                #cv2.imshow(window, frame)
            else:
                #cv2.imshow(window, frame)
                pass
    else: break

cap.release()
perf.isolation_performance_plot(list_x, list_y, "iterations", "founds", "Performance - isolation")

#ERROR, TODO:
# AL LIMPIAR LA LISTA DE CARAS DETECTADAS,
# SE OBTIENE LA ULTIMA X E Y DE DICHAS CARAS "VALIDAS",
# ES DECIR, HAY QUE HACER UNA LISTA QUE ALMACENE
# LAS OCURRENCIAS DE CADA CARA PARA ASI OBTENER
# UNA IMAGEN COMPLETA EN CADA FOTOGRAMA

#cap.release()

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




