# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.5.18
# Version:1.0

import socketserver
import threading
import socket
import time

ADDRESS = ('localhost', 6868)  # 绑定地址

g_conn_pool = []  # 连接池

class TcpHandler(socketserver.BaseRequestHandler):
    ip = None
    hart_time = 0

    def setup(self):
        print("?>>>>>socket>>>setup")
        # self.request.sendall("连接服务器成功!".encode(encoding='utf8'))
        self.request.send("连接服务器成功!".encode(encoding='utf8'))
        print('addr is', self.client_address[0], ":", self.client_address[1], 'conn is', self.request)  # conn
        self.ip, self.port = self.client_address[0], self.client_address[1]
        print(">>>socket>>>setup>>>>>>", "当前所运行线程名：", threading.currentThread().name, "线程ID",
              threading.currentThread().ident)
        self.on_open()

    def handle(self):
        print(">>>socket>>>start>>>>>>", "当前所运行线程名：", threading.currentThread().name, "线程ID",
              threading.currentThread().ident)
        self.on_start()
        while True:
            try:
                # 收消息
                # 当它不断地收的时候用下面这一行代码判断

                msg = self.request.recv(1024)
                if not msg: break
                print('客户端消息', msg.strip(), self.client_address)
                # print("客户端消息：", bytes.decode(encoding="utf8"))
                # 发消息
                res = self.on_message(msg)
                self.send(res)
            except Exception as e:
                print("异常导致客户端链接断开!：", e)
                self.on_error(e)
                # self.remove(self.ip, self.port)
                break

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

    def on_open(self):
        # 钩子函数：获取ip,port,tcp
        self.register()
        event = self.server.event
        "on_open" in event and event["on_open"](self)

    def on_start(self):
        # 钩子函数：获取客户端配置信息
        event = self.server.event
        "on_start" in event and event["on_start"](self)

    def on_message(self, msg):
        # 钩子函数：处理通讯信息
        return self.server.event["on_message"](self, msg.decode(encoding="utf-8"))

    def on_close(self):
        # 钩子函数：处理客户端断开情况
        event = self.server.event
        "on_close" in event and event["on_close"](self)

    def on_error(self, error):
        event = self.server.event
        "on_error" in event and event["on_error"](self, error)

    def unregister(self, ip, port):
        self.server.wrap.unregister(ip, port, self)
        print("客户端", ip, ":", port, "断开。")
        # g_conn_pool.remove(self.request)

    def register(self):
        self.server.wrap.register(self, self.ip, self.port)

    def clear(self):
        self.server.wrap.clear()

    def finish(self):
        self.unregister(self.ip, self.port)
        self.on_close()
        # self.clear()

from concurrent.futures import ThreadPoolExecutor
class ThreadingPoolTCPServer(socketserver.ThreadingTCPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True, thread_n=100):
        super(ThreadingPoolTCPServer, self).__init__(server_address, RequestHandlerClass, bind_and_activate=True)

        self.executor = ThreadPoolExecutor(thread_n)

    def process_request(self, request, client_address):
        self.executor.submit(self.process_request_thread, request, client_address)

class TcpServer():
    def __init__(self, address, handle, number=None, **event):
        number = number if isinstance(number, int) else None
        print(">>>number:", number)
        self.tcpServer = ThreadingPoolTCPServer(address, handle,
                                                thread_n=number) if number else socketserver.ThreadingTCPServer(address,
                                                                                                                TcpHandler)
        self.links = {}
        self.tcpServer.wrap = self
        self.tcpServer.event = {"on_message": lambda s, msg: msg}

        for k, handle in event.items():
            self.tcpServer.event[k] = handle

    def register(self, tcp, ip, port):
        address = "{0}:{1}".format(ip, port)
        self.links[address] = tcp

    def unregister(self, ip, port, tcp):
        address = "{0}:{1}".format(ip, port)
        clients = self.links
        address in clients and self.links.pop(address)
        print("移除", address, "剩余", dict(self.clients))

    def clear(self):
        self.links.clear()

    @property
    def clients(self):
        return self.links

    def send(self, address, emit):
        print(">>>>>>", address, )
        self.links[address].request.send(emit.encode(encoding="utf8")) if address in self.links else print(
            "发送失败：没有该",
            address, "客户端")

    def sendAll(self):
        pass

    def restart(self):
        print("重启方法")
        pass

    def stop(self):
        print("停止方法")
        pass

    def run(self, *args):
        # cb = kwargs["cb"] if "cb" in kwargs else lambda d, s: d
        # self.setCb(args[0])
        # 同步完配置
        time.sleep(0.01)
        self.tcpServer.serve_forever()

    # test = property(restart, stop)

class TcpClient():
    def __init__(self, address, **conf):
        # socket.setdefaulttimeout(0.01)
        "timeout" in conf and socket.setdefaulttimeout(conf["timeout"])
        self.client = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        self.address = address
        self.bufsize = 1024

    def on_open(self):
        def run(*args):
            for i in range(1):
                time.sleep(1)
                self.send("tcpTest %d" % i)
            time.sleep(1)
            # ws.close()
            print("thread terminating...")
        threading.Thread(target=run).start()

    def on_message(self, msg):
        print('收到服务端发来的消息：%s' % msg.decode('utf-8'))
        return msg

    def on_error(self, error):
        print("客户端抛出异常", error)

    def on_close(self):
        print("客户端通讯关闭")

    def stop(self):
        self.client.close()
        self.on_close()

    def input(self):
        msg = input('请你输入命令>>：').strip()

    def send(self, msg):
        self.client.send(msg.encode('utf-8'))

    def run(self):
        # 同步完配置
        time.sleep(0.01)
        try:
            self.client.connect(self.address)
            self.on_open()
            c = self.client
            bufsize = self.bufsize

            while True:
                # 发收消息
                msg = c.recv(bufsize)
                if not msg: break
                # print("客户端消息：", bytes.decode(encoding="utf8"))
                res = self.on_message(msg)
                # 发消息
                # self.send(res)

        except Exception as e:
            self.on_error(e)

        self.stop()
