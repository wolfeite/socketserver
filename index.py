import sys
from PyQt5.QtWidgets import QApplication
from gui import Gui
from libs.socket import tcpSocketServerApp as tssApp, webSocketServerApp as wssApp
from app import createTestApp
from PyQt5.QtCore import QTimer
import threading

if __name__ == "__main__":
    gui = Gui()
    QApp = QApplication(sys.argv)
    gui.init()
    tsApp = tssApp(("0.0.0.0", 6868))
    wsApp = wssApp(("0.0.0.0", 6869))
    createTestApp(gui, tsApp, wsApp)

    # QApp.exec_()
    sys.exit(QApp.exec_())
