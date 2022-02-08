from PyQt5.QtCore import pyqtSignal, QThread
import variables as config
import cv2
import numpy as np
from Utilities import ModelInterpreter as mi
import time

class PostWorker(QThread):
    iterationDone = pyqtSignal(int, int, int)

    def __init__(self, i , blocker, iteration, chunk ,parent=None):
        super().__init__(parent)
        print("worker (" + str(i) + ") in pool")
        self.blocker = blocker
        self.iteration = iteration
        self.parent = parent
        self.next = 0
        self.done = 0
        self.pr = True
        self.i = i
        self.chunk = chunk

    def goNext(self, signal):
        self.next = signal

    def run(self):
        self.parent.unlock.connect(self.goNext)

        while self.iteration <= config.VIDEO_LENGHT:
            strIt = str(self.iteration)
            for f in self.chunk:
                if strIt in self.parent.faces[f]:
                    #MARCADO PARA MORIR
                    cropped = self.parent.frame[
                              int(self.parent.faces[f][strIt]["y"]):int(self.parent.faces[f][strIt]["y"]) + int(self.parent.faces[f][strIt]["h"]),
                              int(self.parent.faces[f][strIt]["x"]):int(self.parent.faces[f][strIt]["x"]) + int(self.parent.faces[f][strIt]["w"])]
                    # cropped = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
                    resized = cv2.resize(cropped, (224, 224))
                    resized = np.expand_dims(resized, axis=0)
                    resized = resized / 255.0
                    #MARCADO PARA MORIR
                    predictions = self.parent.model.predict(resized)
                    print(self.parent.frame)
                    pred = mi.getClass(n=np.argmax(predictions)) #sacar esto?
                    print("PRED (" + str(self.i) + "): " + str(pred) + "\n")
                    self.parent.faces[f][strIt]["pred"] = pred
                    cv2.rectangle(self.parent.frame, (int(self.parent.faces[f][strIt]["x"]), int(self.parent.faces[f][strIt]["y"])),
                                  (int(self.parent.faces[f][strIt]["x"]) + int(self.parent.faces[f][strIt]["w"]),
                                   int(self.parent.faces[f][strIt]["y"]) + int(self.parent.faces[f][strIt]["h"])),
                                  (255, 255, 255), 1)
                    cv2.putText(self.parent.frame, "ID " + f + pred,
                                (int(int(self.parent.faces[f][strIt]["x"])) + 5, int(self.parent.faces[f][strIt]["y"]) - 7),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
                #time.sleep(10)
            self.done = 1
            self.iterationDone.emit(self.i, 1, self.iteration)

            while self.next == 0:
                #self.iterationDone.emit(self.i, 1, self.iteration)
                if self.pr:
                    print("Hilo " + str(self.i) + " en espera" + "\n")
                    self.pr = False

            #print("Hilo " + str(self.i) + " pasa a la siguiente iteracion\n")

            self.iteration += 1
            self.next = 0
            self.done = 0
            self.pr = True


