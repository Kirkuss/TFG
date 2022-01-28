import tensorflow as tf
import numpy as np
import cv2
import json
import variables as config
import Utilities as Dmanager
import Performance_stats as perf
import tensorflow as tf
import os

#from tensorflow import keras
from Utilities import ModelInterpreter as mi
from Utilities import timeStamp as ts
from multiprocessing import Process

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

class EmotionProc(QThread):

    changePixmap2 = pyqtSignal(QImage, int)
    updateTerminal = pyqtSignal()

    js = Dmanager.jsonManager()
    faces = {}

    #if os.path.isfile(config.EMOTION_MODEL):
    #model = tf.keras.models.load_model("Resources/datasets/Models/FINAL")

    def __init__(self, parent=None):
        super(EmotionProc, self).__init__(parent)
        self.pathToVideo = config.PATH_TO_VIDEO
        self.pathToOutput = config.JSON_PATH_POS
        self.model = tf.keras.models.load_model(config.PATH_TO_EMODEL)
        self.js = Dmanager.jsonManager()
        self.pause = False
        self.jump = False
        self.frame = ""
        self.faces = self.js.loadJson(config.PATH_TO_JSON_PRE).copy()

    def threaded_process(self, i, k):
        face = self.faces[i]
        if k in face:
            print("frame: " + str(k) + " pid" + str(os.getpid()))
            cropped = self.frame[int(self.faces[i][k]["y"]):int(self.faces[i][k]["y"]) + int(self.faces[i][k]["h"]),
            int(self.faces[i][k]["x"]):int(self.faces[i][k]["x"]) + int(self.faces[i][k]["w"])]
            # cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(cropped, (224, 224))
            resized = np.expand_dims(resized, axis=0)
            resized = resized / 255.0
            predictions = self.model.predict(resized, verbose=0)
            pred = mi.getClass(n=np.argmax(predictions))
            self.faces[i][k]["pred"] = pred
            cv2.rectangle(self.frame, (int(self.faces[i][k]["x"]), int(self.faces[i][k]["y"])),
                (int(self.faces[i][k]["x"]) + int(self.faces[i][k]["w"]),
                int(self.faces[i][k]["y"]) + int(self.faces[i][k]["h"])),
                (255, 255, 255), 1)
            cv2.putText(self.frame, "ID " + i + pred,
                (int(int(self.faces[i][k]["x"])) + 5, int(self.faces[i][k]["y"]) - 7),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        exit(0)

    def run(self):
        config.LOG += "\n" + ts.getTime(self) + " AIWake ... [STEP 2 - POSTPROCESSING - STARTED]\n" + ts.getTime(self) + \
                      " Video source [" + config.PATH_TO_VIDEO + "]\n" + ts.getTime(self) + " Data model for step 2 [" \
                      + config.PATH_TO_EMODEL + "]"
        cap = cv2.VideoCapture(config.PATH_TO_VIDEO)
        self.updateTerminal.emit()
        config.VIDEO_LENGHT = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        iterations = 0

        if config.PATH_TO_JSON_PRE:
            while (cap.isOpened()):
                iterations += 1
                ret, self.frame = cap.read()
                writeOnPause = True

                while self.pause and not self.jump:
                    if writeOnPause:
                        config.LOG += "\n" + ts.getTime(self) + " Video paused by user at frame [" + str(
                            iterations) + "]"
                        self.updateTerminal.emit()
                        writeOnPause = False

                if ret:
                    self.frame = cv2.resize(self.frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
                    for i in self.faces:

                            p = Process(target=thread_.work, args=(i,))
                            #p.start() esto es una bomba para el pc

                            """
                            if int(j) == iterations:

                                cropped = frame[int(self.faces[i][j]["y"]):int(self.faces[i][j]["y"]) + int(self.faces[i][j]["h"]),
                                          int(self.faces[i][j]["x"]):int(self.faces[i][j]["x"])+int(self.faces[i][j]["w"])]
                                #cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                                resized = cv2.resize(cropped, (224,224))
                                resized = np.expand_dims(resized, axis=0)
                                resized = resized/255.0
                                predictions = self.model.predict(resized, verbose=0)
                                pred = mi.getClass(n = np.argmax(predictions))
                                self.faces[i][j]["pred"] = pred
                                #print(predictions[0])
                                cv2.rectangle(frame, (int(self.faces[i][j]["x"]),int(self.faces[i][j]["y"])),
                                              (int(self.faces[i][j]["x"]) + int(self.faces[i][j]["w"]),
                                               int(self.faces[i][j]["y"]) + int(self.faces[i][j]["h"])),
                                              (255, 255, 255), 1)
                                cv2.putText(frame, "ID " + i + pred,
                                            (int(int(self.faces[i][j]["x"])) + 5, int(self.faces[i][j]["y"]) - 7),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)

                                break #occurrence found, break first j for loop.
                                """

                    rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)

                    self.changePixmap2.emit(convertToQt, perf.getVideoProgress(iterations, config.VIDEO_LENGHT))
                    #perf.getVideoProgress(iterations, config.VIDEO_LENGHT)
                    self.jump = False

        self.js.data = self.faces.copy()
        self.js.saveJson("Resources/jsonFiles/PostProcessResults.json")

        cap.release()










