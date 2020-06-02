import threading
from .TcpSocket import TcpServer, TcpClient
from .WebSocket import WebSocketServer, WebSocketClient

from ..Thread import Thread, threadFactory

def tcpSocketServerApp(address, **conf):
    tsApp = TcpServer(*address, **conf)
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
    thread = threadFactory(ws_clientApp.run)
    ws_clientApp.thread = thread
    return ws_clientApp

def tcpSocketClientApp(address, **conf):
    ts_clientApp = TcpClient(*address, **conf)
    thread = threadFactory(ts_clientApp.run)
    ts_clientApp.thread = thread
    return ts_clientApp


def webSocketClient(address, **conf):
    ws_clientApp = WebSocketClient(*address, **conf)
    ws_clientApp.run()
    return ws_clientApp

def tcpSocketClient(address, **conf):
    ts_clientApp = TcpClient(*address, **conf)
    ts_clientApp.run()
    return ts_clientApp
