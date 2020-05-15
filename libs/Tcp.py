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

    def handled(self):
        # 获取ip
        self.ip = str(self.client_address[0]) + ":" + str(self.client_address[1])
        print("handle: 客户端连接" + self.ip + " ({0})".format(_py))

        while True:
            try:
                bytes = self.request.recv(1024)
                print("客户端消息：", bytes.decode(encoding="utf8"))
            except:  # 意外掉线
                self.remove()
                break

    def handle(self):
        print('conn is', self.request)  # conn
        print('addr is', self.client_address)  # addr

        while True:
            try:
                # 收消息
                # 当它不断地收的时候用下面这一行代码判断

                data = self.request.recv(1024)
                if not data: break
                print('收到的消息是', data.strip(), self.client_address)
                # 发消息
                res = self.cb(data)
                self.request.send(res)
            except Exception as e:
                print("报错：", e)
                self.remove()
                break

    def cb(self, data):
        print("cb回调处理")
        return self.server.cb(data, self)

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

def listenerWebSocket(cb=lambda d, s: d, number=None):
    print(">>>>>>>>>>>开启服务监听")
    number = number if isinstance(number ,int) else None
    IOServer = ThreadingPoolTCPServer(ADDRESS, TcpHandler, thread_n=number) if number else socketserver.ThreadingTCPServer(ADDRESS, TcpHandler)
    IOServer.cb = cb
    IOServer.serve_forever()

def createWebSocket(cb=lambda d, s: d, number=None):
    thread = threading.Thread(target=listenerWebSocket, args=[cb, number])
    thread.setDaemon(True)
    thread.start()

    return thread
