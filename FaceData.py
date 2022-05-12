import variables as config

class FaceData():
    def __init__(self, id, data):
        self.labels = {}
        self.labelsLine = {}
        self.faceDict = data.copy()
        self.id = id

    def getLabels(self):
        for k in config.LABELS:
            self.labels[k] = 0
            self.labelsLine[k] = []

    def calculatePercent(self):
        total = 0
        for k in self.labels:
            total += self.labels[k]
        for k in self.labels:
            if total > 0:
                if self.labels[k] > 0:
                    self.labels[k] = (self.labels[k]/total) * 100
                else: self.labels[k] = 0

    def calculatePercentLine(self, frame):
        total = 0
        for k in self.labels:
            total += self.labels[k]
        for k in self.labels:
            if total > 0:
                if self.labels[k] > 0:
                    self.labelsLine[k].insert(frame,(self.labels[k]/total) * 100)
                else:
                    self.labelsLine[k].insert(frame, 0)
            else:
                self.labelsLine[k].insert(frame, 0)

    def generateLabels(self):
        if config.TILL_FRAME and config.JSON_POST_DONE:
            for k in self.labels:
                self.labels[k] = 0
        if config.TILL_FRAME and config.SELECTED_FRAME > 0:
            for k in self.faceDict:
                if int(k) <= config.SELECTED_FRAME:
                    self.labels[self.faceDict[k]["prediction"]] += 1
        else:
            for k in self.faceDict:
                if int(k) <= config.CURRENT_FRAME:
                    self.labels[self.faceDict[k]["prediction"]] += 1

    def generateYaxisData(self):
        for i in range(config.VIDEO_LENGHT):
            if str(i+1) in self.faceDict:
                self.labels[self.faceDict[str(i+1)]["prediction"]] += 1
            for k in self.labelsLine:
                self.calculatePercentLine(i)
                self.labelsLine[k].append(self.labels[k])
        print("Face: " + str(self.id) + " len: " + str(self.labelsLine))

    def getYaxisData(self, x_data):
        for k in self.labelsLine:
            if len(self.labelsLine[k]) == 0:
                self.generateYaxisData()
                #self.generateLabels()
                #self.calculatePercent()
        """
        for i in x_data:
            for k in self.labelsLine:
                if i > len(self.labelsLine[k]) or len(self.labelsLine[k]) == 0:
                    self.labelsLine[k].append(self.labels[k])
                elif (i > len(self.labelsLine[k]) or len(self.labelsLine[k]) == 0) and str(i) not in self.faceDict:
                    self.labelsLine[k].append(0)
        """

    def generateLabelsLine(self):
        if config.TILL_FRAME and config.SELECTED_FRAME > 0:
            for k in self.faceDict:
                if int(k) <= config.SELECTED_FRAME:
                    self.labelsLine[self.faceDict[k]["prediction"]].append(self.labels[self.faceDict[k]["prediction"]])
        else:
            for k in self.faceDict:
                if int(k) <= config.CURRENT_FRAME:
                    self.labelsLine[self.faceDict[k]["prediction"]].append(self.labels[self.faceDict[k]["prediction"]])