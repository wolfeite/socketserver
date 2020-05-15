import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from gui import Gui
from libs.Tcp import createWebSocket as cw

if __name__ =="__main__":
    gui = Gui()
    QApp = QApplication(sys.argv)
    gui.init()
    cwApp = cw(number=3)
    #QApp.exec_()
    sys.exit(QApp.exec_())


