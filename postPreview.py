import time

import variables as config
import Utilities as Dmanager
import cv2

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

class postPreview(QThread):

    changePixmap_preview = pyqtSignal(QImage, int)
    updateStatus_preview = pyqtSignal(list, int)
    changePixmap_pick = pyqtSignal(QImage, list)
    updateFrameSelector = pyqtSignal(int)
    updateStatus = pyqtSignal(list, int)
    setPickerMood = pyqtSignal(list)
    setPicker = pyqtSignal(list)

    def __init__(self, parent=None):
        super(postPreview, self).__init__(parent)
        self.pathToVideo = config.PATH_TO_VIDEO
        self.js = Dmanager.jsonManager()
        self.facesInfo = self.js.loadJson(config.PATH_TO_JSON_POS)
        self.iterations = 1
        self.showOnlySelected = False
        self.finished = False
        self.pause = False
        self.writeOnPause = True
        self.firstTime = True
        self.barReleased = False
        self.forward = False
        self.forwardToProcessed = False
        self.backward = False
        self.backwardToProcessed = False

    def getFaceIds(self, faceList, k, delete):
        idList = []
        if delete:
            for k, v in faceList.items():
                idList.append(k)
        else:
            idList.append(k)
        return idList

    def generateFaceInfo(self, sample):
        list = []
        list.append(sample)
        return list

    def drawFaceInfo(self, id, frame, x, y, w, h, selected, pred):
        if config.DETAILED:
            if selected:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 255, 255), 2)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                cv2.putText(frame, id + " " + pred, (int(x + (w * config.PROP)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5,
                            (0, 255, 0), 1, cv2.LINE_AA)
            elif not self.showOnlySelected:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0),
                              1)
                cv2.putText(frame, id + " " + pred, (int(x + (w * config.PROP)) + 5, y - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (0, 255, 0), 1, cv2.LINE_AA)
        return frame

    def setStatusText(self, text):
        status = []
        status.append(text)
        return status

    def setFaceFrameMood(self, mood):
        self.facesInfo[str(config.SELECTED_FACE)][str(self.iterations)]["prediction"] = mood

    def deleteFaceFrameMood(self):
        del self.facesInfo[str(config.SELECTED_FACE)][str(self.iterations)]

    def setFaceFrameMoodAll(self, mood):
        for k in self.facesInfo[str(config.SELECTED_FACE)]:
            self.facesInfo[str(config.SELECTED_FACE)][k]["prediction"] = mood

    def deleteAll(self):
        if config.SELECTED_FACE > 0:
            del self.facesInfo[str(config.SELECTED_FACE)]
            self.setPicker.emit(self.getFaceIds(self.facesInfo, "0", True))

    def processFaces(self, frame):
        if frame is not None:
            for k in self.facesInfo:
                if str(self.iterations) in self.facesInfo[k]:
                    prediction = self.facesInfo[k][str(self.iterations)]["prediction"]
                    x = int(self.facesInfo[k][str(self.iterations)]["x"])
                    y = int(self.facesInfo[k][str(self.iterations)]["y"])
                    w = int(self.facesInfo[k][str(self.iterations)]["w"])
                    h = int(self.facesInfo[k][str(self.iterations)]["h"])

                    if config.SELECTED_FACE >= 0:
                        if k == str(config.SELECTED_FACE):
                            if k in self.facesInfo:
                                cropped = frame[y: (y + h), x: (x + w)]
                                rgbImage = cv2.cvtColor(cropped, cv2.COLOR_BGR2RGB)
                                hs, ws, ch = rgbImage.shape
                                bytesPerLine = ch * ws
                                cropped2Qt = QImage(rgbImage.data, ws, hs, bytesPerLine, QImage.Format_RGB888)
                                # aux_face = self.list[str(config.SELECTED_FACE)]
                                if self.firstTime:
                                    self.setPickerMood.emit([prediction])
                                    self.firstTime = False
                                self.changePixmap_pick.emit(cropped2Qt, self.generateFaceInfo("Test"))
                            frame = self.drawFaceInfo(k, frame, x, y, w, h, True, prediction)
                        elif k != str(config.SELECTED_FACE) and not self.showOnlySelected:
                            frame = self.drawFaceInfo(k, frame, x, y, w, h, False, prediction)
                    elif not self.showOnlySelected:
                        frame = self.drawFaceInfo(k, frame, x, y, w, h, False, prediction)
                    #else:
                    #    self.drawFaceInfo(k, frame, x, y, w, h, False, prediction)

            print("[" + str(self.iterations) + "] Frame procesado: " + str(id(frame)))

    def getNearestProcessed(self, iterations):
        aux_iterations = iterations
        founds = []
        if self.forwardToProcessed:
            for k in self.facesInfo:
                while True:
                    aux_iterations += 1
                    str_iterations = str(aux_iterations)
                    if aux_iterations > config.VIDEO_LENGHT:
                        aux_iterations = iterations
                        break
                    if str_iterations in self.facesInfo[k]:
                        founds.append(aux_iterations)
                        aux_iterations = iterations
                        break
            if len(founds) == 0:
                return -1
            return min(founds)
        elif self.backwardToProcessed:
            for k in self.facesInfo:
                while True:
                    aux_iterations -= 1
                    str_iterations = str(aux_iterations)
                    if aux_iterations < 0:
                        aux_iterations = iterations
                        break
                    if str_iterations in self.facesInfo[k]:
                        founds.append(aux_iterations)
                        aux_iterations = iterations
                        break
            if len(founds) == 0:
                return -1
            return max(founds)
        return -1

    def run(self):
        self.updateStatus.emit(self.setStatusText("Starting post-processing preview..."), 2)
        cap = cv2.VideoCapture(self.pathToVideo)
        self.updateStatus.emit(self.setStatusText("Waiting for user to review obtained data"), 1)

        while (cap.isOpened()):

            #if self.iterations == config.VIDEO_LENGHT:
            #   self.pause = True

            while self.pause:
                print("1: " + str(config.SELECTED_FRAME <= config.VIDEO_LENGHT))
                print(str(config.SELECTED_FRAME > 0))

                if self.forward:
                    config.SELECTED_FRAME += 1
                    cap.set(1, config.SELECTED_FRAME)
                    self.forward = False
                elif self.forwardToProcessed:
                    res = self.getNearestProcessed(self.iterations)
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
                    res = self.getNearestProcessed(self.iterations)
                    if res < 0:
                        pass
                    else:
                        config.SELECTED_FRAME = res
                    cap.set(1, config.SELECTED_FRAME)
                    self.backwardToProcessed = False
                else:
                    cap.set(1, config.SELECTED_FRAME)

                if config.SELECTED_FRAME <= config.VIDEO_LENGHT and config.SELECTED_FRAME > 0:

                    self.iterations = config.SELECTED_FRAME
                    self.updateFrameSelector.emit(config.SELECTED_FRAME)

                    ret, frame = cap.read()
                    if frame is not None:
                        frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
                        print("[" + str(self.iterations) + "] Frame antes: " + str(id(frame)))
                        print(str(self.iterations))
                        self.processFaces(frame)
                        print("frame pocho")
                        rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        h, w, ch = rgbImage.shape
                        bytesPerLine = ch * w
                        convertToQt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                        # print(str(convertToQt))
                        self.changePixmap_preview.emit(convertToQt, 0)
                if self.writeOnPause:
                    print("Video paused at frame: " + str(self.iterations))
                    self.writeOnPause = False

            if self.barReleased:
                print("Bar released")
                #cap.set(1, config.SELECTED_FRAME)
                self.iterations = config.SELECTED_FRAME
                self.barReleased = False

            self.writeOnPause = True

            ret, frame = cap.read()

            if ret:
                #status
                frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)

                #FRAME TREATMENT
                print("SI VES ESTO ALGO PASA")
                self.processFaces(frame)
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                # print(str(convertToQt))
                self.changePixmap_preview.emit(convertToQt, 0)

                self.iterations += 1

                if self.iterations == 2:
                    config.SELECTED_FRAME = 2
                    self.pause = True

                if self.iterations == config.VIDEO_LENGHT:
                    self.pause = True

            self.updateFrameSelector.emit(self.iterations)