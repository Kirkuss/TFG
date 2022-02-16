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

from Utilities import ModelInterpreter as mi
from Utilities import timeStamp as ts
from multiprocessing import cpu_count
from tornado import concurrent

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
        self.js = Dmanager.jsonManager()
        self.pause = False
        self.jump = False
        self.frame = ""
        self.faces = self.js.loadJson(config.PATH_TO_JSON_PRE).copy()
        self.iterations = 1
        self.test = 0
        self.workers = {}
        self.resSum = 0
        self.model = tf.keras.models.load_model(config.PATH_TO_EMODEL)

    #def predict(self, resized):
    #   return self.model.predict(resized, verbose = 0)

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
        print(str(pointers))
        return pointers

    def run(self):
        config.LOG += "\n" + ts.getTime(self) + " AIWake ... [STEP 2 - POSTPROCESSING - STARTED]\n" + ts.getTime(self) + \
                      " Video source [" + config.PATH_TO_VIDEO + "]\n" + ts.getTime(self) + " Data model for step 2 [" \
                      + config.PATH_TO_EMODEL + "]\n" + ts.getTime(self) + " Available CPUs: [" + str(cpu_count()) + "]"
        cap = cv2.VideoCapture(config.PATH_TO_VIDEO)
        self.updateTerminal.emit()
        config.VIDEO_LENGHT = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        iterations = 1

        pool_size = config.THREAD_POOL_SIZE
        facesLen = len(self.faces)
        #pool = ThreadPool(pool_size)
        blocker = Dmanager.threadManager(parent=self)
        blocker.poolSize = pool_size
        #blocker.unlock.connect(self.unlockFunc)
        pointers = self.getChunk(facesLen, pool_size)

        if config.PATH_TO_JSON_PRE:
            temp = 0
            while temp < 1:
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
                    pr2 = True
                    if self.iterations == 1:
                        futures = []
                        with concurrent.futures.ThreadPoolExecutor(max_workers=config.THREAD_POOL_SIZE) as executor:
                            for i in pointers:
                                postW = ew.EmotionWorker(chunk=pointers[i], faces=self.faces, parent=self)
                                #postW.iterationDone.connect(self.unlockFunc)
                                future = executor.submit(postW.run(), i)
                                futures.append(future)

                        """
                        for i in range(1, config.THREAD_POOL_SIZE + 1): #TESTING PROVISIONAL
                            postW = pw.PostWorker(i = i, blocker=blocker, iteration=iterations, chunk = pointers[i], parent=self)
                            postW.iterationDone.connect(self.unlockFunc)
                            blocker.addToPool(postW, i)
                            #pool.map_async(postW.run, [i], callback=self.pool_results)
                            #p = Process(target=thread_.work, args=(i,))
                            #p.start() esto es una bomba para el pc
                        """
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

                    temp += 1

        self.js.data = self.faces.copy()
        self.js.saveJson("Resources/jsonFiles/PostProcessResults.json")

        cap.release()










