from libs.Thread import Loop

counts = 0
def web_single_send(gui, web):
    # gui.interval_single.setText("5")
    # gui.counts_single.setText("1111")
    def getPlanVals():
        ip = gui.ip.text()
        port = gui.port.text()
        interval = gui.interval_single.text()
        isLoop = gui.loop_single.isChecked()
        msg = gui.context_single.text()
        return {"ip": ip, "port": port, "interval": interval, "isLoop": isLoop, "msg": msg}

    def send(client, address, msg):
        global counts
        web.send(address, msg)
        client["send_counts"] += 1
        counts = client["send_counts"]

    def clear():
        global counts
        vals = getPlanVals()
        ip, port = vals["ip"], vals["port"]
        if ip and port:
            address = "{0}:{1}".format(ip, port)
            client = web.clients[address]
            client["send_counts"] = 0
        counts = 0

    def stop():
        loop.stop()
        gui.send_single.setEnabled(True)
        gui.stop_single.setEnabled(False)

    def btn_send_single():
        # gui.counts_single.setText("1121")
        vals = getPlanVals()
        ip, port, interval, isLoop, msg = vals["ip"], vals["port"], int(vals["interval"]), vals["isLoop"], vals["msg"]
        print("interval>>", interval)
        address = "{0}:{1}".format(ip, port)
        if ip and port and msg and address in web.clients:
            gui.send_single.setEnabled(False)
            gui.stop_single.setEnabled(True)
            client = web.clients[address]
            if isLoop:
                loop.connect(send, [client, address, msg]).start(interval)
            else:
                send(client, address, msg)
                gui.send_single.setEnabled(True)
                gui.stop_single.setEnabled(False)

    def counts_send():
        # print("send_single线程是", threading.current_thread().ident)
        gui.counts_single.setText(str(counts))

    gui.timer.timeout.connect(counts_send)
    # tt.start(5000)

    loop = Loop()
    gui.send_single.setEnabled(True)
    gui.stop_single.setEnabled(False)
    gui.send_single.clicked.connect(btn_send_single)
    gui.stop_single.clicked.connect(stop)
    gui.clear_single.clicked.connect(clear)
