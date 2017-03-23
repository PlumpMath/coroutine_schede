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
            print("ggg")
            yield self
        print("wait over")
        return self.result()


import selectors
import sys

class CusHandle:
    def __init__(self, fn, args, loop):
        self.call_back = fn
        self.args = args
        self.loop = loop

    def __call__(self):
        self.call_back(*self.args)


class Loop:
    def __init__(self):
        self._ready = deque()
        # self.selector = selector
        # self._selector = selectors.DefaultSelector()
        # self._selector.register(sys.stdin, selectors.EVENT_READ)

    def call_soon(self, fn):
        self._ready.append(fn)

    def for_ever(self):
        while True:
            if self._ready:
                print("all task", self._ready)
                fn = self._ready.popleft()
                print("fn", fn)
                fn()

    def as_complete(self, task):
        #def map_f(fn):
        #    nonlocal self
        task = Task(task, self)
        self._ready.append(task.step)




def aa(fut, fn):
    while True:
        print("please input %s: " )
        a = int(fn())
        print("input is %d" % (a))
        if a == 10:
            break
    fut.set_result("test data")


async def http_read():
    print("start so early")
    fut = future(loop)
    flag = 25
    aa(fut, input)
    # print("gggggg")
    data = await fut
    # print("last  data", data)
    return data


async def request_handler():
    data = await http_read()
    print("\n\ndata*", data)
    return data


class Task:

    def __init__(self, core, loop):
        self.core = core
        self.loop = loop

    def step(self):
        print("step run")
        try:
            print("why ")
            result = self.core.send(None)
            print("NO RUN")
        except StopIteration as ex:
            print('stop ***')
            return
        else:
            if result is None:
                print("none")
                self.loop.call_soon(self.step)
            elif isinstance(result, future):
                print("wake up, and result", result)
                # result.add_done_callback(self.wake_up)
                self.loop.call_soon(self.wake_up)
            else:
                print("\nthis is other result: ", result)

    def wake_up(self):
        print("send wake up", self.core)
        try:
            self.core.send(None)
        except StopIteration as ex:
            # print(ex.value)
            pass





loop = Loop()
if __name__ == '__main__':
    from schede_serve import Net
    Net(loop)
    # loop.as_complete()
    loop.for_ever()
    # a = http_read()
    # a.send(None)
    # print(type(a))
    # a = http_read()
    # print("send")
    # a.send(None)
    # print("send 2 ")
    # try:
    #     ret = a.send(None)
    # except StopIteration as ex:
    #     print(ex.value)

