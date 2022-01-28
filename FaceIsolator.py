import Utilities
import variables as config
import cv2
import AIWakeUI
import face_DS as DS
import Utilities as Dmanager
import Performance_stats as perf

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage
from Utilities import timeStamp as ts

class FaceIsolator(QThread):

    changePixmap = pyqtSignal(QImage, int)
    updateTerminal = pyqtSignal()

    def __init__(self, parent=None):
        super(FaceIsolator, self).__init__(parent)
        self.pathToVideo = config.PATH_TO_VIDEO
        self.pathToOutput = config.PATH_TO_JSON_PRE
        self.faceCascade = cv2.CascadeClassifier(config.PATH_TO_MODEL)
        self.js = Dmanager.jsonManager()
        self.pause = False
        self.jump = False
        self.frame = ""
        self.faces = ""
        config.LOG +=  ts.getTime(self) + " AIWake ... [STEP 1 - PREPROCESSING - STARTED]\n" + ts.getTime(self) + \
                       " Video source [" + config.PATH_TO_VIDEO + "]\n" + ts.getTime(self) + " Data model for step 1 ["\
                       + config.PATH_TO_MODEL + "]"

    def updateWithoutProcessing(self):
        pass

    def run(self):
        cap = cv2.VideoCapture(self.pathToVideo)
        config.VIDEO_LENGHT = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        iterations = 0
        founds = 0
        list = {}
        faceCascade = cv2.CascadeClassifier(config.PATH_TO_MODEL)
        config.LOG += "\n" + ts.getTime(self) + " [" + str(config.VIDEO_LENGHT) + "] detected frames to be procesed"
        config.LOG += "\n" + ts.getTime(self) + " Processing..."
        self.updateTerminal.emit()

        while (cap.isOpened()):
            ret, frame = cap.read()
            writeOnPause = True

            while self.pause and not self.jump:
                if writeOnPause:
                    config.LOG += "\n" + ts.getTime(self) + " Video paused by user at frame [" + str(iterations) + "]"
                    self.updateTerminal.emit()
                    writeOnPause = False

            if iterations == config.VIDEO_LENGHT:
                coincidences = 0
                cleanList = DS.noiseOut(list)
                for k in cleanList:
                    coincidences += 1
                self.js.setData(cleanList, "face")
                self.js.saveJson(config.PATH_TO_JSON_PRE)
                cleanList.clear()
                list.clear()
                print("done")
                config.LOG += "\n" + ts.getTime(self) + " Step 1 finished..."
                config.LOG += "\n" + ts.getTime(self) + " Json for step 1 -> " + config.PATH_TO_JSON_PRE
                config.LOG += "\n" + ts.getTime(self) + " AIWake ... [STEP 1 - PREPROCESSING - FINISHED]"
                self.updateTerminal.emit()
                cap.release()

            iterations += 1

            if ret:
                frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
                #self.frame = frame.copy()
                GrayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(GrayFrame, 1.1, 4)

                for (x, y, w, h) in faces:
                    newFace = DS.face(x, y, w, h, iterations)
                    newFound = True
                    if len(list) == 0:
                        founds += 1
                        list[str(founds)] = newFace
                        newFace.queue(newFace, None)
                    else:
                        for k, v in list.items():
                            if newFace.equal(config.PROP, list[k], frame):
                                newFace.occurs += list[k].occurs + 1
                                if newFace.occurs >= int(iterations*config.RATIO): newFace.valid = True
                                else: newFace.valid = False
                                newFace.queue(newFace, list[k].list)
                                list[k] = newFace
                                newFound = False
                                break

                    if newFound and len(list) > 0:
                        founds += 1
                        newFace.queue(newFace, None)
                        list[str(founds)] = newFace

                    if config.DETAILED:
                        if newFace.valid:
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                            cv2.putText(frame, "Accepted", (int(x + (w * config.PROP)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                        (0, 255, 0), 1, cv2.LINE_AA)
                        else:
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                            cv2.putText(frame, "Rejected", (int(x + (w * config.PROP)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                        (0, 0, 255), 1, cv2.LINE_AA)

                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)

                self.changePixmap.emit(convertToQt, perf.getVideoProgress(iterations,config.VIDEO_LENGHT))

                self.jump = False

