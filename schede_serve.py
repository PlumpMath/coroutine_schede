# coding: utf-8

import selectors
import collections
import socket
import asyncio
from base_schede import future, Task, CusHandle


class Net:

    def __init__(self, loop):
        self._selector = selectors.DefaultSelector()
        self._ready = collections.deque()
        self.loop = loop
        sock = socket.socket()
        sock.bind(('localhost', 8888))
        sock.listen(100)
        sock.setblocking(False)
        # self.loop = loop
        # self._selector.register(sock, selectors.EVENT_READ, self.accept2)
        self.add_reader(sock, self.accept, sock)


    def accept(self, sock):
        yield_obj = self.accept2(sock)
        task = Task(yield_obj, self.loop)
        self.loop.call_soon(task.step)


    async def accept2(self, sock):
        fut = future(self.loop)
        conn, addr = sock.accept()  # Should be ready
        # print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        self.recv(fut, conn, 1000)
        data = await fut
        print("\n\nrequest data: ", data)
        self.remove_reader(conn)

    def remove_reader(self, sock):
        try:
            key = self._selector.get_key(sock)
        except KeyError:
            return
        else:
            self._selector.unregister(sock)
            sock.close()

    def recv(self, fut, sock, n):
        # print("in *********")
        #fd = sock.fileno()
        print("start recv")
        try:
            data = sock.recv(n)
            print("sock recv data: ", data)
        except (BlockingIOError, InterruptedError):
            print("exception 11111111111111111111")
            self.add_reader(sock, self.recv, fut, sock, n)
        except Exception as exc:
            print("exception222222222222222222")
            fut.set_exception(exc)
        else:
            fut.set_result(data)
            # sock.close()

    def add_reader(self, sock, fn, *args):
        print("accept handler add ")
        fd = sock.fileno()
        handle = CusHandle(fn, args, self)
        try:
            key = self._selector.get_key(fd)
        except KeyError:
            print("repeat register", fd)
            self._selector.register(fd, selectors.EVENT_READ,
                                    handle)
        else:
            mask, reader= key.events, key.data
            self._selector.modify(fd, selectors.EVENT_READ, handle)

