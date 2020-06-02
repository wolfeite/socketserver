from libs.Thread import Loop

counts = 0
def web_all_send(gui, web):
    def getPlanVals():
        msg = gui.context_all.text()
        interval = gui.interval_all.text()
        isLoop = gui.loop_all.isChecked()

        return {"interval": interval, "isLoop": isLoop, "msg": msg}

    def send(client, address, msg):
        global counts
        print(client, address, msg)
        web.send(address, msg)
        client["send_counts"] += 1
        counts += 1

    def clear():
        global counts
        for key, val in web.clients.items():
            web.clients[key]["send_counts"] = 0
        counts = 0

    def stop():
        loop.stop()
        gui.send_all.setEnabled(True)
        gui.stop_all.setEnabled(False)

    def btn_send_all():
        vals = getPlanVals()
        msg, interval, isLoop = vals["msg"], int(vals["interval"]), vals["isLoop"]
        if msg:
            gui.send_all.setEnabled(False)
            gui.stop_all.setEnabled(True)
            for address, client in web.clients.items():
                if isLoop:
                    loop.connect(send, [client, address, msg]).start(interval)
                else:
                    send(client, address, msg)
                    gui.send_all.setEnabled(True)
                    gui.stop_all.setEnabled(False)

    def counts_send():
        # print("send_all线程是", threading.current_thread().ident)
        gui.counts_all.setText(str(counts))

    gui.timer.timeout.connect(counts_send)
    # tt.start(300)

    loop = Loop()
    gui.send_all.setEnabled(True)
    gui.stop_all.setEnabled(False)
    gui.send_all.clicked.connect(btn_send_all)
    gui.stop_all.clicked.connect(stop)
    gui.clear_all.clicked.connect(clear)
