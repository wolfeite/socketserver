def config_web(gui, web):
    def on_open(c, s):
        print("web服务链接成功了，哈哈！")
        c["recv_counts"] = 0
        c["send_counts"] = 0
        gui.insertText("links", "{0}:{1}【状态：链接】\n".format(*c["address"]))

    def on_message(link, app, message):
        msg = "{0}:{1}：{2}\n".format(*link["address"], message)
        # gui.insertText("receive", msg)
        # gui.insertPlainText("receive", msg)
        link["recv_counts"] += 1
        # msg = msg.decode("utf-8")
        # msg = msg if isinstance(msg, str) else msg.decode(encoding="utf-8")
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
    web.setCon(on_open=on_open, on_message=on_message, on_error=on_error, on_close=on_close)
