# coding: utf-8

from asyncio.futures import Future
from asyncio import events
import selectors
import socket


class Net:

    def __init__(self):
        self._selector = selectors.DefaultSelector()
        self._ready = collections.deque()
        sock = socket.socket()
        sock.bind(('localhost', 8888))
        sock.listen(100)
        sock.setblocking(False)
        # self.loop = loop
        self._selector.register(sock, selectors.EVENT_READ, self.accept)
        # self.loop.call_soon()
        # self.call_soon()



    def accept(self, sock, mask):
        fut = Future()
        # conn, addr = sock.accept()  # Should be ready
        # print('accepted', conn, 'from', addr)
        # conn.setblocking(False)
        # self._selector.register(conn, selectors.EVENT_READ, self.each_connect)

        return fut

    def accept2(self, sock):
        fut = Future()
        conn, addr = sock.accept()  # Should be ready
        print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        self._selector.register(conn, selectors.EVENT_READ, self.each_connect)

    def each_connect(self, sock, mask):
        #fut = Future()
        #.recv(fut, sock, 20)
        #return fut
        data = sock.recv(20)
        print("data", data)
        sock.close()
        self._selector.unregister(sock)


    def recv(self, fut, sock, n):

        fd = sock.fileno()

        try:
            data = sock.recv(n)
        except (BlockingIOError, InterruptedError):
            print("ggg")
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
                                    handle)
        else:
            mask, reader= key.events, key.data
            self._selector.modify(fd, selectors.EVENT_READ, handle)

    def add_callback(self, handle):
        self._ready.append(handle)

    def run_once(self):
        pass



import collections

class Loop:
    def __init__(self):
        self._ready = collections.deque()

    def run_for_ever(self):
        pass


def server_start():
    loop = Loop()
    serv = Net()
    index = 0
    while index >= 0:
        index += 1
        events = serv._selector.select(2)
        for key, mask in events:
            # print("kkk")
            # print(mask, key.fileobj)
            fileobj, reader = key.fileobj, key.data
            # callback = key.data
            # callback(key.fileobj, mask)
            serv.add_callback(reader)


if __name__ == '__main__':
    server_start()
