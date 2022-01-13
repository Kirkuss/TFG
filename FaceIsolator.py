import variables as config
import cv2
import AIWakeUI
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QImage

class FaceIsolator(QThread):

    changePixmap = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super(FaceIsolator, self).__init__(parent)
        self.pathToVideo = config.PATH_TO_VIDEO
        self.pathToOutput = config.PATH_TO_JSON_PRE
        self.show = True
        self.detailed = True
        self.faceCascade = cv2.CascadeClassifier(config.PATH_TO_MODEL)
        self.prop = config.PROP
        self.ratio = config.RATIO

    def hazAlgo(self):
        print("hola")

    def run(self):

        cap = cv2.VideoCapture(self.pathToVideo)

        while (cap.isOpened()):
            ret, frame = cap.read()

            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQt = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)

                self.changePixmap.emit(convertToQt)

                #AIWakeUI.step1UpdateVideo(frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    while True:
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    break
