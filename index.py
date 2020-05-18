import sys
from PyQt5.QtWidgets import QApplication
from gui import Gui
from libs.socket import tcpSocketServerApp as tssApp, webSocketServerApp as wssApp

if __name__ == "__main__":
    gui = Gui()
    QApp = QApplication(sys.argv)
    gui.init()
    def ing(s, d):
        return gui.index_text(d)
    tsApp = tssApp(("0.0.0.0", 6868), on_message=ing)
    wsApp = wssApp(("0.0.0.0", 6869))
    def end():
        for k, v in tsApp.clients.items():
            tsApp.send(k, "服务器关闭链接！！！")
    gui.setExit(end)
    # QApp.exec_()
    sys.exit(QApp.exec_())
