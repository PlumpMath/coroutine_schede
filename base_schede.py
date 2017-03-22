# coding: utf-8
from collections import deque

class future:
    def __init__(self, loop):
        self.done = False
        self._result = None
        self.call_backs = []
        self.loop = loop

    def result(self):
        return self._result

    def add_done_callback(self, fn):
        self.call_backs.append(fn)

    def set_result(self, d):
        self._result = d
        for i in self.call_backs:
            self.loop.call_soon(i)

    def __await__(self):
        if not self.done:
            yield self
        return self.result()


class Loop:
    def __init__(self):
        self._ready = deque()

    def call_soon(self, fn):
        self._ready.append(fn)

    def for_ever(self):
        while True:
            if self._ready:
                fn = self._ready.popleft()
                fn()

    def as_complete(self, task):
        def map_f(fn):
            nonlocal self
            self._ready.append(Task(fn, self).step)

        if not isinstance(task, (list, tuple)):
            task = (task, )
        list(map(map_f, task))



def aa(fut, fn, flag):
    while True:
        print("please input %s: " % flag )
        a = int(fn())
        print("input is %s %d" % (flag, a))
        if a == 10:
            break
    fut.set_result("%s test data" % flag)

async def http_read(flag):
    fut = future(loop)
    aa(fut, input, flag)
    data = await fut
    return data

async def request_handler(flag):
    data = await http_read(flag)
    return data

class Task:
    def __init__(self, core, loop):
        self.core = core
        self.loop = loop

    def step(self):
        try:
            result = self.core.send(None)
        except StopIteration:
            return
        if result is None:
            self.loop.call_soon(self.step)
        elif isinstance(result, future):
            result.add_done_callback(self.wake_up)

    def wake_up(self):
        self.core.send(None)

loop = Loop()
if __name__ == '__main__':
    loop.as_complete((request_handler('request1'), request_handler('request2')))
    loop.for_ever()
