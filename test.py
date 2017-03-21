# coding: utf-8

from asyncio.futures import Future
from asyncio import events
import selectors
import socket


class Net:

    def __init__(self, loop):
        self._selector = selectors.DefaultSelector()
        sock = socket.socket()
        sock.bind(('localhost', 1234))
        sock.listen(100)
        sock.setblocking(False)
        self.loop = loop
        self._selector.register(sock, selectors.EVENT_READ, self.accept)
        # self.loop.call_soon()

    def accept(self, sock, mask):
        conn, addr = sock.accept()  # Should be ready
        print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        self._selector.register(conn, selectors.EVENT_READ, self.each_connect)


    def each_connect(self, sock, mask):
        fut = Future()
        self.recv(fut, sock, 20)
        return fut


    def recv(self, fut, sock, n):

        fd = sock.fileno()

        try:
            data = sock.recv(n)
        except (BlockingIOError, InterruptedError):
            self.add_reader(fd, self.recv, fut, sock, n)
        except Exception as exc:
            fut.set_exception(exc)
        else:
            fut.set_result(data)

    def add_reader(self, fd, fn, *args):
        handle = events.Handle(fn, args, self)
        try:
            key = self._selector.get_key(fd)
        except KeyError:
            self._selector.register(fd, selectors.EVENT_READ,
                                    (handle, None))
        else:
            mask, (reader, writer) = key.events, key.data
            self._selector.modify(fd, mask | selectors.EVENT_READ,
                                  (handle, writer))

import collections

class Loop:
    def __init__(self):
        self._ready = collections.deque()

    def run_for_ever(self):
        p

def server_start():
    loop = Loop()
    serv = Net(loop)
    loop.
