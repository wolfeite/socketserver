import sys
import os

from PyQt5.QtWidgets import QMainWindow, QApplication, QSystemTrayIcon, QAction, QMenu, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore

from .UI.Ui_UI import Ui_UI
from libs.IO import Path

class Gui(Ui_UI):
    def __init__(self):
        super(Gui, self).__init__()
        # self.init()
    def init(self):
        QApplication.setQuitOnLastWindowClosed(False)
        self.mainWin = QMainWindow()
        self.mainWin.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setupUi(self.mainWin)
        # print("开始gui创建111")
        # self.mainWin.show()
        self.set_icon()
        self.set_menus()
        self.set_icon_menus()

    def set_icon(self):
        self.icon = QSystemTrayIcon(self.mainWin)
        try:
            # icon_dir = Path("gui")
            # url = "{0}{2}{1}{3}{1}{4}{1}{5}".format(icon_dir.path["base"], icon_dir.path["sep"], "UI", "Data", "Assets", "icon.png")
            icon_dir = Path("Data")
            url = "{0}{2}{1}{3}{1}{4}".format(icon_dir.path["base"], icon_dir.path["sep"], "statics", "images",
                                              "icon.png")
            print(">>>>url", url)
            self.icon.setIcon(QIcon(url))
        except Exception as err:
            print("【err】【Gui ->set_icon】 icon图片文件错误")

    def set_menus(self):
        self.menu = {}
        self.menu["show"] = QAction('&显示(Show)', triggered=self.mainWin.show)
        self.menu["hide"] = QAction('&隐藏(Hide)', triggered=self.mainWin.hide)
        self.menu["exit"] = QAction('&退出(Exit)', triggered=self.exit)

        self.menus = QMenu()
        for act in self.menu:
            self.menus.addAction(self.menu[act])

    def set_icon_menus(self):
        self.icon.setContextMenu(self.menus)
        self.icon.activated.connect(self.click_btn)
        self.icon.show()
        print(">>>>show icon")

    def click_btn(self, reason):
        if reason == 2 or reason == 3:
            self.mainWin.show()

    def exit(self):
        re = QMessageBox.question(self.mainWin, "退出", "是否退出", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if re == QMessageBox.Yes:
            self.mainWin.hide()
            self.icon.hide()
            print("退出成功")
            sys.exit(0)

    def restart(self):
        # if self.main_exit:
        #     self.main_exit()
        python = sys.executable
        os.execl(python, python, *sys.argv)

