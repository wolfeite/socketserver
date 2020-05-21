# def ing(s, d):
#     # return gui.index_text(d.decode(encoding="utf-8"))
#     print("现在有clients>>", tsApp.clients)
#     return gui.insertText("links", d)

from .test.web_send_single import web_single_send
from .test.web_send_all import web_all_send
from PyQt5.QtCore import QTimer
import threading

def createTestApp(gui, tcp, web):
    def on_open(c, s):
        print("web服务链接成功了，哈哈！")
        c["recv_counts"] = 0
        c["send_counts"] = 0
        gui.insertText("links", "{0}:{1}【状态：链接】\n".format(*c["address"]))

    def on_message(client, server, message):
        msg = "{0}:{1}：{2}\n".format(*client["address"], message)
        # gui.insertText("receive", msg)
        # gui.insertPlainText("receive", msg)
        client["recv_counts"] += 1
        gui.receive.insertPlainText(msg)
        # gui.receive.setText(msg)
        # setPlainText,setText,insertPlainText

    def on_error(client, server, e):
        print("客户端异常》》", e)
        # gui.insertText("links")
        # gui.setPlainText("")

    def on_close(client, server):
        print("关闭一个客户端")
        # gui.clearText("links")
        # gui.links.clear()

    def aggregated():
        # print("开始统计", dir(gui.receive))
        # print(">>>>,执行统计》》》》")
        # print("aggregated线程是", threading.current_thread().ident, "主线程：", tid)
        gui.counts_recv.clear()
        for key, val in web.clients.items():
            counts = web.clients[key]["recv_counts"]
            gui.insertText("counts_recv", "{0}共：{1}条\n".format(key, counts))
        # mes = gui.receive.toPlainText()
        # mes1 = gui.receive.toHtml()
        # print(mes)
        # print(mes1)

    def clearCounts():
        gui.counts_recv.clear()
        print(">>>>开始清理")
        for key, val in web.clients.items():
            web.clients[key]["recv_counts"] = 0
            print(">>>>", web.clients[key]["recv_counts"])
            gui.insertText("counts_recv", "{0}共：{1}条\n".format(key, 0))

    def clearRecv():
        gui.receive.clear()

    def detected():
        gui.links.clear()
        for key, val in web.clients.items():
            gui.insertText("links", "{0}【状态：链接】\n".format(key))

    gui.timer.timeout.connect(aggregated)
    gui.timer.start(200)

    # 信息清理
    gui.clear_recv.clicked.connect(clearRecv)
    # 统计清理
    gui.clear_counts_recv.clicked.connect(clearCounts)
    # 统计
    gui.aggregate.clicked.connect(aggregated)
    # 检测
    gui.detect.clicked.connect(detected)
    web.setCon(on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)

    def end():
        for k, v in web.clients.items():
            web.send(k, "服务器关闭链接！！！")

    gui.setExit(end)

    web_single_send(gui, web)
    web_all_send(gui, web)
