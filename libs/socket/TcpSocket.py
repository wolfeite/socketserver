# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.5.18
# Version:1.0

import socketserver
import threading
from inspect import isfunction
import socket
import time
from .ApiSocket import ApiSocket

ADDRESS = ('localhost', 6868)  # 绑定地址

g_conn_pool = []  # 连接池

class TcpHandler(socketserver.BaseRequestHandler):
    ip = None
    hart_time = 0

    def setup(self):
        # self.request.sendall("连接服务器成功!".encode(encoding='utf8'))
        self.request.send("连接服务器成功!".encode(encoding='utf8'))
        self.ip, self.port = self.client_address[0], self.client_address[1]
        print('setup阶段》》客户端{0}:{1}链接到本服务器'.format(self.ip, self.port))
        currentT = threading.currentThread()
        self.link = {"ident": currentT.ident, "address": (self.ip, self.port), "handler": self}
        print("setup>>>>>>", "当前所运行线程名：", currentT.name, "线程ID", currentT.ident)
        self.on_start()

    def handle(self):
        print(">>>socket>>>start>>>>>>", "当前所运行线程名：", threading.currentThread().name, "线程ID",
              threading.currentThread().ident)
        self.on_open()
        try:
            while True:
                # 收消息
                msg = self.request.recv(1024)
                if not msg: break
                # print("客户端消息：", msg.strip(), msg.decode(encoding="utf8"))
                self.on_message(msg)
                # self.send(res)
        except Exception as e:
            print("异常导致客户端链接断开!：", e)
            self.on_error(e)
            # self.remove(self.ip, self.port)
            # break

    def recv(self):
        pass

    def send(self, emit):
        try:
            # print("send: 发送字节型：" + str(emit) + " ({0})".format(_py))
            # print("send: 发送字符串型：" + str(emit) + " ({0})".format(_py))
            b = emit if isinstance(emit, bytes) else bytes(str(emit if emit else "None"), encoding='utf-8')
            self.request.send(b)
        except Exception as err:
            print("【err】send :" + str(err) + " ({0}:{1})".format(self.ip, self.port))

    @property
    def wrap(self):
        return self.server.wrap

    def on_start(self):
        self.wrap.hook("on_start", self.link, self.server)

    def on_open(self):
        self.wrap.hook("on_open", self.link, self.server)

    def on_message(self, msg):
        self.wrap.hook("on_message", self.link, self.server, msg.decode(encoding="utf-8"))
        # return self.server.event["on_message"](self, msg.decode(encoding="utf-8"))

    def on_error(self, error):
        self.wrap.hook("on_error", self.link, self.server, error)

    def on_close(self):
        self.wrap.hook("on_close", self.link, self.server)

    def finish(self):
        self.on_close()

from concurrent.futures import ThreadPoolExecutor
class ThreadingPoolTCPServer(socketserver.ThreadingTCPServer):
    def __init__(self, address, RequestHandlerClass, bind_and_activate=True, thread_n=100):
        super(ThreadingPoolTCPServer, self).__init__(address, RequestHandlerClass, bind_and_activate=bind_and_activate)
        self.executor = ThreadPoolExecutor(thread_n)

    def process_request(self, request, client_address):
        self.executor.submit(self.process_request_thread, request, client_address)

class TcpServer(ApiSocket):
    def __init__(self, ip, port, **conf):
        address = (ip, port)
        super(TcpServer, self).__init__(address, type="server", **conf)
        number = self.number
        print(">>>运行的线程数number:", number)
        if number:
            self.app = ThreadingPoolTCPServer(address, TcpHandler, thread_n=number)
        else:
            self.app = socketserver.ThreadingTCPServer(address, TcpHandler)

        self.app.wrap = self

    @property
    def clients(self):
        return self.links

    def emit(self, link, msg):
        link["handler"].send(msg)

    def sendAll(self):
        pass

    # def close(self):
    #     self.app.server_close()

    def run_forever(self):
        self.app.serve_forever()

    # test = property(restart, stop)

class TcpClient(ApiSocket):
    def __init__(self, ip, port, **conf):
        # socket.setdefaulttimeout(0.01)
        address = (ip, port)
        super(TcpClient, self).__init__(address, type="client", **conf)
        "timeout" in conf and socket.setdefaulttimeout(conf["timeout"])
        self.bufsize = self.conf.get("bufsize") if self.conf.get("bufsize") else 1024
        self.createSocket()

    # def on_open(self):
    #     def run(*args):
    #         for i in range(1):
    #             time.sleep(1)
    #             self.send("tcpTest %d" % i)
    #         time.sleep(1)
    #         # ws.close()
    #         print("thread terminating...")
    #     threading.Thread(target=run).start()

    # def on_message(self, msg):
    #     print('收到服务端发来的消息：%s' % msg.decode('utf-8'))
    #     return msg

    # def on_error(self, error):
    #     print("客户端抛出异常", error)

    # def on_close(self):
    #     print("客户端通讯关闭")

    # def stop(self):
    #     self.app.close()

    def createSocket(self):
        self.app = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        return self.app

    def input(self):
        msg = input('请你输入命令>>：').strip()

    def emit(self, link, msg):
        msg = msg if isinstance(msg, bytes) else bytes(str(msg if msg else "None"), encoding='utf-8')
        self.app.send(msg)

    def run_forever(self):
        try:
            c = self.createSocket() if self.app._closed else self.app
            link = {"id": 1, "address": (self.address[0], self.address[1]), "handler": c}
            c.connect(self.address)
            self.on_open(link, c)
            bufsize = self.bufsize
            while True:
                # 发收消息
                msg = c.recv(bufsize)
                if not msg: break
                # print("客户端消息：", bytes.decode(encoding="utf8"))
                res = self.on_message(link, c, msg.decode(encoding="utf-8"))
                # 发消息
                # self.send(res)
        except Exception as e:
            self.on_error(link, c, e)
        self.on_close(link, c)
