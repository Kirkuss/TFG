import queue
import threading
import time

import tensorflow as tf
import numpy as np
import cv2
import json
import variables as config
import Utilities as Dmanager
import Performance_stats as perf
import tensorflow as tf
import PostWorker as pw
import os

#from tensorflow import keras
from Utilities import ModelInterpreter as mi
from Utilities import timeStamp as ts
from multiprocessing import Process

from multiprocessing.pool import ThreadPool
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

class EmotionProc(QThread):

    changePixmap2 = pyqtSignal(QImage, int)
    updateTerminal = pyqtSignal()
    unlock = pyqtSignal(int)

    js = Dmanager.jsonManager()
    faces = {}

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
        self.iterations = 1
        self.test = 0
        self.workers = {}
        self.resSum = 0

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

    def pool_results(self, result):
        print("Pillao: {}".format(result))


    def unlockFunc(self, id, done, it):
        #print("Mensaje recibido de: " + str(id) + " Status: " + str(done) + " en la iteracion: " + str(it) + "\n")
        self.resSum += done
        if self.resSum == 4:
            self.resSum = 0
            self.test = 1

    def run(self):
        config.LOG += "\n" + ts.getTime(self) + " AIWake ... [STEP 2 - POSTPROCESSING - STARTED]\n" + ts.getTime(self) + \
                      " Video source [" + config.PATH_TO_VIDEO + "]\n" + ts.getTime(self) + " Data model for step 2 [" \
                      + config.PATH_TO_EMODEL + "]"
        cap = cv2.VideoCapture(config.PATH_TO_VIDEO)
        self.updateTerminal.emit()
        config.VIDEO_LENGHT = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        iterations = 1

        pool_size = 4
        #pool = ThreadPool(pool_size)
        blocker = Dmanager.threadManager(parent=self)
        blocker.poolSize = pool_size
        #blocker.unlock.connect(self.unlockFunc)
        blocker.start()

        if config.PATH_TO_JSON_PRE:
            while (cap.isOpened()):
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
                    if self.iterations == 1:
                        for i in range(1, 5): #TESTING PROVISIONAL
                            postW = pw.PostWorker(i = i, blocker=blocker, iteration=iterations, parent=self)
                            postW.iterationDone.connect(self.unlockFunc)
                            blocker.addToPool(postW, i)
                            #pool.map_async(postW.run, [i], callback=self.pool_results)


                            #p = Process(target=thread_.work, args=(i,))
                            #p.start() esto es una bomba para el pc
                    else:
                        self.unlock.emit(1)

                    pr = True

                    while self.test == 0:
                        #self.unlock.emit(1)
                        if pr:
                            #print("Hilo principal en espera")
                            pr = False

                    self.test = 0

                    #print("Continuando...")

                    self.iterations += 1

                    #print(str("ITERATIONS: " + str(self.iterations)))

                    rgbImage = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)

                    self.changePixmap2.emit(convertToQt, perf.getVideoProgress(self.iterations, config.VIDEO_LENGHT))
                    #perf.getVideoProgress(iterations, config.VIDEO_LENGHT)
                    self.jump = False

        self.js.data = self.faces.copy()
        self.js.saveJson("Resources/jsonFiles/PostProcessResults.json")

        cap.release()










