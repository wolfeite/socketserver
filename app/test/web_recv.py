def web_config_recv(gui, web):
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

    def endChecked():
        gui.detect.setEnabled(True)
        gui.detect.setText("检测")
        for key, val in web.clients.items():
            gui.insertText("links", "{0}【状态：链接】\n".format(key))

    def checking(s):
        gui.detect.setText("等待{0}秒".format(s))

    def detected():
        gui.links.clear()
        gui.detect.setEnabled(False)
        gui.detect.setText("检测中...")
        web.check_alive(end=endChecked, duration=5000, waiting=checking, interval=2000)
        # gui.links.clear()

    gui.timer.timeout.connect(aggregated)
    # 信息清理
    gui.clear_recv.clicked.connect(clearRecv)
    # 统计清理
    gui.clear_counts_recv.clicked.connect(clearCounts)
    # 统计
    gui.aggregate.clicked.connect(aggregated)
    # 检测
    gui.detect.clicked.connect(detected)
