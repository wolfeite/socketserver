import threading
import time
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

def threadFactory(func, args=[], daemon=True):
    thread = threading.Thread(target=func, args=args)
    thread.setDaemon(daemon)
    thread.start()
    return thread

class Loop():
    def __init__(self, daemon=True, isClear=True):
        self.isStop = True
        self.daemon = daemon
        self.isClear = isClear
        self.pool = []
        self.interval = 1

    def loop(self):
        # 同步加载完轮询池
        time.sleep(0.1)
        print("一个loop进入轮询阶段！！！间隔为：{0}当前轮询池为：{1}".format(self.interval, self.pool))
        while not self.isStop:
            for fns in self.pool:
                fns[0](*fns[1])
            time.sleep(self.interval)

    def stop(self):
        self.isStop = True
        self.pool = [] if self.isClear else self.pool
        print("一个loop轮询结束！！！结束后是否清空轮询池：{0}，轮询池为：{1}： <<<".format(self.isClear, self.pool))
        return self

    def connect(self, func, args=[]):
        fns = (func, args)
        self.pool.append(fns)
        return self

    def start(self, interval=1):
        if self.isStop:
            self.interval = interval
            self.isStop = False
            print(">>>开始创建一个新进程来执行loop!!!")
            threadFactory(self.loop, daemon=self.daemon)
