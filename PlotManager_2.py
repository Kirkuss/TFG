import os
import time

from PyQt5.QtGui import QPen, QPainter
import variables as config
from PyQt5.QtCore import Qt, QThread, QPoint, QPointF
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice, QLineSeries, QBarSeries, QBarSet, QValueAxis

from random import seed
from random import random

class PlotterManager_2(QThread):
    def __init__(self, id, chart, series, parent=None):
        # type 0 controla la vista global, type 1 controla detailed
        super(PlotterManager_2, self).__init__(parent)
        self.chart = chart
        self.series_pie = series
        self.series_bar = QBarSeries()
        self.series_line = {}
        self.series_lineProcessing = {}
        self.series_pieProcessing = QPieSeries()
        self.series_barProcessing = QBarSeries()
        self.labels = []
        self.values = []
        self.labelsHash = {}
        self.labelsHashProcessing = {}
        self.id = id
        self.change = True
        self.slices = list()
        self.slicesProcessing = list()
        self.sets = list()
        self.setsProcessing = list()
        self.firstTimePie = True
        self.firstTimeBar = True
        self.firstTimeLine = True
        self.frame = 0
        self.processing = False
        self.firstTimePieProcessing = True
        self.firstTimeBarProcessing = True
        self.firstTimeLineProcessing = True
        self.initial = True
        self.initialProcessing = True
        self.test = True
        self.last = 0

    def plotSelect_processing(self):
        if self.test:
            self.series_bar.hide()
            self.chart.removeSeries(self.series_bar)
            for l in self.series_line:
                self.series_line[l].hide()
                self.chart.removeSeries(self.series_line[l])
            self.series_pie.hide()
            self.chart.removeSeries(self.series_pie)
            self.test = False

        print("PRIMER IF")

        if self.initialProcessing:
            self.linePlotProcessing()
            for s in self.series_lineProcessing:
                self.chart.addSeries(self.series_lineProcessing[s])
                self.chart.setAxisX(self.chart.axes(Qt.Horizontal)[0], self.series_lineProcessing[s])
                self.chart.setAxisY(self.chart.axes(Qt.Vertical)[0], self.series_lineProcessing[s])
            #self.chart.createDefaultAxes(
            self.initialProcessing = False

        print("to puesto")

        if config.SELECTED_CHART == "Pie":
            if self.change:
                self.series_barProcessing.hide()
                for l in self.series_lineProcessing:
                    self.series_lineProcessing[l].hide()
                self.change = False
                if not self.initial:
                    self.chart.axes(Qt.Horizontal)[0].setVisible(False)
                    self.chart.axes(Qt.Vertical)[0].setVisible(False)
                if self.firstTimePieProcessing:
                    self.piePlotProcessing()
                    self.chart.addSeries(self.series_pieProcessing)
                    self.firstTimePieProcessing = False
                self.series_pieProcessing.show()
            else:
                self.updateValues_pieProcessing()

        elif config.SELECTED_CHART == "Bar":
            if self.change:
                self.series_pieProcessing.hide()
                for l in self.series_lineProcessing:
                    self.series_lineProcessing[l].hide()
                self.change = False
                if not self.initial:
                    self.chart.axes(Qt.Horizontal)[0].setVisible(False)
                    self.chart.axes(Qt.Vertical)[0].setVisible(True)
                if self.firstTimeBarProcessing:
                    self.barPlotProcessing()
                    self.chart.addSeries(self.series_barProcessing)
                    self.chart.setAxisY(self.chart.axes(Qt.Vertical)[0], self.series_barProcessing)
                    self.firstTimeBarProcessing = False
                self.series_barProcessing.show()
            else:
                self.updateValues_barProcessing()

        elif config.SELECTED_CHART == "Line":
            if self.change:
                self.series_pieProcessing.hide()
                self.series_barProcessing.hide()
                self.change = False
                if not self.initial:
                    self.chart.axes(Qt.Horizontal)[0].setVisible(True)
                    self.chart.axes(Qt.Vertical)[0].setVisible(True)
                for l in self.series_lineProcessing:
                    self.series_lineProcessing[l].show()

    def calculatePercent(self):
        total = 0
        for k in self.labelsHashProcessing:
            total += self.labelsHashProcessing[k]
        for k in self.labelsHashProcessing:
            if total > 0:
                if self.labelsHashProcessing[k] > 0:
                    self.labelsHashProcessing[k] = (self.labelsHashProcessing[k]/total) * 100
                else: self.labelsHashProcessing[k] = 0

    def calculatePercent_alt(self):
        total = 0
        for k in self.labelsHash:
            total += self.labelsHash[k]
        for k in self.labelsHash:
            if total > 0:
                if self.labelsHash[k] > 0:
                    self.labelsHash[k] = (self.labelsHash[k]/total) * 100
                else: self.labelsHash[k] = 0

    def updateValues_lineProcessing(self):
        self.labelsHashProcessing = config.LABELS.copy()
        self.calculatePercent()
        for s in self.series_lineProcessing:
            point = QPoint(config.CURRENT_FRAME, self.labelsHashProcessing[s])
            self.series_lineProcessing[s] << point

    def linePlotProcessing(self):
        self.labelsHashProcessing = config.LABELS.copy()
        self.calculatePercent()
        for k in self.labelsHashProcessing:
            self.series_lineProcessing[k] = QLineSeries()
            self.series_lineProcessing[k].setName(k)
        for s in self.series_lineProcessing:
            point = QPoint(config.CURRENT_FRAME, self.labelsHashProcessing[s])
            self.series_lineProcessing[s] << point

    def updateValues_barProcessing(self):
        self.labelsHashProcessing = config.LABELS.copy()
        self.calculatePercent()
        for k in self.series_barProcessing.barSets():
            k.replace(0, self.labelsHashProcessing[k.label()])

    def barPlotProcessing(self):
        self.calculatePercent()
        for k in self.labelsHashProcessing:
            set = QBarSet(k)
            set << self.labelsHashProcessing[k]
            self.setsProcessing.append(set)
        for s in self.setsProcessing: self.series_barProcessing.append(s)

    def updateValues_pieProcessing(self):
        self.calculatePercent()
        for k in self.series_pieProcessing.slices():
            k.setValue(self.labelsHashProcessing[k.label()])

    def piePlotProcessing(self):
        self.labelsHashProcessing = config.LABELS.copy()
        self.calculatePercent()
        self.slicesProcessing = list()
        for k in self.labelsHashProcessing:
            self.slicesProcessing.append(QPieSlice(k, self.labelsHashProcessing[k]))
        for s in self.slicesProcessing: self.series_pieProcessing.append(s)

    def plotSelect_preprocess(self):
        if config.SELECTED_CHART == "Pie":
            if self.change:
                self.series_bar.hide()
                for l in self.series_line:
                    self.series_line[l].hide()
                self.series_pie.show()
                self.change = False
                if not self.initial:
                    self.chart.axes(Qt.Horizontal)[0].setVisible(False)
                    self.chart.axes(Qt.Vertical)[0].setVisible(False)
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
                for l in self.series_line:
                    self.series_line[l].hide()
                self.series_bar.show()
                self.change = False
                if not self.initial:
                    self.chart.axes(Qt.Horizontal)[0].setVisible(False)
                    self.chart.axes(Qt.Vertical)[0].setVisible(True)
                if self.firstTimeBar:
                    self.barPlot()
                    self.chart.addSeries(self.series_bar)
                    self.chart.setAxisY(self.chart.axes(Qt.Vertical)[0], self.series_bar)
                    self.firstTimeBar = False
            else:
                self.updateValues_bar()
            #print("BAR")

        elif config.SELECTED_CHART == "Line":
            if self.change:
                self.series_pie.hide()
                self.series_bar.hide()
                for l in self.series_line:
                    self.series_line[l].show()
                self.change = False
                if not self.initial:
                    self.chart.axes(Qt.Horizontal)[0].setVisible(True)
                    self.chart.axes(Qt.Vertical)[0].setVisible(True)

        if self.initial:
            for s in self.series_line:
                self.chart.addSeries(self.series_line[s])
                print(self.series_line[s])
                self.chart.createDefaultAxes()
                self.chart.axes(Qt.Vertical)[0].setRange(float(0), float(100))
                self.chart.axes(Qt.Horizontal)[0].setRange(float(0),float(config.VIDEO_LENGHT))
                self.initial = False

    def setLabels(self):
        counter = 0
        for k in self.labels:
            self.labelsHash[k] = self.values[counter]
            counter += 1

    def barPlot(self):
        self.setLabels()
        self.calculatePercent_alt()
        for k in self.labelsHash:
            set = QBarSet(k)
            set << self.labelsHash[k]
            self.sets.append(set)
        for s in self.sets: self.series_bar.append(s)

    def piePlot(self):
        self.setLabels()
        self.calculatePercent_alt()
        self.slices = list()
        for k in self.labelsHash:
            self.slices.append(QPieSlice(k, self.labelsHash[k]))
        for s in self.slices: self.series_pie.append(s)

    def linePlot(self):
        self.setLabels()
        self.calculatePercent_alt()
        for k in self.labels:
            if k == "Rejected":
                self.series_line[k] = QLineSeries()
                self.series_line[k].setName(k)
        for s in self.series_line:
            if s == "Rejected":
                point = QPoint(self.frame, self.labelsHash[s])
                self.series_line[s] << point

    def updateValues_pie(self):
        self.setLabels()
        self.calculatePercent_alt()
        for k in self.series_pie.slices():
            k.setValue(self.labelsHash[k.label()])

    def updateValues_bar(self):
        self.setLabels()
        self.calculatePercent_alt()
        for k in self.series_bar.barSets():
            k.replace(0, self.labelsHash[k.label()])

    def updateValues_line(self):
        self.setLabels()
        self.calculatePercent_alt()
        for s in self.series_line:
            if s == "Rejected" and self.last != self.frame:
                self.last = self.frame
                point = QPoint(self.frame, self.labelsHash[s])
                print(str(str(self.frame) + " . " + str(self.labelsHash[s])))
                self.series_line[s] << point

    def run(self):
        line = True
        while len(self.labels) <= 0 and len(self.values) <= 0: time.sleep(0.033)
        while True:
            if config.CURRENT_FRAME > 0:
                if line:
                    self.linePlot()
                    line = False
                if self.processing:
                    self.plotSelect_processing()
                else:
                    self.plotSelect_preprocess()
            time.sleep(0.15)


