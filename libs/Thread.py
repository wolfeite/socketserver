# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.5.18
# Version:1.0

'''
edit:
    [time：2020.5.28, by：wolfeite,
    bug：Loop基类当睡眠等待过长时，多次开停操作，造成多个线程共用一个stop状态,而产生无法自动退出线程的问题
    解决方案：为每个线程建立状态列表，当stop操作后，将所有线程状态都设置为关闭。]
'''
import threading
import time
from inspect import isfunction
from libs.Time import Timer

class Thread(threading.Thread):
    def __init__(self, func, args=[], daemon=True):
        super(Thread, self).__init__(daemon=daemon)
        self.func = func
        self.args = args

    def run(self):
        self.res = self.func(*self.args)

    @property
    def result(self):
        try:
            return self.res
        except Exception:
            return None

def threadFactory(func, args=[], kwargs={}, daemon=True):
    thread = threading.Thread(target=func, args=args, kwargs=kwargs)
    thread.setDaemon(daemon)
    thread.start()
    return thread

class Loop():
    def __init__(self, daemon=True, isClear=True):
        self.interval = 0.1
        self.daemon = daemon
        self.isClear = isClear
        self._pool_ = []
        self._isStop_ = True
        self.begin, self.end = None, None
        self._pond_ = {}

    def loop(self):
        # 同步加载完轮询池
        time.sleep(0.01)
        id = threading.currentThread().ident
        isfunction(self.begin) and self.begin()
        print("一个loop进入轮询！！！暂停后是否清空轮询池：{0}，间隔为：{1}，轮询池为：{2}".format(self.isClear, self.interval, self._pool_))
        while not self._pond_[id]:
            for fns in self._pool_:
                fns[0](*fns[1])
            time.sleep(self.interval)
        isfunction(self.end) and self.end()
        self.clearThread(id)

    def stop(self):
        self._isStop_ = True
        self._pool_ = [] if self.isClear else self._pool_
        for id, isStop in self._pond_.items():
            self._pond_[id] = True
        print("一个loop轮询结束！！！轮询池为：{0}： 未执行完成线程：{1}<<<".format(self._pool_, self._pond_))
        return self

    def clearThread(self, id):
        self._pond_.pop(id)
        print("线程{0}结束，当前线程池为：{1}".format(id, self._pond_))

    def connect(self, func, args=[]):
        fns = (func, args)
        self._pool_.append(fns)
        return self

    def setInterval(self, interval):
        self.interval = interval / 1000 if interval >= 1 else 0.1

    def start(self, interval=100, begin=None, end=None):
        self.setInterval(interval)
        self.begin, self.end = begin, end
        if self._isStop_:
            self._isStop_ = False
            t = threadFactory(self.loop, daemon=self.daemon)
            self._pond_[t.ident] = False
            print(">>>开始创建一个新进程ID:{0}来执行loop!!!".format(t.ident))

class Timeout(Loop):
    def __init__(self, daemon=True, isClear=True):
        super(Timeout, self).__init__(daemon=daemon, isClear=isClear)

    def loop(self):
        id = threading.currentThread().ident
        isfunction(self.begin) and self.begin()
        print("timeout类实例！！！暂停后是否清空轮询池：{0}，间隔为：{1}，轮询池为：{2}".format(self.isClear, self.interval, self._pool_))
        p = self._pool_
        length = len(p)
        for i in range(length):
            fns = p[i]
            fns[0](*fns[1])
            i < length - 1 and time.sleep(self.interval)
        isfunction(self.end) and self.end()
        self.stop()
        self.clearThread(id)

class Interval(Loop):
    def __init__(self, daemon=True, isClear=True):
        super(Interval, self).__init__(daemon=daemon, isClear=isClear)
        self.wait = 0.2
        self.waiting = lambda t: t
        self.timer = Timer()
    def loop(self):
        # 同步加载完轮询池
        time.sleep(0.01)
        id = threading.currentThread().ident
        isfunction(self.begin) and self.begin()
        print("一个loop进入轮询！！！暂停后是否清空轮询池：{0}，间隔为：{1}，轮询池为：{2}".format(self.isClear, self.interval, self._pool_))
        self.timer.start()
        while not self._pond_[id]:
            dis = self.timer.time
            self.waiting(dis)
            if dis >= self.interval:
                for fns in self._pool_:
                    fns[0](*fns[1])
                self.timer.start()

            time.sleep(self.wait)

        isfunction(self.end) and self.end()
        self.clearThread(id)

    def setWait(self, wait):
        self.wait = wait / 1000 if wait > 1 else 0.2

    def start(self, interval=100, begin=None, end=None, wait=200, waiting=None):
        self.setWait(wait)
        if isfunction(waiting):
            self.waiting = waiting
        super(Interval, self).start(interval=interval, begin=begin, end=end)

class Duration(Interval):
    def __init__(self, daemon=True, isClear=True):
        super(Duration, self).__init__(daemon=daemon, isClear=isClear)
        self.duration = 1

    def loop(self):
        # 同步加载完轮询池
        time.sleep(0.01)
        id = threading.currentThread().ident
        isfunction(self.begin) and self.begin()
        print("一个loop进入轮询！！！暂停后是否清空轮询池：{0}，间隔为：{1}，轮询池为：{2}".format(self.isClear, self.interval, self._pool_))
        self.timer.start()
        startTime = time.time()
        while not self._pond_[id]:
            totalTime = time.time() - startTime
            if totalTime > self.duration:
                self.stop()
            else:
                dis = self.timer.time
                self.waiting(dis)
                if dis >= self.interval:
                    for fns in self._pool_:
                        fns[0](*fns[1])
                    self.timer.start()

            time.sleep(self.wait)

        isfunction(self.end) and self.end()
        self.clearThread(id)

    def setDuration(self, duration):
        self.duration = duration / 1000 if duration > 1 else 1

    def start(self, interval=400, begin=None, end=None, wait=200, duration=1000):
        self.setDuration(duration)
        super(Duration, self).start(interval=interval, begin=begin, end=end, wait=wait, waiting=None)

class HeartBeat():
    def __init__(self):
        pass

    def start(self):
        pass

    def keep_alive(self):
        pass
