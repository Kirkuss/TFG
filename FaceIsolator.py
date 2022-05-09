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
    preprocessDone = pyqtSignal()
    changeSelectedFrame = pyqtSignal(int)
    updatePlotter = pyqtSignal(list, list)

    def __init__(self, parent=None):
        super(FaceIsolator, self).__init__(parent)
        self.pathToVideo = config.PATH_TO_VIDEO
        self.pathToOutput = config.PATH_TO_JSON_PRE
        self.faceCascade = cv2.CascadeClassifier(config.PATH_TO_MODEL)
        self.previewData = {}
        self.js = Dmanager.jsonManager()
        self.pause = False
        self.jump = False
        self.frame = ""
        self.showOnlySelected = False
        self.list = {}
        self.faces = ""
        self.sig = False
        self.deleteAuto = False
        self.finished = False
        self.selecting = False
        self.done = False
        self.x_data = []
        self.y_data = []

        self.forward = False
        self.forwardToProcessed = False
        self.backward = False
        self.backwardToProcessed = False

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

    def getFaceIds(self, faceList, k, delete):
        idList = []
        if delete:
            for k, v in faceList.items():
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
        self.updateStatus.emit(self.setStatusText("Generating preview data..."), 1)
        deleted = self.list.pop(str(config.SELECTED_FACE))
        del self.previewData[str(config.SELECTED_FACE)]
        self.js.setDataSerialized(self.previewData)
        self.js.saveJson(config.PATH_TO_JSON_TEMP)
        print("Deleted face: " + str(deleted))
        self.setPicker.emit(self.getFaceIds(self.list, "0", True))
        self.updateStatus.emit(self.setStatusText("Waiting for user to review obtained data"), 1)

    def drawFaces(self, id, valid, frame, x, y , w, h, selected):
        test = 1
        if config.DETAILED:
            if valid == "True":
                if selected:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                    cv2.rectangle(frame, (x * test, y * test), (x * test + w * test, y * test + h * test), (0, 255, 0), 1)
                    cv2.putText(frame, id + " Selected", (int(x + (w * config.PROP)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 255, 0), 1, cv2.LINE_AA)
                elif not self.showOnlySelected:
                    cv2.rectangle(frame, (x * test, y * test), (x * test + w * test, y * test + h * test), (0, 255, 0),
                                  1)
                    cv2.putText(frame, id + " Accepted", (int(x * test + (w * test * config.PROP)) + 5, y * test - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 1, cv2.LINE_AA)
            else:
                if selected:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    cv2.putText(frame, id + " Selected", (int(x + (w * config.PROP)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (0, 0, 255), 1, cv2.LINE_AA)
                elif not self.showOnlySelected:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    cv2.putText(frame, id + " Rejected", (int(x + (w * config.PROP)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 0, 255), 1, cv2.LINE_AA)

    def deleteAllRejected(self):
        cleanList = DS.noiseOut(self.list)
        self.list = cleanList
        self.updateStatus.emit(self.setStatusText("Generating preview data..."), 1)

        aux = self.previewData.copy()
        for k in aux:
            if k not in self.list:
                del self.previewData[k]
        del aux

        self.js.setDataSerialized(self.previewData)
        self.js.saveJson(config.PATH_TO_JSON_TEMP)
        self.updateStatus.emit(self.setStatusText("Waiting for user to review obtained data"), 1)
        self.setPicker.emit(self.getFaceIds(cleanList, "0", True))

    def deleteFaceFrame(self):
        print("deleting face frame")
        if str(config.SELECTED_FACE) in self.previewData:
            if str(config.SELECTED_FRAME) in self.previewData[str(config.SELECTED_FACE)]:
                del self.previewData[str(config.SELECTED_FACE)][str(config.SELECTED_FRAME)]
                self.js.setDataSerialized(self.previewData)
                self.js.saveJson(config.PATH_TO_JSON_TEMP)
                print("Deleted face frame: " + str(config.SELECTED_FRAME))

    def getNearestProcessed(self, iterations):
        aux_iterations = iterations
        founds = []
        if self.forwardToProcessed:
            for k in self.previewData:
                while True:
                    aux_iterations += 1
                    str_iterations = str(aux_iterations)
                    if aux_iterations > config.VIDEO_LENGHT:
                        aux_iterations = iterations
                        break
                    if str_iterations in self.previewData[k]:
                        founds.append(aux_iterations)
                        aux_iterations = iterations
                        break
            if len(founds) == 0:
                return -1
            return min(founds)
        elif self.backwardToProcessed:
            for k in self.previewData:
                while True:
                    aux_iterations -= 1
                    str_iterations = str(aux_iterations)
                    if aux_iterations < 0:
                        aux_iterations = iterations
                        break
                    if str_iterations in self.previewData[k]:
                        founds.append(aux_iterations)
                        aux_iterations = iterations
                        break
            if len(founds) == 0:
                return -1
            return max(founds)
        return 0

    def run(self):
        self.updateStatus.emit(self.setStatusText("Preparing pre-process"), 1)
        cap = cv2.VideoCapture(self.pathToVideo)
        config.VIDEO_LENGHT = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        iterations = 0
        iterations_ratio = 0
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
                if self.deleteAuto:
                    cleanList = DS.noiseOut(self.list)
                    self.list = cleanList
                    self.setPicker.emit(self.getFaceIds(cleanList ,"0" ,True))

                self.updateStatus.emit(self.setStatusText("Generating preview data..."), 1)
                self.js.setData(self.list, "face")
                self.js.saveJson(config.PATH_TO_JSON_TEMP)
                self.previewData = self.js.loadJson(config.PATH_TO_JSON_TEMP)
                self.updateStatus.emit(self.setStatusText("Waiting for user to review obtained data"), 1)

                self.x_data = list(range(1, int(iterations) + 1))
                self.updatePlotter.emit(self.x_data, self.y_data)

                while not self.finished:
                    if self.selecting and self.done:
                        if config.SELECTED_FRAME < config.VIDEO_LENGHT:

                            if self.forward:
                                config.SELECTED_FRAME += 1
                                cap.set(1, config.SELECTED_FRAME)
                                self.forward = False
                            elif self.forwardToProcessed:
                                res = self.getNearestProcessed(iterations)
                                if res < 0:
                                    pass
                                else:
                                    config.SELECTED_FRAME = res
                                cap.set(1, config.SELECTED_FRAME)
                                self.forwardToProcessed = False
                            elif self.backward:
                                config.SELECTED_FRAME -= 1
                                cap.set(1, config.SELECTED_FRAME)
                                self.backward = False
                            elif self.backwardToProcessed:
                                res = self.getNearestProcessed(iterations)
                                if res < 0:
                                    pass
                                else:
                                    config.SELECTED_FRAME = res
                                cap.set(1, config.SELECTED_FRAME)
                                self.backwardToProcessed = False
                            else:
                                cap.set(1, config.SELECTED_FRAME)

                            iterations = config.SELECTED_FRAME
                            self.changeSelectedFrame.emit(config.SELECTED_FRAME)

                            ret, frame = cap.read()
                            frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)

                            for k in self.previewData:
                                if str(config.SELECTED_FRAME) in self.previewData[k]:

                                    valid = self.previewData[k][str(config.SELECTED_FRAME)]["valid"]
                                    x = int(self.previewData[k][str(config.SELECTED_FRAME)]["x"])
                                    y = int(self.previewData[k][str(config.SELECTED_FRAME)]["y"])
                                    w = int(self.previewData[k][str(config.SELECTED_FRAME)]["w"])
                                    h = int(self.previewData[k][str(config.SELECTED_FRAME)]["h"])

                                    if config.SELECTED_FACE >= 0:
                                        if k == str(config.SELECTED_FACE):
                                            if k in self.previewData:
                                                cropped = frame[y: (y + h), x: (x + w)]
                                                rgbImage = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                                                hs, ws, ch = rgbImage.shape
                                                bytesPerLine = ch * ws
                                                cropped2Qt = QImage(rgbImage.data, ws, hs, bytesPerLine, QImage.Format_RGB888)
                                                aux_face = self.list[str(config.SELECTED_FACE)]
                                                self.changePixmap_pick.emit(cropped2Qt,
                                                                            self.generateFaceInfo(aux_face, iterations,
                                                                                                  config.SELECTED_FACE))
                                            self.drawFaces(k, valid, frame, x, y, w, h, True)
                                        elif k != str(config.SELECTED_FACE) and not self.showOnlySelected:
                                            self.drawFaces(k, valid, frame, x, y, w, h, False)
                                    elif not self.showOnlySelected:
                                        self.drawFaces(k, valid, frame, x, y, w, h, False)

                            rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            h, w, ch = rgbImage.shape
                            bytesPerLine = ch * w
                            convertToQt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                            self.changePixmap.emit(convertToQt, perf.getVideoProgress(iterations, config.VIDEO_LENGHT))

                self.updateStatus.emit(self.setStatusText("Saving JSON file for pre-processing data..."), 2)

                for k in self.previewData:
                    coincidences += 1
                self.js.setDataSerialized(self.previewData)
                self.js.saveJson(config.PATH_TO_JSON_PRE)
                del self.previewData
                self.list.clear()
                self.updateStatus.emit(self.setStatusText("JSON file saved: " + config.PATH_TO_JSON_PRE), 1)
                config.LOG += "\n" + ts.getTime(self) + " Step 1 finished..."
                config.LOG += "\n" + ts.getTime(self) + " Json for step 1 -> " + config.PATH_TO_JSON_PRE
                config.LOG += "\n" + ts.getTime(self) + " AIWake ... [STEP 1 - PREPROCESSING - FINISHED]"
                self.updateTerminal.emit()
                cap.release()
                ret = False

            if iterations % config.SELECTED_SPEED == 0:
                iterations_ratio += 1

            self.y_data.append(founds)
            iterations += 1

            if ret and iterations % config.SELECTED_SPEED == 0 and iterations >= config.SELECTED_SPEED:
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
                        self.setPicker.emit(self.getFaceIds(self.list ,str(founds), False))
                    else:
                        for k, v in self.list.items():
                            if newFace.equal(config.PROP, self.list[k], frame):
                                newFace.occurs += self.list[k].occurs + 1
                                if newFace.occurs >= int(iterations_ratio*config.RATIO): newFace.valid = True
                                else: newFace.valid = False
                                newFace.queue(newFace, self.list[k].list)
                                self.list[k] = newFace
                                newFound = False
                                break

                    if newFound and len(self.list) > 0:
                        founds += 1
                        newFace.queue(newFace, None)
                        self.list[str(founds)] = newFace
                        self.setPicker.emit(self.getFaceIds(self.list, str(founds), False))

                    if config.DETAILED:
                        if newFace.valid:
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                            cv2.putText(frame, "Accepted", (int(x + (w * config.PROP)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                        (0, 255, 0), 1, cv2.LINE_AA)
                        else:
                            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                            cv2.putText(frame, "Rejected", (int(x + (w * config.PROP)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                        (0, 0, 255), 1, cv2.LINE_AA)

            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)

                self.changePixmap.emit(convertToQt, perf.getVideoProgress(iterations,config.VIDEO_LENGHT))
                self.updateFrameSelector.emit(iterations)

                self.jump = False

        self.updateStatus.emit(self.setStatusText("Starting post-processing..."), 2)
        self.preprocessDone.emit()

