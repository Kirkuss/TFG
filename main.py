import AIWakeUI
import sys

from PyQt5.QtWidgets import QApplication

def window():
    app = QApplication(sys.argv)
    win = AIWakeUI.AIWake_UI()
    win.show()
    sys.exit(app.exec_())

try:
    window()
except Exception as e:
    print(str(e))



