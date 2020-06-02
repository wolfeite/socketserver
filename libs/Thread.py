# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.5.18
# Version:1.0

'''
edit:
    1-[time：2020.5.28, by：wolfeite,
    bug：Loop基类当睡眠等待过长时，多次开停操作，造成多个线程共用一个stop状态,而产生无法自动退出线程的问题
    解决方案：为每个线程建立状态列表，当stop操作后，将所有线程状态都设置为关闭。]
    2-[time：2020.5.30, by：wolfeite,
    bug：循环语句异常，而导致无法结束进入stop状态。解决方案就是进行异常捕获处理，并抽离出run执行部分]
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

    def run(self):
        # 同步加载完轮询池
        time.sleep(0.01)
        id = threading.currentThread().ident
        isfunction(self.begin) and self.begin()
        print("loop进入轮询！！！轮询池为：{0}，当前线程池：{1}".format(self._pool_, self._pond_))
        try:
            self.loop(id)
        except Exception as e:
            print("由于loop异常！执行stop操作", e)
            self.stop()
        isfunction(self.end) and self.end()
        self.clearThread(id)

    def loop(self, id):
        while not self._pond_[id]:
            for fns in self._pool_:
                fns[0](*fns[1])
            time.sleep(self.interval)

    def stop(self):
        self._isStop_ = True
        self._pool_ = [] if self.isClear else self._pool_
        for id in self._pond_:
            self._pond_[id] = True
        print("loop轮询状态全设置为停止：True！！！轮询池为：{0}： 当前线程池：{1}<<<".format(self._pool_, self._pond_))
        return self

    def clearThread(self, id):
        self._pond_.pop(id)
        print("线程{0}结束退出，当前线程池：{1}".format(id, self._pond_))

    def connect(self, func, args=[]):
        if self.isStop:
            fns = (func, args)
            self._pool_.append(fns)
        return self

    def setInterval(self, interval):
        self.interval = interval / 1000 if interval >= 1 else 0.1

    @property
    def isStop(self):
        return self._isStop_

    def start(self, interval=100, begin=None, end=None):
        self.setInterval(interval)
        self.begin, self.end = begin, end
        if self._isStop_:
            self._isStop_ = False
            t = threadFactory(self.run, daemon=self.daemon)
            self._pond_[t.ident] = False
            print(">>>创建新进程ID:{0},loop配置为：清空轮询池：{1}，间隔为：{2}，".format(t.ident, self.isClear, self.interval))

class Timeout(Loop):
    def __init__(self, daemon=True, isClear=True):
        super(Timeout, self).__init__(daemon=daemon, isClear=isClear)

    def loop(self, id):
        p = self._pool_
        length = len(p)
        for i in range(length):
            fns = p[i]
            fns[0](*fns[1])
            i < length - 1 and time.sleep(self.interval)
        self.stop()

class Interval(Loop):
    def __init__(self, daemon=True, isClear=True):
        super(Interval, self).__init__(daemon=daemon, isClear=isClear)
        self.wait = 0.2
        self.waiting = lambda t: t
        self.timer = Timer()

    def loop(self, id):
        self.timer.start()
        while not self._pond_[id]:
            dis = self.timer.time
            self.waiting(dis)
            if dis >= self.interval:
                for fns in self._pool_:
                    fns[0](*fns[1])
                self.timer.start()

            time.sleep(self.wait)

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

    def loop(self, id):
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

    def setDuration(self, duration):
        self.duration = duration / 1000 if duration > 1 else 1

    def start(self, interval=400, begin=None, end=None, wait=200, duration=1000, waiting=None):
        self.setDuration(duration)
        super(Duration, self).start(interval=interval, begin=begin, end=end, wait=wait, waiting=waiting)
