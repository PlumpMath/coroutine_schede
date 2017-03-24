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
        print("start sned*****************")
        fut = future(self.loop)
        # this fut obj is less useful otherwise you have to generate a new task
        self.add_writer(sock, self.send, fut, sock, response)
        await fut

    def _parse_headers(self, data):
        headers = b''
        for name, value in data.items():
            try:
                headers += (
                    b'%b: %b\r\n' % (
                        name.encode(), value.encode('utf-8')))
            except AttributeError:
                headers += (
                    b'%b: %b\r\n' % (
                        str(name).encode(), str(value).encode('utf-8')))

        return headers

    def handle_request(self, request):
        version = '1.1'
        status = 200
        keep_alive = False
        timeout_header = b''
        headers = {}
        headers['Transfer-Encoding'] = 'chunked'
        #f "Content-Length" in headers:
        #headers.pop('Content-Length', None)
        headers['Content-Length'] = len(b'test for shawn')
        headers['Content-Type'] = 'text/plain'

        headers= self._parse_headers(self.request.headers)
        self.body = b'test for shawn'

        return (b'HTTP/%b %d %b\r\n'
                b'Connection: %b\r\n'
                b'%b'
                b'%b\r\n'
                b'%b') % (
                   version.encode(),
                   status,
                   b'OK',
                   b'keep-alive' if keep_alive else b'close',
                   timeout_header,
                   headers,
                   self.body
               )

    async def accept2(self, sock):
        fut = future(self.loop)
        conn, addr = sock.accept()  # Should be ready
        conn.setblocking(False)
        self.recv(fut, conn, 1000)
        data = await fut

        self.parser = HttpRequestParser(self)
        print("\n\nget data: ", data, type(data))
        self.parser.feed_data(data)

        response = self.handle_request(self.request)
        await self.make_response(conn, self.request, response)

        # print("version: ", self.parser.get_http_version())

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
        print("start send===================")
        try:
            data = sock.send(send_data)
        except (BlockingIOError, InterruptedError):
            print("send ))))")
            self.add_writer(sock, self.send, fut, sock, send_data)
        except Exception as exc:
            fut.set_exception(exc)
        else:
            fut.set_result(data)

    def recv(self, fut, sock, n):
        print("start recv")
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
            mask, reader= key.events, key.data
            self._selector.modify(fd, selectors.EVENT_WRITE, handle)
