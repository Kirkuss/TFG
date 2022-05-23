import os
import time

from PyQt5.QtCore import QThread, pyqtSignal
import variables as config
import Utilities as Dmanager
import FaceData as data


from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class plotDataDetailed_struct():
    def __init__(self, frame, data):
        self.frame = frame
        self.data = data

class PlotterManager(QThread):
    drawing = pyqtSignal(int)

    def __init__(self, id, type, parent=None):
        # type 0 controla la vista global, type 1 controla detailed
        super(PlotterManager, self).__init__(parent)
        self.isolatorDetailedData = []
        self.id = id
        self.figure = plt.figure(type)
        self.canvas = FigureCanvas(self.figure)
        self.notFinished = True
        self.type = type
        self.y_data = []
        self.x_data = []
        self.x_data_line = []
        self.y_data_line = []
        self.labels = {"angry": 0, "disgust": 0, "fear": 0, "happy": 0, "neutral": 0, "sad": 0, "surprise": 0}
        self.lineData = {}
        self.proccessing = False
        self.js = Dmanager.jsonManager()
        self.facesInfo = {}
        self.readJson = config.JSON_POST_DONE
        self.faceList = {}
        self.x_axis = []
        self.y_axis = []
        self.plotDetections = False
        self.draw = True

    def run(self):
        self.readJson = config.JSON_POST_DONE
        self.generateYaxisLabelsForLine()
        while self.notFinished:
            print("HEY: " + str(self.type))
            if self.draw or not self.draw:
            #print("Plotter: " + str(os.getpid()) + " canvas: " + str(self.canvas))
                self.plotTest()
                if self.readJson:
                    self.facesInfo = self.js.loadJson(config.PATH_TO_JSON_POS)
                    self.readJson = False
                    self.populateFaceList()
                if config.TILL_FRAME and config.JSON_POST_DONE: time.sleep(0.2)
                elif self.proccessing: time.sleep(3)
                else: time.sleep(0.5)
        return 0

    def populateFaceList(self):
        for k in self.facesInfo:
            self.faceList[str(k)] = data.FaceData(int(k), self.facesInfo[k])
            self.faceList[str(k)].getLabels()
            print(self.faceList[str(k)])

    def calculateTillFrame(self, line):
        for k in self.facesInfo:
            for n in self.facesInfo[k]:
                if line:
                    if int(n) <= config.CURRENT_FRAME:
                        self.labels[self.facesInfo[k][n]["prediction"]] += 1
                else:
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

    def getXaxisIfLine(self, line):
        self.x_data_line.clear()
        if line:
            self.x_data_line = list(range(1, config.CURRENT_FRAME + 1))
        else:
            self.x_data_line = list(range(1, config.SELECTED_FRAME + 1))

    def getYaxisIfLine(self):
        for k in self.faceList:
            self.faceList[k].getYaxisData(self.x_data)

        if config.FACE_DATA_ONLY and config.SELECTED_FACE > 0:
            pass
        else:
            for i in self.x_data_line:
                for k in self.lineData:
                    if i > len(self.lineData[k]) or len(self.lineData[k]) == 0:
                        self.lineData[k].append(self.labels[k])

    def generateYaxisLabelsForLine(self):
        for k in self.labels: self.lineData[k] = []

    def getPlotData(self):
        self.y_data.clear()
        self.x_data.clear()
        if config.TILL_FRAME and config.JSON_POST_DONE:
            self.labels = {"angry": 0, "disgust": 0, "fear": 0, "happy": 0, "neutral": 0, "sad": 0, "surprise": 0}
            self.calculateTillFrame(False)
            self.calculatePercent()
        else:
            self.labels = {"angry": 0, "disgust": 0, "fear": 0, "happy": 0, "neutral": 0, "sad": 0, "surprise": 0}
            #self.labels = config.LABELS.copy()
            self.calculatePercent()
        for i in self.labels:
            if self.labels[i] > 0:
                self.y_data.append(i)
                self.x_data.append(self.labels[i])

    def plotTest(self, title="Data"):
        self.figure = plt.figure(self.type)
        self.figure.clear()
        print("figura: " + str(self.type) + " clear")
        if self.proccessing: self.drawWhenProcessing(title)
        else: self.drawDataDetections(self.x_axis, self.y_axis)
        self.canvas.draw()
        self.drawing.emit(self.id)
        print("figura: " + str(self.type) + " Draw")

    def drawWhenProcessing(self, title):
        self.getPlotData()
        if config.TILL_FRAME and config.SELECTED_FRAME > 0: self.getXaxisIfLine(False)
        else: self.getXaxisIfLine(True)
        self.getYaxisIfLine()
        if config.SELECTED_CHART == "Pie": self.drawPie(title)
        elif config.SELECTED_CHART == "Bar": self.drawBar(title)
        elif config.SELECTED_CHART == "Line": self.drawLine()

    def drawLine(self):
        print("LINE")
        for k in self.lineData:
            if config.TILL_FRAME and config.SELECTED_FRAME > 0: self.drawLineFaceSelected(k)
            else: self.drawLineGlobal(k)
        plt.legend()

    def drawLineGlobal(self, k):
        print("GLOBAL")
        if config.FACE_DATA_ONLY and config.SELECTED_FACE > 0:
            plt.fill_between(self.x_data_line, self.faceList[str(config.SELECTED_FACE)].labelsLine[k], alpha=0.2)
            plt.plot(self.x_data_line, self.faceList[str(config.SELECTED_FACE)].labelsLine[k], label=k)
        else:
            plt.fill_between(self.x_data_line, self.lineData[k], alpha=0.2)
            plt.plot(self.x_data_line, self.lineData[k], label=k)

    def drawLineFaceSelected(self, k):
        print("FACE")
        if config.FACE_DATA_ONLY and config.SELECTED_FACE > 0:
            plt.fill_between(self.x_data_line,
                             self.faceList[str(config.SELECTED_FACE)].labelsLine[k][0:len(self.x_data_line)], alpha=0.2)
            plt.plot(self.x_data_line, self.faceList[str(config.SELECTED_FACE)].labelsLine[k][0:len(self.x_data_line)],
                     label=k)
        else:
            plt.fill_between(self.x_data_line, self.lineData[k][0:len(self.x_data_line)], alpha=0.2)
            plt.plot(self.x_data_line, self.lineData[k][0:len(self.x_data_line)], label=k)

    def getTitleFrame(self, title):
        if config.TILL_FRAME and config.SELECTED_FRAME > 0: title += " frame: {0}".format(config.SELECTED_FRAME)
        else: title += " frame: {0}".format(config.CURRENT_FRAME)
        return title

    def drawBar(self, title):
        print("BAR")
        plt.bar(self.y_data, self.x_data)
        plt.ylabel("%")
        plt.title(self.getTitleFrame(title))

    def drawPie(self, title):
        print("PIE")
        plt.pie(self.x_data, labels=self.y_data, autopct='%1d%%', shadow=False)
        plt.axis('equal')
        plt.title(self.getTitleFrame(title))

    def drawDataDetections(self, x_axis, y_axis, title="Accepted - Rejected"):
        print("INIT " + str(self.canvas))
        plt.pie(x_axis, labels=y_axis, autopct='%1d%%', shadow=False)
        plt.axis('equal')
        plt.title(title)