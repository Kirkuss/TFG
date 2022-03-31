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
        self.barReleased = False

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

    def setStatusText(self, text):
        status = []
        status.append(text)
        return status

    def run(self):
        self.updateStatus.emit(self.setStatusText("Starting post-processing preview..."), 2)
        cap = cv2.VideoCapture(self.pathToVideo)
        self.updateStatus.emit(self.setStatusText("Waiting for user to review obtained data"), 1)

        while (cap.isOpened()):

            #if self.iterations == config.VIDEO_LENGHT:
            #   self.pause = True

            while self.pause:
                if self.writeOnPause:
                    print("Video paused at frame: " + str(self.iterations))
                    self.writeOnPause = False

            if self.barReleased:
                cap.set(1, config.SELECTED_FRAME)
                self.iterations = config.SELECTED_FRAME
                self.barReleased = False

            self.writeOnPause = True

            ret, frame = cap.read()

            if ret:
                #status
                frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)

                #FRAME TREATMENT
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
                                    #aux_face = self.list[str(config.SELECTED_FACE)]
                                    self.changePixmap_pick.emit(cropped2Qt, self.generateFaceInfo("Test"))
                                self.drawFaceInfo(k, frame, x, y, w, h, True, prediction)
                            elif k != str(config.SELECTED_FACE) and not self.showOnlySelected:
                                self.drawFaceInfo(k, frame, x, y, w, h, False, prediction)
                        elif not self.showOnlySelected:
                            self.drawFaceInfo(k, frame, x, y, w, h, False, prediction)

                        self.drawFaceInfo(k, frame, x, y, w, h, False, prediction)
                #FRAME TREATMENT

                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)

                self.changePixmap_preview.emit(convertToQt, 0)

                self.iterations += 1
                time.sleep(0.04)

            self.updateFrameSelector.emit(self.iterations)