# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.5.18
# Version:1.0

import logging
from .websocket_server import WebsocketServer
from ..Thread import Loop, Timeout, Interval, Duration
import websocket
import threading
from inspect import isfunction
import time
from .ApiSocket import ApiSocket

class WebSocketServer(ApiSocket):
    def __init__(self, ip, port, **conf):
        super(WebSocketServer, self).__init__((ip, port), type="server", **conf)
        # 创建Websocket Server
        self.app = WebsocketServer(port, host=ip)

        # 有设备连接上了
        self.app.set_fn_new_client(self.on_open)
        # 断开连接
        self.app.set_fn_client_left(self.on_close)
        # 接收到信息
        self.app.set_fn_message_received(self.on_message)
        # 异常处理
        self.app.set_fn_error(self.on_error)
        # self.clients = self.app.clients

    @property
    def clients(self):
        return self.links

    def emit(self, link, msg):
        # self.app.send_message(link, msg)
        link["handler"].send_message(msg)

    # def send(self, address, msg, cb=None):
    #     try:
    #         client = address
    #         if isinstance(address, str):
    #             if address in self.clients:
    #                 client = self.clients[address]
    #             else:
    #                 print("没有该链接的客户端！")
    #                 return False
    #         self.app.send_message(client, msg)
    #         isfunction(cb) and cb(client, msg)
    #     except Exception as e:
    #         # 客户端未挥手断网
    #         client["alive"] = False
    #         print(e)

    def sendAll(self, msg, cb=None):
        c = self.clients
        for address, client in c.items():
            self.send(address, msg, cb)

    def sendToAll(self, msg):
        try:
            self.app.send_message_to_all(msg)
        except Exception as e:
            print("某客户端链接异常：", e)

    # def close(self):
    #     self.app.server_close()

    def run_forever(self):
        self.app.run_forever()

class WebSocketClient(ApiSocket):
    def __init__(self, ip, port, **conf):
        super(WebSocketClient, self).__init__((ip, port), type="client", **conf)
        print(">>>>id", self.id)
        def on_open(app):
            # print(">>>>客户端：", dir(app))
            link = {"id": 1, "address": (app.wrap.address[0], app.wrap.address[1]), "handler": app}
            app.wrap.on_open(link, app)

        def on_message(app, msg):
            app.wrap.on_message(app.wrap.links[app.wrap.id], app, msg)

        def on_error(app, error):
            print("客户端链接异常：", error, type(error), str(type(error)))
            link = app.wrap.links.get(app.wrap.id)
            app.wrap.on_error(link, app, error)
            # if str(type(error)) == "<class 'ConnectionRefusedError'>":
            #     app.wrap.stop_app()

        def on_close(app):
            print(">>>>触发onclose事件：即将关闭应用轮询服务》》》")
            link = app.wrap.links.get(app.wrap.id)
            app.wrap.on_close(link, app)
            # app.wrap.stop_app()

        websocket.enableTrace(True)
        url = "ws://{0}:{1}".format(ip, port)
        self.app = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error,
                                          on_close=on_close, on_open=on_open)
        self.app.wrap = self

    def emit(self, link, msg):
        print("发送：", msg)
        self.app.send(msg)

    # def send(self, link, msg, cb=None):
    #     print("发送：", msg)
    #     self.app.send(msg)

    # def close(self):
    #     self.app.close()

    def run_forever(self):
        self.app.run_forever()

# # Called for every client connecting (after handshake)
# def new_client(client, server):
#     print(client['id'], client, "共有：", server.clients)
#     print("New client connected and was given id %d" % client['id'])
#     # 发送给所有的连接
#     # print("现所链接的客户端为",dict(server.client))
#     print(client["address"], "当前所运行线程名：", threading.currentThread().name, "线程ID", threading.currentThread().ident)
#     server.send_message_to_all("Hey all, a new client has joined us")
#
# # Called for every client disconnecting
# def client_left(client, server):
#     print("Client(%d) disconnected" % client['id'])
#
# # Called when a client sends a message
# def message_received(client, server, message):
#     if len(message) > 200:
#         message = message[:200] + '..'
#     print("Client(%d) said: %s" % (client['id'], message))
#
#     # 发送给所有的连接
#     server.send_message_to_all(message)
#
# # 创建Websocket Server
# server = WebsocketServer(6869, host='0.0.0.0')
# # 有设备连接上了
# server.set_fn_new_client(new_client)
# # 断开连接
# server.set_fn_client_left(client_left)
# # 接收到信息
# server.set_fn_message_received(message_received)
# # 开始监听
# server.run_forever()
