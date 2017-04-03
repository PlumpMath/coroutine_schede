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
        self.done = True

    def set_exception(self, exc):
        print("exc", exc)

    def __await__(self):
        if not self.done:
            yield self
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
    def __init__(self, selector=None):
        self._ready = deque()
        self.selector = None

    def call_soon(self, fn):
        self._ready.append(fn)

    def for_ever(self):
        if self.selector is None:
            raise RuntimeError("you should init a selector fro Loop")
        while True:
            events = self.selector.select()
            for key, mask in events:
                callback = key.data
                self._ready.append(callback)

            while self._ready:
                fn = self._ready.popleft()
                fn()

    def as_complete(self, task):
        task = Task(task, self)
        self._ready.append(task.step)

    def set_selector(self, selector):
        self.selector = selector


class Task:

    def __init__(self, core, loop):
        self.core = core
        self.loop = loop

    def step(self):
        try:
            result = self.core.send(None)
        except StopIteration as ex:
            return
        else:
            if result is None:
                self.loop.call_soon(self.step)
            elif isinstance(result, future):
                if result.done is False:
                    result.add_done_callback(self.step)
                else:
                    self.loop.call_soon(self.step)
            else:
                result.set_exception("can not handle, runtime error")

    def wake_up(self):
        try:
            result = self.core.send(None)
        except StopIteration as ex:
            print("wake up exception: ", ex.value)


loop = Loop()
if __name__ == '__main__':
    from schede_serve import NetServer
    obj = NetServer(loop)
    loop.set_selector(obj._selector)
    loop.for_ever()


