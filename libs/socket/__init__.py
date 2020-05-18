import threading
from .TcpSocket import TcpServer, TcpHandler, TcpClient
from .WebSocket import WebSocketServer, WebSocketClient

def tcpSocketServerApp(address, number=None, **event):
    tsApp = TcpServer(address, TcpHandler, number, **event)
    thread = threading.Thread(target=tsApp.run)
    thread.setDaemon(True)
    tsApp.thread = thread
    thread.start()
    return tsApp

def webSocketServerApp(address, **conf):
    wsApp = WebSocketServer(*address, **conf)
    thread = threading.Thread(target=wsApp.run)
    thread.setDaemon(True)
    wsApp.thread = thread
    thread.start()
    return wsApp

def webSocketClientApp(address, **conf):
    ws_clientApp = WebSocketClient(*address, **conf)
    ws_clientApp.run()
    return ws_clientApp

def tcpSocketClientApp(address, **conf):
    ts_clientApp = TcpClient(address, **conf)
    ts_clientApp.run()
    return ts_clientApp
