# coding: utf-8

from asyncio.futures import Future
import asyncio


class future(Future):
    def __init__(self, loop):
        super().__init__(loop=loop)
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

    def __iter__(self):
        if not self.done:
            print("ggg")
            yield self
        print("wait over")
        return self.result()

def aa(fut, fn, flag):
    while True:
        print("please input %s: " % flag )
        a = int(fn())
        print("input is %s %d" % (flag, a))
        if a == 10:
            break
    fut.set_result("%s test data" % flag)


async def http_read(loop):

    #fut = Future()
    fut = Future()
    flag = 25
    aa(fut, input, flag)
    data = await fut
    print("\n\n\n\n****************: ", data, '\n\n')
    return data


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(http_read(loop))
    loop.run_forever()
