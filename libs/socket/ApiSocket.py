# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.5.28
# Version:1.0：socket包装基类通用接口

'''
edit:
    1-[time：2020.5.30, by：wolfeite, bug：python不支持尾递归优化，断网重连改用while机制]

'''
from ..Thread import Loop, Timeout, Interval, Duration
import threading
from inspect import isfunction
import time
import copy

class ApiSocket():
    def __init__(self, address=(), type="server", **conf):
        # links格式：{"0.0.0.0:80":link}，link格式：{"address":(),"handler":tcp,alive:True,isShutDown:False}
        self.address, self.type, self.links = address, type, {}
        self.init(**conf)
        self.validateConf()
        self.loop = Loop(isClear=False) if self.conf["loop"] == "Loop" else Interval(isClear=False)
        self.duration = Duration()
        self.loop.connect(self._keep_alive_)

    def init(self, **conf):
        type = self.type
        r_s_a = ("t", "s") if type == "server" else ("s", "t")
        auto = False if type == "server" else True
        self._default_ = {"on_message": lambda *m: m, "loop": "Interval", "interval_run": 5, "number": None,
                          "auto_alive": auto, "recv_send_alive": r_s_a, "interval_alive": 20000}
        self.conf = copy.deepcopy(self._default_)
        self.conf.update(conf)
        self.id = "{0}:{1}".format(*self.address)
        self.counts_restart = 0
        self.running = True
        self.paused = False

    def validateConf(self):
        rs_alive = self.conf.get("recv_send_alive")
        rs_alive = rs_alive if isinstance(rs_alive, tuple) else self._default_["recv_send_alive"]
        self.conf["recv_send_alive"] = rs_alive

    def hook(self, name, *args):
        conf = self.conf
        isfunction(conf.get(name)) and conf[name](*args)

    @property
    def counts(self):
        return len(self.links)

    @property
    def number(self):
        number = self.conf["number"]
        return number if isinstance(number, int) else None

    def register(self, link, ip, port):
        address = "{0}:{1}".format(ip, port)
        link["alive"] = True
        link["isShutDown"] = False
        link["id"] = link["id"] if "id" in link else self.counts + 1
        self.links[address] = link

    def unregister(self, ip, port):
        address = "{0}:{1}".format(ip, port)
        links = self.links
        address in links and links.pop(address)
        print("移除", address, "剩余", dict(self.links))

    def clear(self):
        self.links.clear()

    def on_start(self, link, app):
        self.hook("on_start", link, app)

    def on_open(self, link, app):
        self.register(link, *link["address"])
        print(">>on_open", link["address"])
        self.send(link, "《与{0}:{1}链接建立成功！》".format(*link["address"]))
        self.hook("on_open", link, app)
        # isfunction(self.conf.get("on_open")) and self.conf["on_open"](link, app)

    def on_message(self, link, app=None, msg=""):
        recv_alive = self.conf.get("recv_send_alive")[0]
        send_alive = self.conf.get("recv_send_alive")[1]
        if msg == send_alive:
            print("收到{0}响应的心跳包:{1}".format(link["address"], msg))
            link["alive"] = True
            return "recv alive"
        elif msg == recv_alive:
            # time.sleep(10)
            print("准备响应心跳包:{1}到{0}".format(link["address"], msg))
            self.send(link, msg)
            return "send alive"
        elif msg == "quit" and self.type == "client":
            self.quit()

        if len(msg) > 200:
            msg = msg[:200] + '..'
        print("{0}said: {1}".format(link["address"], msg))
        self.conf["on_message"](link, app, msg)
        # self.conf["on_message"](link, server, msg)

    def on_error(self, link, app=None, e=None):
        print("客户端{0}异常导致link断开:{1}{2}".format(link["address"] if link else "None", type(e), e))
        self.hook("on_error", link, app, e)
        # isfunction(self.conf.get("on_error")) and self.conf["on_error"](link, app, e)
        # <class 'ConnectionResetError'> <class 'websocket._exceptions.WebSocketConnectionClosedException'> <class 'ConnectionAbortedError'>

    def on_close(self, link, app=None):
        if link and link.get("address"):
            print("客户端{0}关闭".format(link["address"]))
            address = link["address"]
            self.unregister(*address)
            self.hook("on_close", link, app)
            # isfunction(self.conf.get("on_close")) and self.conf["on_close"](link, app)
            print("link({0}) disconnected".format(address))
            # if self.type == "client":
            #     print("应用已经close，准备stop应用，最后执行on_stop_app钩子函数")
            #     self.stop_app()

    def on_stop_app(self):
        print("进入on_stop_app执行!!!")
        self.loop.stop()
        self.hook("on_stop_app", self)
        # isfunction(self.conf.get("on_stop_app")) and self.conf["on_stop_app"](self)
        # if self.conf.get("keep_run"):
        #     time.sleep(self.conf.get("interval_run"))
        #     self.restart()

    def on_start_app(self):
        self.conf["auto_alive"] and self.loop.start(self.conf.get("interval_alive"))
        self.hook("on_start_app", self)
        # isfunction(self.conf.get("on_start_app")) and self.conf["on_start_app"](self)

    def setCon(self, **con):
        self.conf.update(con)

    def _keep_alive_(self, cb=None):
        # heartbeat
        send_alive = self.conf.get("recv_send_alive")[1]
        print("......准备心跳包......", send_alive)
        c = self.links
        for address, link in c.items():
            alive = link["alive"]
            if alive:
                link["alive"] = False
                # self.server.send_message(client, "s")
                self.send(link, send_alive, cb)
            else:
                # 客户端断网重连，服务器链接超时
                isShutDown = link["isShutDown"]
                if not isShutDown:
                    print("请求链接超时，主动断开：", address, self.type, self.type == "client")
                    link["isShutDown"] = True
                    # self.restart() if self.type == "client" else self.stop_link(link)
                    self.stop_app() if self.type == "client" else self.stop_link(link)

    def check_alive(self, end=None, begin=None, interval=3000, duration=10000, waiting=None):
        self.duration.connect(self._keep_alive_)
        self.duration.start(interval=interval, duration=duration, end=end, begin=begin, waiting=waiting)

    def keep_run(self):
        while self.running:
            if not self.paused:
                self.on_start_app()
                # 开始监听
                try:
                    self.run_forever()
                except Exception as e:
                    print("run_forever>>>应用服务异常{0}?即将停止子链接".format(e))
                    self.running = False
                    self.stop_link_all()
                self.on_stop_app()

            if self.running:
                time.sleep(self.conf.get("interval_run"))
                if not self.paused:
                    self.counts_restart += 1
                    print("第{0}次重启链接服务器".format(self.counts_restart))

        print("应用服务线程执行结束！")

    def run(self):
        # 同步完配置
        time.sleep(0.01)
        self.keep_run()

    def send(self, point, msg, cb=None):
        try:
            toPoint = point
            if isinstance(point, str):
                if point in self.links:
                    toPoint = self.links[point]
                else:
                    print("{0}没有该link,发送失败！".format(toPoint))
                    return False
            # print(toPoint, msg)
            self.emit(toPoint, msg)
            isfunction(cb) and cb(toPoint, msg)
        except Exception as e:
            # 客户端未挥手断网
            toPoint["alive"] = False
            print("发送消息异常》》", e)

    def stop_app(self):
        print("即将stop应用轮询服务！")
        self.loop.stop()
        self.close()

    def stop_link(self, link):
        if self.type == "server":
            # print("请求链接超时，主动断开：", dir(client["handler"]))
            # print("request", dir(client["handler"].request))
            # client["handler"].request.settimeout(0)
            link["handler"].request.shutdown(2)
            link["handler"].request.close()

    def stop_link_all(self):
        for address, link in self.links.items():
            self.stop_link(link)

    def close(self):
        if self.type == "server":
            self.app.server_close()
        elif self.type == "client":
            # print(">>>>>>client:", dir(self.app))
            self.app.close()

    def quit(self):
        self.running = False
        self.stop_app()

    def pause(self):
        self.paused = True
        self.stop_app()

    def restart(self):
        if self.running:
            self.paused = False
            self.stop_app()

    def emit(self, link, msg):
        print("请自定义实现")
        pass

    def run_forever(self):
        print("请自定义实现")
        pass
