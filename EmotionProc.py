import tensorflow as tf
import numpy as np
import cv2
import json
import variables as config
import Utilities as Dmanager
import Performance_stats as perf


cap = cv2.VideoCapture(config.PATH_TO_VIDEO)
js = Dmanager.jsonManager()
window = "Postprocesado"
cv2.namedWindow(window)
cv2.moveWindow(window, 40, 30)
cap.set(3, 640)
cap.set(4, 480)

class ProcessingEngine():
    faces = {}
    videoLenght = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def __init__(self):
        pass

    def startPostProcessing(self, jsonFile = config.PATH_TO_JSON_PRE):
        self.faces = js.loadJson(jsonFile).copy()
        for i in self.faces:
            for j in self.faces[i]:
                pass
            #print(i)
        self.startVideoPreview()

    def startVideoPreview(self):
        iterations = 0
        if config.PATH_TO_JSON_PRE:
            while (cap.isOpened()):
                perf.showStats(iterations, self.videoLenght, False)
                iterations += 1
                ret, frame = cap.read()
                if ret:
                    frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
                    for i in self.faces:
                        #print(i)
                        for j in self.faces[i]:
                            if int(j) == iterations:
                                cv2.rectangle(frame, (int(self.faces[i][j]["x"]),int(self.faces[i][j]["y"])),
                                              (int(self.faces[i][j]["x"]) + int(self.faces[i][j]["w"]),
                                               int(self.faces[i][j]["y"]) + int(self.faces[i][j]["h"])),
                                              (255, 255, 255), 1)
                                cv2.putText(frame, "ID " + i,
                                            (int(int(self.faces[i][j]["x"])) + 5, int(self.faces[i][j]["y"]) - 7),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.imshow(window, frame)
                    if cv2.waitKey(1) & 0xFF == ord ('q'):
                        break
                else:
                    break






