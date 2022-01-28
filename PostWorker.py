from PyQt5.QtCore import QThread, pyqtSignal

class PostWorker(QThread):

    def __init__(self, ep, parent=None):
        super(PostWorker, self).__init__(parent)
        self.ep = ep

    def run(self):
        print(self.ep)
        exit(0)