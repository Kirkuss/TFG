from __future__ import print_function

import os.path
import sys
import time
import cv2
import Performance_stats as perf
import face_DS as DS
import Utilities as Dmanager
import variables as config
import EmotionProc as ep
import DataProcessor as dp
import ModelTrainer as mt


#mt.generateModel()
#exit (1)

show = True
detailed = True
source = "VIDEO"
path = "video5.mp4"
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

postProcessing = False
processCollectedData = True
videoLenght = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

founds = 0
iterations = 0
postIterations = 0
ratio = 0.4
prop = 0.25

list_x = []
list_y = []

js = Dmanager.jsonManager()

print(" |___________")
print(" | AIWake ...")
if source=="VIDEO":
    print(" | Video source [" + source + "] -> Resources/" + path)
elif source == "CAM":
    print(" | Video source [" + source + "] -> CAM")
print(" | Data model -> " + model)
print(" |___________")
print(" | Processing...")

while (cap.isOpened()) and not processCollectedData:

    ret, frame = cap.read()

    if iterations == videoLenght and not processCollectedData:
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
        js.setData(cleanList, "face")
        js.saveJson(config.PATH_TO_JSON_PRE)
        cleanList.clear()
        list.clear()

    iterations += 1

    if ret and postProcessing and not processCollectedData:
        perf.showStats(iterations, videoLenght, postProcessing)
        frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
        GrayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(GrayFrame, 1.1, 4)

        for (x, y, w, h) in faces:
            newFace = DS.face(x, y, w, h, iterations)
            newFound = True
            #print(list)

            #Interesa optimizar

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

            #Interesa optimizar

            if detailed:
                if newFace.valid:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                    cv2.putText(frame, "Accepted", (int(x + (w*prop)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)
                else:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    cv2.putText(frame, "Rejected", (int(x + (w*prop)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                #imgCropped = frame[y:y + h, x:x + w]
                #imgCropped = cv2.resize(imgCropped, (320,240))
            else: pass

            if show:
                #cv2.imshow("Gepeto", imgCropped)
                cv2.imshow(window, frame)
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

    elif not postProcessing and not processCollectedData:
        cv2.destroyAllWindows()
        cap.release()
        ProcessEP = ep.ProcessingEngine()
        ProcessEP.startPostProcessing()
        break

    else: break

if processCollectedData:
    print("Vamos a procesar")
    dp.startProcessingData()
    pass

perf.isolation_performance_plot(list_x, list_y, "iterations", "founds", "Performance - isolation")





