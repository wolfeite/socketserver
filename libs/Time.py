# Author: 骆琦（wolfeite）
# Corp: 朗迹
# StartTime:2020.5.27
# Version:1.0

import time

class Timer():
    def __init__(self, immediate=False):
        self.begin = 0
        self.end = 0
        # self.unit = unit
        immediate and self.start()

    def start(self):
        self.begin = time.time()

    def stop(self):
        self.end = time.time()

    def compute(self, begin, end):
        res = end - begin
        res = 0 if res < 0 else res
        self.end = end
        return round(res, 2)

    @property
    def useTime(self):
        return self.compute(self.begin, self.end)

    @property
    def time(self):
        return self.compute(self.begin, time.time())
