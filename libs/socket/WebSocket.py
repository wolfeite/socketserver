import logging
from websocket_server import WebsocketServer
import websocket
import threading
import time

class WebSocketServer():
    def __init__(self, ip, port, **conf):
        # 创建Websocket Server
        self.server = WebsocketServer(port, host=ip)
        print("属性项：", dir(self.server))
        # 有设备连接上了
        self.server.set_fn_new_client(self.on_open)
        # 断开连接
        self.server.set_fn_client_left(self.on_close)
        # 接收到信息
        self.server.set_fn_message_received(self.on_message)
        self.clients = self.server.clients

    def on_open(self, client, server):
        print(client['id'], client, "共有：", server == self.server, self.clients)
        print("New client connected and was given id %d" % client['id'])
        # 发送给所有的连接
        # print("现所链接的客户端为",dict(server.client))
        print(client["address"], "当前所运行线程名：", threading.currentThread().name, "线程ID", threading.currentThread().ident)
        # server.send_message_to_all("Hey all, a new client has joined us")
        # server.send_message(client,">>>>建立才成功从！！！")
        client["handler"].send_message(">>>>建立才成功从！！！{0}{1}".format(*client["address"]))
        pass

    def on_message(self, client, server, message):
        if len(message) > 200:
            message = message[:200] + '..'
        print("Client(%d) said: %s" % (client['id'], message))

        # 发送给所有的连接
        server.send_message_to_all(message)

    def on_close(self, client, server):
        print("Client(%d) disconnected" % client['id'])

    def send(self):
        self.server.send_message()

    def sendAll(self, msg):
        self.server.send_message_to_all(msg)

    def restart(self):
        pass

    def stop(self):
        pass

    def run(self):
        # 开始监听
        self.server.run_forever()

class WebSocketClient():
    def __init__(self, ip, port, *conf):
        def on_open(ws):
            ws.wrap.on_open(ws)

        def on_message(ws, msg):
            ws.wrap.on_message(ws, msg)

        def on_error(ws, error):
            print("WS发送错误")
            ws.wrap.on_error(ws, error)

        def on_close(ws):
            ws.wrap.on_close(ws)

        websocket.enableTrace(True)
        url = "ws://{0}:{1}".format(ip, port)
        self.client = websocket.WebSocketApp(url, on_message=on_message, on_error=on_error,
                                             on_close=on_close, on_open=on_open)
        self.client.wrap = self

    def on_open(self, ws):
        def run(*args):
            for i in range(1):
                time.sleep(1)
                ws.send("Hello %d" % i)
            time.sleep(1)
            # ws.close()
            print("thread terminating...")
        threading.Thread(target=run).start()

    def on_message(self, ws, msg):
        print("收到服务器消息：", msg)

    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws):
        print("### closed ###", ws is self.client)

    def send(self, msg):
        self.client.send(msg)

    def restart(self):
        pass

    def stop(self):
        self.client.close()

    def run(self):
        # 开始监听
        self.client.run_forever()



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
