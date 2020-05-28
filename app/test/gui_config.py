def config_gui(gui, tcp, web):
    def end():
        for k, v in web.clients.items():
            web.send(k, "服务器关闭链接！！！")

        for k, v in tcp.clients.items():
            tcp.send(k, "服务器关闭链接！！！")

    gui.setExit(end)
