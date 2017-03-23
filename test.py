# coding: utf-8

from asyncio.futures import Future
from asyncio import events
# from asyncio.tasks import Task
import selectors
import socket
import asyncio


class CusTask:
    def __init__(self, crop, loop):
        self._crop = crop
        self.loop = loop

    def _step(self):
        try:

            result = self._crop.send(None)
        except StopIteration as exc:
            print("stop ", exc.value)
            #self.set_result(exc.value)
            return
        else:
            if result is None:
                self.loop.call_soon(self._step)


class CusHandle:
    def __init__(self, fn, args, loop):
        self.call_func = fn
        self.args = args
        self.loop = loop

    def _run(self):
        self.call_func(*self.args)


class Net:

    def __init__(self):
        self._selector = selectors.DefaultSelector()
        self._ready = collections.deque()
        sock = socket.socket()
        sock.bind(('localhost', 8888))
        sock.listen(100)
        sock.setblocking(False)
        # self.loop = loop
        # self._selector.register(sock, selectors.EVENT_READ, self.accept2)
        self.add_reader(sock, self.accept, sock)
        # self.loop.call_soon()
        # self.call_soon()



    def accept(self, sock):
        # fut = Future()
        # conn, addr = sock.accept()  # Should be ready
        # print('accepted', conn, 'from', addr)
        # conn.setblocking(False)
        # self._selector.register(conn, selectors.EVENT_READ, self.each_connect)
        # fut = Future()
        yield_obj = self.accept2(sock)
        task = CusTask(yield_obj, self)
        self.add_soon(CusHandle(task._step, tuple(), self))
        # print("sock:  ", sock.fileno())
        self.socket_d = {sock.fileno(): yield_obj}
        # yield from fut


    @asyncio.coroutine
    def accept2(self, sock):
        fut = Future()
        conn, addr = sock.accept()  # Should be ready
        print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        self.recv(fut, conn, 20)
        data = yield from fut

        # self._selector.register(conn, selectors.EVENT_READ, self.each_connect)
        # self.add_reader(conn, self.each_connect, conn)
        # task = CusTask()
        # yield from fut
        # fut.set_result(None)
        # self.add_reader(conn, self.each_connect, )
        # yield from fut
        # self.add_reader(conn, self.each_connect, sock, fut)
        # self.add_callback()


    def get_debug(self):
        return False

    @asyncio.coroutine
    def each_connect(self, sock, mask):
        #fut = Future()
        #.recv(fut, sock, 20)
        #return fut
        fut = Future()
        self.recv(fut, sock, 20)
        # yield from fut
        data = yield from fut
        print("recv data", data)
        #fut = Task()
        #fut = Future()
        # yield from fut


    def run_coroutine(self, fn):
        fn.send(None)

    def recv(self, fut, sock, n):
        print("in *********")
        fd = sock.fileno()

        try:
            data = sock.recv(n)
            print("\n recv data: ", data)
        except (BlockingIOError, InterruptedError):
            print("gggggg")
            self.add_reader(fd, self.recv, fut, sock, n)
        except Exception as exc:
            fut.set_exception(exc)
        else:
            fut.set_result(data)
            # sock.close()

            self._selector.unregister(sock)
            sock.close()


    def add_reader(self, fd, fn, *args):
        handle = CusHandle(fn, args, self)
        try:
            key = self._selector.get_key(fd)
        except KeyError:
            self._selector.register(fd, selectors.EVENT_READ,
                                    handle)
        else:
            mask, reader= key.events, key.data
            self._selector.modify(fd, selectors.EVENT_READ, handle)

    def add_soon(self, handle):
        self._ready.append(handle)

    def run_once(self):
        pass



import collections

class Loop:
    def __init__(self):
        self._ready = collections.deque()

    def run_for_ever(self):
        pass

from functools import partial
def server_start():
    loop = Loop()
    serv = Net()
    index = 0
    flag = True
    while index >=0:
        index += 1
        events = serv._selector.select(2)
        for key, mask in events:
            # print("kkk")
            # print(mask, key.fileobj)
            fileobj, reader = key.fileobj, key.data
            print("fd ", fileobj)
            # callback = key.data
            # callback(key.fileobj, mask)
            # reader = partial(reader, sock=fileobj, mask=mask)
            # reader is a coroutine object
            serv.add_soon(reader)
            print("once")
            flag = False
        if len(serv._ready) > 0:
            run = serv._ready.popleft()
            # print(type(run), run)
            print("11111111")
            run._run()
        # if len(serv._ready) > 0: print('len', len(serv._ready), serv._ready[0])
        # for i in serv._ready:
        #    print(i)
        #    i()




if __name__ == '__main__':
    server_start()

