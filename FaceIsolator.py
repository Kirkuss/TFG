import variables as config
import cv2
import AIWakeUI
import face_DS as DS
import Utilities as Dmanager
import Performance_stats as perf

from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

class FaceIsolator(QThread):

    changePixmap = pyqtSignal(QImage, int)

    def __init__(self, parent=None):
        super(FaceIsolator, self).__init__(parent)
        self.pathToVideo = config.PATH_TO_VIDEO
        self.pathToOutput = config.PATH_TO_JSON_PRE
        self.show = True
        self.detailed = True
        self.faceCascade = cv2.CascadeClassifier(config.PATH_TO_MODEL)
        self.prop = config.PROP
        self.ratio = config.RATIO
        self.videoLenght = config.VIDEO_LENGHT
        self.js = Dmanager.jsonManager()

    def hazAlgo(self):
        print("hola")

    def run(self):

        cap = cv2.VideoCapture(self.pathToVideo)
        iterations = 0
        founds = 0
        list = {}
        faceCascade = cv2.CascadeClassifier(config.PATH_TO_MODEL)
        ratio = 0.4
        prop = 0.25

        while (cap.isOpened()):
            ret, frame = cap.read()

            if iterations == self.videoLenght:
                cleanList = {}
                coincidences = 0
                cleanList = DS.noiseOut(list)
                for k in cleanList:
                    coincidences += 1
                occRation = (coincidences/founds) * 100
                self.js.setData(cleanList, "face")
                self.js.saveJson(config.PATH_TO_JSON_PRE)
                cleanList.clear()
                list.clear()
                pass

            iterations += 1

            if ret:
                frame = cv2.resize(frame, (540, 380), fx=0, fy=0, interpolation=cv2.INTER_CUBIC)
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
                            if newFace.equal(prop, list[k], frame):
                                newFace.occurs += list[k].occurs + 1
                                if newFace.occurs >= int(iterations*ratio): newFace.valid = True
                                else: newFace.valid = False
                                newFace.queue(newFace, list[k].list)
                                list[k] = newFace
                                newFound = False
                                break

                    if newFound and len(list) > 0:
                        founds += 1
                        newFace.queue(newFace, None)
                        list[str(founds)] = newFace

                    if newFace.valid:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 1)
                        cv2.putText(frame, "Accepted", (int(x + (w * prop)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0, 255, 0), 1, cv2.LINE_AA)
                    else:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 1)
                        cv2.putText(frame, "Rejected", (int(x + (w * prop)) + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0, 0, 255), 1, cv2.LINE_AA)

                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)

                self.changePixmap.emit(convertToQt, perf.getVideoProgress(iterations,config.VIDEO_LENGHT))

                """
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)

                self.changePixmap.emit(convertToQt)
                """

                #AIWakeUI.step1UpdateVideo(frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    while True:
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    break
