import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from gui import Gui
from libs.Tcp import createWebSocket as cw

if __name__ == "__main__":
    gui = Gui()
    QApp = QApplication(sys.argv)
    gui.init()
    def ing(d, s):
        return gui.index_text(d)
    cwApp = cw(number=3, ing=ing)
    def end():
        for k, v in cwApp.pool.items():
            cwApp.send(k, "服务器关闭链接！！！")
    gui.setExit(end)
    # QApp.exec_()
    sys.exit(QApp.exec_())
