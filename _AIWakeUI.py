from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow

import sys
import DataProcessor as dp
import variables as config

class AIWake_UI(QMainWindow):
    def __init__(self):
        super(AIWake_UI, self).__init__()
        self.setGeometry(0, 0, 600, 600)
        self.setWindowTitle("AIWake")
        self.initUI()

    def initUI(self):
        self.label = QtWidgets.QLabel(self)
        self.label.setText("Test")
        self.move(30, 20)

        self.b1 = QtWidgets.QPushButton(self)
        self.b1.setText("Testb1")
        self.b1.move(30, 60)
        self.b1.clicked.connect(self.b1Click)

    def b1Click(self):
        dp.startProcessingData(config.VIDEO_LENGHT)

    """
    def update(self):
        self.label.adjustSize()
    """
