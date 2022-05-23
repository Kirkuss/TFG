import os
import time

from PyQt5.QtGui import QPen
import variables as config
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice, QLineSeries, QBarSeries, QBarSet

from random import seed
from random import random

class PlotterManager_2(QThread):
    def __init__(self, id, chart, series, parent=None):
        # type 0 controla la vista global, type 1 controla detailed
        super(PlotterManager_2, self).__init__(parent)
        self.chart = chart
        self.series_pie = series
        self.series_bar = QBarSeries()
        self.labels = []
        self.values = []
        self.labelsHash = {}
        self.id = id
        self.change = True
        self.slices = list()
        self.sets = list()
        self.firstTimePie = True
        self.firstTimeBar = True


    def plotSelect(self):
        if config.SELECTED_CHART == "Pie":
            if self.change:
                self.series_bar.hide()
                self.series_pie.show()
                self.change = False
                if self.firstTimePie:
                    self.piePlot()
                    self.chart.addSeries(self.series_pie)
                    self.firstTimePie = False
            else:
                self.updateValues_pie()
            #print("PIE")

        elif config.SELECTED_CHART == "Bar":
            if self.change:
                self.series_pie.hide()
                self.series_bar.show()
                self.change = False
                if self.firstTimeBar:
                    self.barPlot()
                    self.chart.addSeries(self.series_bar)
                    self.firstTimeBar = False
            else:
                self.updateValues_bar()
            #print("BAR")

    def setLabels(self):
        counter = 0
        for k in self.labels:
            self.labelsHash[k] = self.values[counter]
            counter += 1

    def barPlot(self):
        self.setLabels()
        for k in self.labelsHash:
            set = QBarSet(k)
            set << self.labelsHash[k]
            self.sets.append(set)
        for s in self.sets: self.series_bar.append(s)

    def piePlot(self):
        self.setLabels()
        self.slices = list()
        for k in self.labelsHash:
            self.slices.append(QPieSlice(k, self.labelsHash[k]))
        for s in self.slices: self.series_pie.append(s)

    def updateValues_pie(self):
        self.setLabels()
        for k in self.series_pie.slices():
            k.setValue(self.labelsHash[k.label()])

    def updateValues_bar(self):
        self.setLabels()
        for k in self.series_bar.barSets():
            k.replace(0, self.labelsHash[k.label()])

    def run(self):
        while len(self.labels) <= 0 and len(self.values) <= 0: time.sleep(0.033)
        while True:
            self.plotSelect()
            time.sleep(0.033)


