import threading
from .TcpSocket import TcpServer, TcpHandler, TcpClient
from .WebSocket import WebSocketServer, WebSocketClient

from ..Thread import Thread, threadFactory

def tcpSocketServerApp(address, number=None, **event):
    tsApp = TcpServer(address, TcpHandler, number, **event)
    thread = threadFactory(tsApp.run)
    tsApp.thread = thread
    return tsApp

def webSocketServerApp(address, **conf):
    wsApp = WebSocketServer(*address, **conf)
    thread = Thread(wsApp.run)
    # thread = threadFactory(wsApp.run)
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
