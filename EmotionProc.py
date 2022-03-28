import gc
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
import PostWorker as pw
import EmotionImgWorker as ew
import os
import threading
import Utilities

from Utilities import ModelInterpreter as mi
from Utilities import timeStamp as ts
from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor

from multiprocessing.pool import ThreadPool
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

class EmotionProc(QThread):

    changePixmap2 = pyqtSignal(QImage, int)
    updateTerminal = pyqtSignal()
    unlock = pyqtSignal(int)
    postPbValue = pyqtSignal(int)
    done = pyqtSignal()

    js = Dmanager.jsonManager()
    faces = {}

    def __init__(self, parent=None):
        super(EmotionProc, self).__init__(parent)
        self.pathToVideo = config.PATH_TO_VIDEO
        self.pathToOutput = config.PATH_TO_JSON_POS
        self.js = Dmanager.jsonManager()
        self.pause = False
        self.jump = False
        self.frame = ""
        self.iterations = 1
        self.test = 0
        self.workers = {}
        self.resSum = 0
        self.model = tf.keras.models.load_model(config.PATH_TO_EMODEL)
        self.faces = self.js.loadJson(config.PATH_TO_JSON_PRE).copy()

    #def predict(self, resized):
    #   return self.model.predict(resized, verbose = 0)

    def getTotalFaces(self):
        count = 0
        for k in self.faces:
            count += len(self.faces[k])
        return count

    def unlockFunc(self, id, done, it):
        #print("Mensaje recibido de: " + str(id) + " Status: " + str(done) + " en la iteracion: " + str(it) + "\n")
        self.resSum += done
        if self.resSum == config.THREAD_POOL_SIZE:
            self.resSum = 0
            self.test = 1

    def getChunk(self, len, pool_size):
        chunk_size = len//pool_size
        mod = len%pool_size
        print("LEN: " + str(chunk_size) + " MOD: " + str(mod))
        pointers = {}
        list = []
        if chunk_size == 0:
            config.THREAD_POOL_SIZE = 1
        else:
            counter = 0
            itCounter = 0
            threadId = 1

            if mod != 0: equilibrate = True
            else: equilibrate = False

            for k in self.faces:
                counter += 1
                itCounter += 1
                list.append(k)
                if counter == chunk_size and not equilibrate:
                    pointers[threadId] = list.copy()
                    list.clear()
                    counter = 0
                    threadId += 1
                    if mod != 0: equilibrate = True
                elif counter == chunk_size and equilibrate:
                    mod -= 1
                    counter -= 1
                    equilibrate = False
        #print(str(pointers))
        return pointers

    def test(self, h):
        print("done {}".format(h))

    def crop(self, frame, x, y, w, h):
        cropped = frame[int(y) : (int(y) + int(h)), int(x) : (int(x) + int(w))]
        resized = cv2.resize(cropped, (224, 224))
        resized = np.expand_dims(resized, axis=0)
        resized = resized / 255.0
        return resized

    def saveProcessedFaces(self):
        self.js.setDataSerialized(self.faces)
        self.js.saveJson(self.pathToOutput)
        print("PostPro json saved")

    def run(self):
        config.LOG += "\n" + ts.getTime(self) + " AIWake ... [STEP 2 - POSTPROCESSING - STARTED]\n" + ts.getTime(self) + \
                      " Video source [" + config.PATH_TO_VIDEO + "]\n" + ts.getTime(self) + " Data model for step 2 [" \
                      + config.PATH_TO_EMODEL + "]\n" + ts.getTime(self) + " Available CPUs: [" + str(cpu_count()) + "]"
        cap = cv2.VideoCapture(config.PATH_TO_VIDEO)
        self.updateTerminal.emit()
        config.VIDEO_LENGHT = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        pool_size = config.THREAD_POOL_SIZE
        blocker = Dmanager.threadManager(parent=self)
        blocker.poolSize = pool_size

        while (cap.isOpened()):

            ret, frame = cap.read()

            if ret:
                frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
                for k in self.faces:
                    if str(self.iterations) in self.faces[k]:
                        faceMat = self.crop(frame, self.faces[k][str(self.iterations)]["x"],
                                            self.faces[k][str(self.iterations)]["y"],
                                            self.faces[k][str(self.iterations)]["w"],
                                            self.faces[k][str(self.iterations)]["h"])
                        predictions = self.model.predict(faceMat)
                        pred = Utilities.ModelInterpreter.getClass(n=np.argmax(predictions))  # sacar esto?
                        self.faces[k][str(self.iterations)]["prediction"] = pred
                        #print(str(k) + "/" + str(self.iterations) + " WORKER [" + str(os.getpid()) + "]: " + str(pred))

                self.postPbValue.emit(perf.getVideoProgress(self.iterations, config.VIDEO_LENGHT))

            if self.iterations == config.VIDEO_LENGHT:
                print("Processing done")
                cap.release()
                break

            self.iterations += 1

        self.saveProcessedFaces()
        self.done.emit()












