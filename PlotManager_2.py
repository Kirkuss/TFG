import os
import time

from PyQt5.QtGui import QPen
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice

from random import seed
from random import random

class PlotterManager_2(QThread):
    def __init__(self, id, chart, series, parent=None):
        # type 0 controla la vista global, type 1 controla detailed
        super(PlotterManager_2, self).__init__(parent)
        self.chart = chart
        self.series = series
        self.id = id

    def run(self):
        slices = list()
        seed(self.id)
        slices.append(QPieSlice("1", random()))
        slices.append(QPieSlice("2", random()))
        slices.append(QPieSlice("3", random()))
        slices.append(QPieSlice("4", random()))
        for k in slices:
            self.series.append(k)
        while True:
            for k in self.series.slices():
                #print(str(k) + " id: " + str(self.id))
                k.setValue(random())
            self.chart.addSeries(self.series)
            time.sleep(0.033)


