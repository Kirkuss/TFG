import time

from PyQt5.QtCore import QThread, pyqtSignal
import matplotlib.pyplot as plt
import variables as config
import Utilities as Dmanager

class PlotterManager(QThread):
    def __init__(self, canvas, figure,parent=None):
        super(PlotterManager, self).__init__(parent)
        self.canvas = canvas
        self.figure = figure
        self.notFinished = True
        self.y_data = []
        self.x_data = []
        self.labels = {}
        self.proccessing = False
        self.js = Dmanager.jsonManager()
        self.facesInfo = {}
        self.readJson = config.JSON_POST_DONE

    def run(self):
        self.readJson = config.JSON_POST_DONE
        while self.notFinished:
            if self.proccessing:
                self.getPlotData()
                self.plotTest()
                #print("plotter running in 2")
            else:
                pass

            if self.readJson:
                self.facesInfo = self.js.loadJson(config.PATH_TO_JSON_POS)
                self.readJson = False
            if config.TILL_FRAME and config.JSON_POST_DONE:
                time.sleep(0.2)
            else:
                time.sleep(3)
        return 0

    def calculateTillFrame(self):
        for k in self.facesInfo:
            for n in self.facesInfo[k]:
                if int(n) <= config.SELECTED_FRAME:
                    self.labels[self.facesInfo[k][n]["prediction"]] += 1

    def calculatePercent(self):
        total = 0
        for k in self.labels:
            total += self.labels[k]
        for k in self.labels:
            if total > 0:
                if self.labels[k] > 0:
                    self.labels[k] = (self.labels[k]/total) * 100
                else: self.labels[k] = 0

    def getPlotData(self):
        self.y_data.clear()
        self.x_data.clear()
        if config.TILL_FRAME and config.JSON_POST_DONE:
            self.labels = {"angry": 0, "disgust": 0, "fear": 0, "happy": 0, "neutral": 0, "sad": 0, "surprise": 0}
            self.calculateTillFrame()
            self.calculatePercent()
        else:
            self.labels = config.LABELS.copy()
            self.calculatePercent()
        for i in self.labels:
            if self.labels[i] > 0:
                self.y_data.append(i)
                self.x_data.append(self.labels[i])

    def plotTest(self, x_label="Frames", y_label="Detections", title="Data"):
        self.figure.clear()
        plt.pie(self.x_data,labels=self.y_data , autopct='%1d%%', shadow=False)
        plt.axis('equal')
        # plt.ylabel(y_label)
        plt.title(title)
        self.canvas.draw()

    def drawDataDetections(self, x_axis, y_axis, x_label="Frames", y_label="Detections", title="Data"):
        self.figure.clear()
        plt.plot(x_axis, y_axis)
        plt.xlabel(x_label)
        # plt.ylabel(y_label)
        plt.title(title)
        self.canvas.draw()