# coding: utf-8

import selectors
import collections
import socket
import asyncio
from base_schede import future, Task, CusHandle
from httptools import HttpRequestParser
from custom_http import HttpProtocol
import asyncio

class NetServer(HttpProtocol):

    def __init__(self, loop):
        super().__init__()
        self._selector = selectors.DefaultSelector()
        self._ready = collections.deque()
        self.loop = loop
        sock = socket.socket()
        sock.bind(('localhost', 8889))
        sock.listen(100)
        sock.setblocking(False)
        self.add_reader(sock, self.accept, sock)


    def accept(self, sock):
        yield_obj = self.accept2(sock)
        task = Task(yield_obj, self.loop)
        self.loop.call_soon(task.step)

    async def make_response(self, sock, request, response):
        fut = future(self.loop)
        self.add_writer(sock, self.send, fut, sock, response)
        await fut


    def handle_request(self, request):
        from custom_http import Response
        """ In here, Web server Logical service.
            Router and request handle.
        """
        obj = Response(body="hello world", content_type='text/plain')
        return obj.output()


    async def accept2(self, sock):
        fut = future(self.loop)
        conn, addr = sock.accept()  # Should be ready
        conn.setblocking(False)
        self.recv(fut, conn, 1024*1024*10)
        data = await fut
        print("\ndata:", type(data), '\n', data, '\n')
        self.parser = HttpRequestParser(self)
        self.parser.feed_data(data)
        print('recive data: ', self.request.body)
        response = self.handle_request(self.request)
        await self.make_response(conn, self.request, response)

        self.remove_reader(conn)

    def remove_reader(self, sock):
        try:
            key = self._selector.get_key(sock)
        except KeyError:
            return
        else:
            self._selector.unregister(sock)
            sock.close()

    def send(self, fut, sock, send_data):
        try:
            data = sock.send(send_data)
        except (BlockingIOError, InterruptedError):
            self.add_writer(sock, self.send, fut, sock, send_data)
        except Exception as exc:
            fut.set_exception(exc)
        else:
            fut.set_result(data)

    def recv(self, fut, sock, n):
        try:
            data = sock.recv(n)
        except (BlockingIOError, InterruptedError):
            self.add_reader(sock, self.recv, fut, sock, n)
        except Exception as exc:
            fut.set_exception(exc)
        else:
            fut.set_result(data)

    def add_reader(self, sock, fn, *args):
        fd = sock.fileno()
        handle = CusHandle(fn, args, self)
        try:
            key = self._selector.get_key(fd)
        except KeyError:
            self._selector.register(fd, selectors.EVENT_READ,
                                    handle)
        else:
            mask, reader= key.events, key.data
            self._selector.modify(fd, selectors.EVENT_READ, handle)

    def add_writer(self, sock, fn, *args):
        fd = sock.fileno()
        handle = CusHandle(fn, args, self)
        try:
            key = self._selector.get_key(fd)
        except KeyError:
            self._selector.register(fd, selectors.EVENT_WRITE,
                                    handle)
        else:
            mask, writer= key.events, key.data
            self._selector.modify(fd, selectors.EVENT_WRITE, handle)
