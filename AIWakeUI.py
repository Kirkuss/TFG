from PyQt5.QtWidgets import QMainWindow, QFileDialog, QDialog
from PyQt5 import uic
from PyQt5.QtGui import QPixmap

import DataProcessor as dp
import FaceIsolator as fi
import EmotionProc as ep
import variables as config
import postPreview as pp
import PostDialog as pd

class AIWake_UI(QMainWindow):
    def __init__(self):
        super(AIWake_UI, self).__init__()
        uic.loadUi("AIWake_app.ui",self)
        self.setWindowTitle("AIWake")

        self.testing = True
        self.thread = {}
        self.currentThread = [True, False, False]

        self.initUI()

    def initUI(self):

        #self.moodOpts = ["angry", "disgust", "fear", "happy", "neutral", "sad", "surprise"]

        self.playBt.clicked.connect(self.playBtClick)
        self.showBoxesCb.stateChanged.connect(self.previewChange_showHB)
        self.showDetailedCb.stateChanged.connect(self.previewChange_showDE)
        self.pauseBt.clicked.connect(self.pauseBtClick_step1)
        self.selectFile_step1.clicked.connect(self.browseStep1Video)
        self.detection_ratio.valueChanged.connect(self.updateDetect)
        self.acceptanceLbl.setText(str(self.detection_ratio.value()/100))
        self.hb_detection_prop.valueChanged.connect(self.updateThreshold)
        self.thresholdLbl.setText(str(self.hb_detection_prop.value()/100))
        self.forwardBt_step1.clicked.connect(self.forwardVideo_step1)
        self.frontTabPanel.currentChanged.connect(self.tabTest)
        self.FacePicker.currentIndexChanged.connect(self.testeo)
        self.FacePicker_pos.currentIndexChanged.connect(self.testeo)
        self.deleteBt.clicked.connect(self.deleteFace)
        self.statusColor.setStyleSheet("background-color: yellow;")
        #self.startPostProcessBt.clicked.connect(self.startPostProcessing)
        self.finishStep1Bt.clicked.connect(self.finishStep1)
        self.frameSelector.sliderReleased.connect(self.sliderReleased)
        self.frameSelector.valueChanged.connect(self.testSlider)
        self.frameSelector.sliderPressed.connect(self.sliderPressed)
        self.showSelectedOnlyCb.stateChanged.connect(self.showOnlySelected)
        self.deleteAutomatCb.stateChanged.connect(self.deleteAllAutomatically)
        self.deleteAllRejected.clicked.connect(self.deleteAll)
        self.deleteFaceFrameBt.clicked.connect(self.deleteFaceFrame)
        self.start3Test.clicked.connect(self.startTest)

    def getMoodOptions(self):
        moods = self.moodOptions.text()
        print(moods)
        return moods.replace(" ","").split(",")

    def sliderPressed(self):
        if self.currentThread[2]:
            self.thread[3].pause = True

    def startTest(self):
        self.thread[3] = pp.postPreview(parent=None)
        self.thread[3].changePixmap_preview.connect(self.updateVideo)
        self.thread[3].changePixmap_pick.connect(self.setPreview)
        self.thread[3].updateFrameSelector.connect(self.updateFrameSelector)
        self.thread[3].start()

    def setPickerMood(self, mood):
        self.moodSelector.setCurrentText(mood[0])

    def deleteFaceFrame(self):
        self.thread[1].deleteFaceFrame()

    def deleteAll(self):
        if self.thread[1].done:
            self.FacePicker.clear()
            self.FacePicker_pos.clear()
        self.thread[1].deleteAllRejected()

    def deleteAllAutomatically(self, state):
        if state == 2:
            self.thread[1].deleteAuto = True
        else:
            self.thread[1].deleteAuto = False

    def showOnlySelected(self, state):
        if config.SELECTED_FACE > 0:
            if state == 2:
                self.thread[1].showOnlySelected = True
            else:
                self.thread[1].showOnlySelected = False

    def testSlider(self):
        config.SELECTED_FRAME = self.frameSelector.value()

    def sliderReleased(self):
        self.thread[1].selecting = True
        if self.currentThread[2]:
            self.thread[3].barReleased = True

    def finishStep1(self):
        self.thread[1].finished = True

    def startPostProcessing(self):
        self.currentThread[0] = False
        self.currentThread[1] = True
        self.thread[2] = ep.EmotionProc(parent=None)
        self.thread[2].postPbValue.connect(self.setPostProgress)
        self.thread[2].done.connect(self.startPostPreview)
        self.thread[2].updateStatus.connect(self.updateStatus)
        self.thread[2].start()

    def startPostPreview(self):
        self.currentThread[1] = False
        self.currentThread[2] = True
        self.moodSelector.addItems(self.getMoodOptions())
        self.thread[3] = pp.postPreview(parent=None)
        self.thread[3].changePixmap_preview.connect(self.updateVideo)
        self.thread[3].changePixmap_pick.connect(self.setPreview)
        self.thread[3].updateFrameSelector.connect(self.updateFrameSelector)
        self.thread[3].updateStatus.connect(self.updateStatus)
        self.thread[3].setPickerMood.connect(self.setPickerMood)
        self.thread[3].start()

    def setPostProgress(self, progress):
        self.postPb.setValue(progress)

    def deleteFace(self):
        self.FacePicker.clear()
        self.FacePicker_pos.clear()
        self.thread[1].deleteFace()

    def testeo(self, i):
        if i >= 0:
            self.FacePicker_pos.setCurrentIndex(i)
            self.FacePicker.setCurrentIndex(i)
            print ("Index: " + str(i))
            config.SELECTED_FACE = int(self.FacePicker_pos.currentText())
            self.thread[1].sig = False

    def tabTest(self, index):
        try:
            if index == 0:
                if self.thread[2].isRunning():
                    print("2 running")
                    #self.thread[2].wait(self.mutexTab2)
            elif index == 1:
                if self.thread[1].isRunning():
                    print("1 running")
                    #self.thread[1].wait(self.mutexTab1)
                else: print("1 finished")

        except Exception as e:
            print(str(e))

    def forwardVideo_step1(self):
        self.thread[1].pause = True
        self.thread[1].jump = True

    def forwardVideo_step2(self):
        self.thread[2].pause = True
        self.thread[2].jump = True

    def updateThreshold(self):
        value = self.hb_detection_prop.value()
        self.thresholdLbl.setText(str(value/100))
        config.PROP = value/100

    def updateDetect(self):
        value = self.detection_ratio.value()
        self.acceptanceLbl.setText(str(value/100))
        config.RATIO = value/100

    def pauseBtClick_step1(self):
        if self.currentThread[2]:
            self.thread[3].pause = True
        elif self.currentThread[0]:
            self.thread[1].pause = True

    def pauseBtClick_step2(self):
        self.thread[2].pause = True

    def previewChange_showHB(self):
        if self.showBoxesCb.isChecked(): config.SHOW_HB = True
        else: config.SHOW_HB = False

    def previewChange_showDE(self):
        if self.showDetailedCb.isChecked(): config.DETAILED = True
        else: config.DETAILED = False

    def b1Click(self):
        dp.startProcessingData(config.VIDEO_LENGHT)

    def playBtClick(self):
        if self.currentThread[0]:
            if self.thread[1].isRunning():
                self.thread[1].pause = False
            else:
                self.thread[1].start()
                self.thread[1].updateFrameSelector.connect(self.updateFrameSelector)
                self.thread[1].changePixmap.connect(self.updateVideo)
                self.thread[1].updateTerminal.connect(self.updateTerminal)
                self.thread[1].updateStatus.connect(self.updateStatus)
                self.thread[1].setPicker.connect(self.setPicker)
                self.thread[1].changePixmap_pick.connect(self.setPreview)
                self.thread[1].preprocessDone.connect(self.startPostProcessing)
                self.frameSelector.setMaximum(config.VIDEO_LENGHT)
        elif self.currentThread[2]:
            self.thread[3].pause = False

    def updateFrameSelector(self, frame):
        self.frameSelector.setValue(frame)

    def updateStatus(self, text, color):
        if color == 1: self.statusColor.setStyleSheet("background-color: green;")
        elif color == 2: self.statusColor.setStyleSheet("background-color: yellow;")
        elif color == 3: self.statusColor.setStyleSheet("background-color: red;")

        self.statusText.setText(text[0])


    def setPreview(self, cropped, info):
        self.PreviewFaceLbl.setPixmap(QPixmap.fromImage(cropped))
        self.PreviewFaceLblMood.setPixmap(QPixmap.fromImage(cropped))
        #infoText = info[0] + "\n" + info[1] + "\n" + info[2] + "\n" + info[3]
        infoText = "Test"
        self.imgText.setPlainText(infoText)

    def setPicker(self, idList):
        if self.thread[1].done and self.thread[1].deleteAuto:
            self.FacePicker.clear()
            self.FacePicker_pos.clear()
        self.FacePicker.addItems(idList)
        self.FacePicker_pos.addItems(idList)
        idList.clear()

    def playBtClickPost(self):
        if self.currentThread[1]:
            if self.thread[2].pause:
                self.thread[2].pause = False
        else:
            self.thread[2].start()
            self.thread[2].changePixmap2.connect(self.updatePostVideo)
            self.thread[2].updateTerminal.connect(self.updateTerminal)

    def updateVideo(self, frame, progress):
        self.step1Video.setPixmap(QPixmap.fromImage(frame))
        self.postPb.setValue(progress)

    def updateTerminal(self):
        pass
        #self.terminalInfo.setPlainText(config.LOG)

    def browseStep1Video(self):
        fileName = QFileDialog.getOpenFileName(self, "Choose a video", "C:", "Video Files (*.mp4 *.flv *.mkv)")
        config.PATH_TO_VIDEO = fileName[0]
        self.pathInText_step1.insert(str(fileName[0]))
        self.thread[1] = fi.FaceIsolator(parent=None)
        #self.thread[2] = ep.EmotionProc(parent=None)

    def updatePostVideo(self, frame, progress):
        self.step2Video.setPixmap(QPixmap.fromImage(frame))
        self.step2Pb.setValue(progress)





    """
    @pyqtSlot(QImage)
    def step1UpdateVideo(self, frame):
        self.step 1Video.setPixmap(QPixmap.fromImage(frame))

    
    def update(self):
        self.label.adjustSize()
    """
