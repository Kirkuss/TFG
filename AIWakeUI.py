from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5 import uic
from PyQt5.QtGui import QPixmap

import DataProcessor as dp
import FaceIsolator as fi
import EmotionProc as ep
import variables as config

class AIWake_UI(QMainWindow):
    def __init__(self):
        super(AIWake_UI, self).__init__()
        uic.loadUi("AIWake_app.ui",self)
        self.setWindowTitle("AIWake")

        self.thread = {}

        self.initUI()

    def initUI(self):
        self.bt1.clicked.connect(self.b1Click)
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
        self.playBt_2.clicked.connect(self.playBtClickPost)
        self.forwardBt_step2.clicked.connect(self.forwardVideo_step2)
        self.pauseBt_2.clicked.connect(self.pauseBtClick_step2)
        self.frontTabPanel.currentChanged.connect(self.tabTest)
        self.FacePicker.currentIndexChanged.connect(self.testeo)

    def testeo(self, i):
        print ("Index: " + str(self.FacePicker.currentText()))
        config.SELECTED_FACE = int(self.FacePicker.currentText())

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
        if self.thread[1].isRunning():
            if self.thread[1].pause:
                self.thread[1].pause = False
        else:
            self.thread[1].start()
            self.thread[1].changePixmap.connect(self.updateVideo)
            self.thread[1].updateTerminal.connect(self.updateTerminal)
            self.thread[1].setPicker.connect(self.setPicker)
            self.thread[1].changePixmap_pick.connect(self.setPreview)

    def setPreview(self, cropped, info):
        self.PreviewFaceLbl.setPixmap(QPixmap.fromImage(cropped))
        infoText = info[0]
        self.imgText.setPlainText(infoText)

    def setPicker(self, idList):
        self.FacePicker.addItems(idList)
        idList.clear()

    def playBtClickPost(self):
        if self.thread[2].isRunning():
            if self.thread[2].pause:
                self.thread[2].pause = False
        else:
            self.thread[2].start()
            self.thread[2].changePixmap2.connect(self.updatePostVideo)
            self.thread[2].updateTerminal.connect(self.updateTerminal)

    def updateVideo(self, frame, progress):
        self.step1Video.setPixmap(QPixmap.fromImage(frame))
        self.step1Pb.setValue(progress)

    def updateTerminal(self):
        self.terminalInfo.setPlainText(config.LOG)

    def browseStep1Video(self):
        fileName = QFileDialog.getOpenFileName(self, "Choose a video", "C:", "Video Files (*.mp4 *.flv *.mkv)")
        config.PATH_TO_VIDEO = fileName[0]
        self.pathInText_step1.insert(str(fileName[0]))
        self.pathInText_step2.insert(str(fileName[0]))
        self.thread[1] = fi.FaceIsolator(parent=None)
        self.thread[2] = ep.EmotionProc(parent=None)

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
