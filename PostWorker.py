from PyQt5.QtCore import pyqtSignal, QThread
import variables as config
import time

class PostWorker(QThread):
    iterationDone = pyqtSignal(int, int, int)

    def __init__(self, i , blocker, iteration, parent=None):
        super().__init__(parent)
        self.blocker = blocker
        self.iteration = iteration
        self.parent = parent
        self.next = 0
        self.done = 0
        self.pr = True
        self.i = i

    def goNext(self, signal):
        self.next = signal

    def run(self):

        self.parent.unlock.connect(self.goNext)

        while self.iteration <= config.VIDEO_LENGHT:
            print("Hilo " + str(self.i) + " procesando en iteracion: " + str(self.iteration) + "\n")
            #time.sleep(10)
            self.done = 1
            self.iterationDone.emit(self.i, 1, self.iteration)

            while self.next == 0:
                #self.iterationDone.emit(self.i, 1, self.iteration)
                if self.pr:
                    #print("Hilo " + str(self.i) + " en espera" + "\n")
                    self.pr = False

            #print("Hilo " + str(self.i) + " pasa a la siguiente iteracion\n")

            self.iteration += 1
            self.next = 0
            self.done = 0
            self.pr = True


