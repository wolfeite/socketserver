import logging
from websocket_server import WebsocketServer
import threading

# Called for every client connecting (after handshake)
def new_client(client, server):
    print(client['id'], client, "共有：", server.clients)
    print("New client connected and was given id %d" % client['id'])
    # 发送给所有的连接
    # print("现所链接的客户端为",dict(server.client))
    print(client["address"], "当前所运行线程名：", threading.currentThread().name, "线程ID", threading.currentThread().ident)
    server.send_message_to_all("Hey all, a new client has joined us")

# Called for every client disconnecting
def client_left(client, server):
    print("Client(%d) disconnected" % client['id'])

# Called when a client sends a message
def message_received(client, server, message):
    if len(message) > 200:
        message = message[:200] + '..'
    print("Client(%d) said: %s" % (client['id'], message))

    # 发送给所有的连接
    server.send_message_to_all(message)

# 创建Websocket Server
server = WebsocketServer(6868, host='0.0.0.0')
# 有设备连接上了
server.set_fn_new_client(new_client)
# 断开连接
server.set_fn_client_left(client_left)
# 接收到信息
server.set_fn_message_received(message_received)
# 开始监听
server.run_forever()
