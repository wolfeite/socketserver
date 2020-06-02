from libs.socket import webSocketClient as wscApp
import time
import _thread as thread

def on_open(link, app):
    print(link, app)
    def run(*args):
        for i in range(2000):
            time.sleep(0.001)
            # ws.send("Hello %d" % i)
            msg = "你好hello{0}".format(i)
            # msg=str(msg, encoding="utf-8")
            # encode("utf-8")
            # msg=msg.encode(encoding='utf8')
            # msg=bytes(msg, encoding='utf-8')
            app.send(msg)
        time.sleep(1)
        # ws.close()
        print("thread terminating...")
    thread.start_new_thread(run, ())

def on_message(link, app, msg):
    print("收到服务器消息!:", msg)
    # print("客户端开始睡眠20秒")

clientApp = wscApp(("127.0.0.1", 7000), on_open=on_open, on_message=on_message)

# import websocket
# try:
#     import thread
# except ImportError:
#     print("ImportError异常：", ImportError)
#     import _thread as thread
# import time
#
# def on_message(ws, message):
#     print("收到服务器消息：", message)
#
# def on_error(ws, error):
#     print(error)
#
# def on_close(ws):
#     print("### closed ###")
#
# def on_open(ws):
#     def run(*args):
#         for i in range(1):
#             time.sleep(1)
#             ws.send("Hello %d" % i)
#         time.sleep(1)
#         # ws.close()
#         print("thread terminating...")
#     thread.start_new_thread(run, ())
#
# if __name__ == "__main__":
#     websocket.enableTrace(True)
#     ws = websocket.WebSocketApp("ws://127.0.0.1:6869",
#                                 on_message=on_message,
#                                 on_error=on_error,
#                                 on_close=on_close, on_open=on_open)
#     # ws.on_open = on_open
#     ws.run_forever()
