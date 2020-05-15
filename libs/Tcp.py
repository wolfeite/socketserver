import socketserver
import threading

ADDRESS = ('localhost', 6868)  # 绑定地址

g_conn_pool = []  # 连接池

class TcpHandler(socketserver.BaseRequestHandler):
    ip = None
    hart_time = 0

    def setup(self):
        # self.request.sendall("连接服务器成功!".encode(encoding='utf8'))
        # self.request.send("连接服务器成功!".encode(encoding='utf8'))
        # 加入连接池
        g_conn_pool.append(self.request)

    def handle(self):
        print('addr is', self.client_address[0], ":", self.client_address[1], 'conn is', self.request)  # conn
        self.ip, self.port = self.client_address[0], self.client_address[1]
        self.server.wrap.setTcpPool(self.ip, self.port, self)

        while True:
            try:
                # 收消息
                # 当它不断地收的时候用下面这一行代码判断

                data = self.request.recv(1024)
                if not data:
                    print("链接断开!")
                    self.remove()
                    break
                print('客户端消息', data.strip(), self.client_address)
                # print("客户端消息：", bytes.decode(encoding="utf8"))
                # 发消息
                res = self.ing(data)
                self.send(res)
            except Exception as e:
                print("链接断开!报错：", e)
                self.remove()
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

    def ing(self, data):
        print("cb回调处理")
        return self.server.event["ing"](data, self)

    def finish(self):
        print(">>>>>>>>>>>结束socketserver监听,清除了这个客户端。")

    def remove(self):
        print("有一个客户端掉线了。")
        g_conn_pool.remove(self.request)

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
        self.tcpServer = ThreadingPoolTCPServer(address, handle,
                                                thread_n=number) if number else socketserver.ThreadingTCPServer(ADDRESS,
                                                                                                                TcpHandler)
        self.pool = {}
        self.tcpServer.wrap = self
        self.tcpServer.event = {"ing": lambda d, s: d}

        for k, handle in event.items():
            self.tcpServer.event[k] = handle

    def setTcpPool(self, ip, port, tcp):
        address = ip + str(port)
        self.pool[address] = tcp

    def getTcpPool(self):
        return self.pool

    def send(self, address, emit):
        print(">>>>>>", address, )
        self.pool[address].request.send(emit.encode(encoding="utf8")) if address in self.pool else print("发送失败：没有该",
                                                                                                         address, "客户端")

    def run(self, *args):
        # cb = kwargs["cb"] if "cb" in kwargs else lambda d, s: d
        # self.setCb(args[0])
        self.tcpServer.serve_forever()

def createWebSocket(number=None, **event):
    tcp = TcpServer(ADDRESS, TcpHandler, number, **event)
    thread = threading.Thread(target=tcp.run)
    thread.setDaemon(True)
    tcp.thread = thread
    thread.start()
    return tcp
