import AIWakeUI
import sys

from PyQt5.QtWidgets import QApplication

def work(i):
    print("Soy un hilo: " + str(i))

def window():
    app = QApplication(sys.argv)
    win = AIWakeUI.AIWake_UI()
    win.show()
    sys.exit(app.exec_())

window()



