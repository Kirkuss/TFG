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
from cryptography.fernet import Fernet

class FaceIsolator(QThread):

    changePixmap = pyqtSignal(QImage, int)
    updateTerminal = pyqtSignal()
    setPicker = pyqtSignal(list)
    changePixmap_pick = pyqtSignal(QImage, list)
    updateStatus = pyqtSignal(list, int)
    updateFrameSelector = pyqtSignal(int)

    def __init__(self, parent=None):
        super(FaceIsolator, self).__init__(parent)
        self.pathToVideo = config.PATH_TO_VIDEO
        self.pathToOutput = config.PATH_TO_JSON_PRE
        self.faceCascade = cv2.CascadeClassifier(config.PATH_TO_MODEL)
        self.js = Dmanager.jsonManager()
        self.pause = False
        self.jump = False
        self.frame = ""
        self.list = {}
        self.faces = ""
        self.sig = False
        self.selectedFrame = 0
        self.finished = False
        self.selecting = False
        self.done = False
        self.key = b'6cOMmRQnESKFNYyU2rD6uD-GvWVAMKibEkX4ws7-NwA='
        self.fernet = Fernet(self.key)
        config.IMG_KEY = self.key
        config.LOG +=  ts.getTime(self) + " AIWake ... [STEP 1 - PREPROCESSING - STARTED]\n" + ts.getTime(self) + \
                       " Video source [" + config.PATH_TO_VIDEO + "]\n" + ts.getTime(self) + " Data model for step 1 ["\
                       + config.PATH_TO_MODEL + "]"
        cap = cv2.VideoCapture(self.pathToVideo)
        config.VIDEO_LENGHT = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

    def updateWithoutProcessing(self):
        pass

    def getFaceIds(self, k, delete):
        idList = []
        if delete:
            for k, v in self.list.items():
                idList.append(k)
        else:
            idList.append(k)
        return idList

    def generateFaceInfo(self, face, iterations, id):
        info = []
        info.append("Face id: " + str(id))
        if face.valid: info.append("Status: Accepted")
        else: info.append("Status: Rejected")
        info.append("Appeared in " + str(int(face.occurs)) + " frames")
        info.append("Ratio: " + str(int((face.occurs/iterations)*100)) + "%")
        return info

    def setStatusText(self, text):
        status = []
        status.append(text)
        return status

    def deleteFace(self):
        deleted = self.list.pop(str(config.SELECTED_FACE))
        print("Deleted face: " + str(deleted))
        self.setPicker.emit(self.getFaceIds("0", True))

    def drawFaces(self, valid, frame, x, y , w, h, selected):
        test = 1
        if config.DETAILED:
            if valid == "True":
                if selected:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                    cv2.rectangle(frame, (x * test, y * test), (x * test + w * test, y * test + h * test), (0, 255, 0), 1)
                    cv2.putText(frame, "Selected", (int(x + (w * config.PROP)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 0), 1, cv2.LINE_AA)
                else:
                    cv2.rectangle(frame, (x * test, y * test), (x * test + w * test, y * test + h * test), (0, 255, 0),
                                  1)
                    cv2.putText(frame, "Accepted", (int(x * test + (w * test * config.PROP)) + 5, y * test - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 1, cv2.LINE_AA)
            else:
                if selected:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    cv2.putText(frame, "Selected", (int(x + (w * config.PROP)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 0, 255), 1, cv2.LINE_AA)
                else:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    cv2.putText(frame, "Rejected", (int(x + (w * config.PROP)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 0, 255), 1, cv2.LINE_AA)

    def run(self):
        self.updateStatus.emit(self.setStatusText("Preparing pre-process"), 1)
        cap = cv2.VideoCapture(self.pathToVideo)
        config.VIDEO_LENGHT = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        iterations = 0
        founds = 0
        faceCascade = cv2.CascadeClassifier(config.PATH_TO_MODEL)
        config.LOG += "\n" + ts.getTime(self) + " [" + str(config.VIDEO_LENGHT) + "] detected frames to be procesed"
        config.LOG += "\n" + ts.getTime(self) + " Processing..."
        self.updateTerminal.emit()
        lastFrame = ""

        while (cap.isOpened()):

            ret, frame = cap.read()
            writeOnPause = True

            while self.pause and not self.jump:
                if writeOnPause:
                    config.LOG += "\n" + ts.getTime(self) + " Video paused by user at frame [" + str(iterations) + "]"
                    self.updateStatus.emit(self.setStatusText("Preview paused at frame [" + str(iterations) + "]"), 2)
                    self.updateTerminal.emit()
                    writeOnPause = False

            if iterations == config.VIDEO_LENGHT:
                coincidences = 0
                self.done = True
                self.updateStatus.emit(self.setStatusText("Generating preview data..."), 1)
                self.js.setData(self.list, "face")
                self.js.saveJson(config.PATH_TO_JSON_TEMP)
                previewData = self.js.loadJson(config.PATH_TO_JSON_TEMP)
                self.updateStatus.emit(self.setStatusText("Waiting for user to review obtained data"), 1)
                while not self.finished:
                    if self.selecting and self.done:
                        cap.set(1, self.selectedFrame)
                        ret, frame = cap.read()
                        frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
                        for k in previewData:
                            if str(self.selectedFrame) in previewData[k]:
                                if config.SELECTED_FACE >= 0:
                                    if k == str(config.SELECTED_FACE):
                                        self.drawFaces(previewData[k][str(self.selectedFrame)]["valid"], frame,
                                                       int(previewData[k][str(self.selectedFrame)]["x"]),
                                                       int(previewData[k][str(self.selectedFrame)]["y"]),
                                                       int(previewData[k][str(self.selectedFrame)]["w"]),
                                                       int(previewData[k][str(self.selectedFrame)]["h"]), True)
                                    else:
                                        self.drawFaces(previewData[k][str(self.selectedFrame)]["valid"], frame,
                                                       int(previewData[k][str(self.selectedFrame)]["x"]),
                                                       int(previewData[k][str(self.selectedFrame)]["y"]),
                                                       int(previewData[k][str(self.selectedFrame)]["w"]),
                                                       int(previewData[k][str(self.selectedFrame)]["h"]), False)
                                else:
                                    self.drawFaces(previewData[k][str(self.selectedFrame)]["valid"], frame,
                                                   int(previewData[k][str(self.selectedFrame)]["x"]),
                                                   int(previewData[k][str(self.selectedFrame)]["y"]),
                                                   int(previewData[k][str(self.selectedFrame)]["w"]),
                                                   int(previewData[k][str(self.selectedFrame)]["h"]), False)
                        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        h, w, ch = rgbImage.shape
                        bytesPerLine = ch * w
                        convertToQt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                        self.changePixmap.emit(convertToQt, perf.getVideoProgress(iterations, config.VIDEO_LENGHT))
                        #self.selecting = False

                    if config.SELECTED_FACE >= 0 and not self.sig:
                        aux_face = self.list[str(config.SELECTED_FACE)]
                        cropped = lastFrame[aux_face.y : (aux_face.y + aux_face.h), aux_face.x : (aux_face.x + aux_face.w)]
                        rgbImage = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                        h, w, ch = rgbImage.shape
                        bytesPerLine = ch * w
                        cropped2Qt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                        self.changePixmap_pick.emit(cropped2Qt, self.generateFaceInfo(aux_face, iterations, config.SELECTED_FACE))
                        self.sig = True
                    pass
                cleanList = DS.noiseOut(self.list)
                for k in cleanList:
                    coincidences += 1
                self.js.setData(cleanList, "face")
                self.js.saveJson(config.PATH_TO_JSON_PRE)
                cleanList.clear()
                self.list.clear()
                print("done")
                config.LOG += "\n" + ts.getTime(self) + " Step 1 finished..."
                config.LOG += "\n" + ts.getTime(self) + " Json for step 1 -> " + config.PATH_TO_JSON_PRE
                config.LOG += "\n" + ts.getTime(self) + " AIWake ... [STEP 1 - PREPROCESSING - FINISHED]"
                self.updateTerminal.emit()
                cap.release()

            iterations += 1

            if ret:
                self.updateStatus.emit(self.setStatusText("Obtaining faces in video frame: [" + str(iterations) + "]"), 1)
                frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
                if iterations == config.VIDEO_LENGHT - 1:
                    lastFrame = frame.copy()
                #self.frame = frame.copy()
                GrayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(GrayFrame, 1.1, 4)

                for (x, y, w, h) in faces:
                    newFace = DS.face(x, y, w, h, iterations, self.fernet)
                    newFound = True
                    if len(self.list) == 0:
                        founds += 1
                        self.list[str(founds)] = newFace
                        newFace.queue(newFace, None)
                        self.setPicker.emit(self.getFaceIds(str(founds), False))
                    else:
                        for k, v in self.list.items():
                            if newFace.equal(config.PROP, self.list[k], frame):
                                newFace.occurs += self.list[k].occurs + 1
                                if newFace.occurs >= int(iterations*config.RATIO): newFace.valid = True
                                else: newFace.valid = False
                                newFace.queue(newFace, self.list[k].list)
                                self.list[k] = newFace
                                newFound = False
                                break

                    if newFound and len(self.list) > 0:
                        founds += 1
                        newFace.queue(newFace, None)
                        self.list[str(founds)] = newFace
                        self.setPicker.emit(self.getFaceIds(str(founds), False))

                    if config.SELECTED_FACE >= 0:
                        aux_face = self.list[str(config.SELECTED_FACE)]
                        cropped = frame[aux_face.y : (aux_face.y + aux_face.h), aux_face.x : (aux_face.x + aux_face.w)]
                        rgbImage = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                        h, w, ch = rgbImage.shape
                        bytesPerLine = ch * w
                        cropped2Qt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                        self.changePixmap_pick.emit(cropped2Qt, self.generateFaceInfo(aux_face, iterations, config.SELECTED_FACE))

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
                self.updateFrameSelector.emit(iterations)

                self.jump = False

