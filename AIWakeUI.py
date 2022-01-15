from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import pyqtSlot

import sys
import DataProcessor as dp
import variables as config
import FaceIsolator as fi

#faceIsolator = fi.FaceIsolator()

class AIWake_UI(QMainWindow):
    def __init__(self):
        super(AIWake_UI, self).__init__()
        uic.loadUi("AIWake_app.ui",self)
        self.setWindowTitle("AIWake")

        self.thread = {}

        self.initUI()

    def initUI(self):
        self.bt1.clicked.connect(self.b1Click)
        self.playBt.clicked.connect(self.playBtClick)
        self.infoBt.clicked.connect(self.hazAlgo)

    def hazAlgo(self):
        self.thread[1].hazAlgo()

    def b1Click(self):
        dp.startProcessingData(config.VIDEO_LENGHT)

    def playBtClick(self):
        self.thread[1] = fi.FaceIsolator(parent=None)
        self.thread[1].start()
        self.thread[1].changePixmap.connect(self.updateVideo)

    def updateVideo(self, frame, progress):
        self.step1Video.setPixmap(QPixmap.fromImage(frame))
        self.step1Pb.setValue(progress)




    """
    @pyqtSlot(QImage)
    def step1UpdateVideo(self, frame):
        self.step 1Video.setPixmap(QPixmap.fromImage(frame))

    
    def update(self):
        self.label.adjustSize()
    """
