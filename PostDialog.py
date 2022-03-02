import gc

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QThread

import EmotionProc as ep

class PostDialog(QDialog):
    def __init__(self, parent=None):
        super(PostDialog, self).__init__(parent)
        loadUi("Post_process_info/postProcessingInfo.ui", self)

        self.thread = {}

    def __del__(self):
        del(self.thread[1])
        gc.collect()
        print("destroyed")

    def showEvent(self, event):
        self.thread[1] = ep.EmotionProc(parent=None)
        self.thread[1].run()
