# coding: utf-8
"""
implement the http parser
"""
from http.cookiejar import CookieJar


COMMON_STATUS_CODES = {
    200: b'OK',
    400: b'Bad Request',
    404: b'Not Found',
    500: b'Internal Server Error',
}
ALL_STATUS_CODES = {
    100: b'Continue',
    101: b'Switching Protocols',
    102: b'Processing',
    200: b'OK',
    201: b'Created',
    202: b'Accepted',
    203: b'Non-Authoritative Information',
    204: b'No Content',
    205: b'Reset Content',
    206: b'Partial Content',
    207: b'Multi-Status',
    208: b'Already Reported',
    226: b'IM Used',
    300: b'Multiple Choices',
    301: b'Moved Permanently',
    302: b'Found',
    303: b'See Other',
    304: b'Not Modified',
    305: b'Use Proxy',
    307: b'Temporary Redirect',
    308: b'Permanent Redirect',
    400: b'Bad Request',
    401: b'Unauthorized',
    402: b'Payment Required',
    403: b'Forbidden',
    404: b'Not Found',
    405: b'Method Not Allowed',
    406: b'Not Acceptable',
    407: b'Proxy Authentication Required',
    408: b'Request Timeout',
    409: b'Conflict',
    410: b'Gone',
    411: b'Length Required',
    412: b'Precondition Failed',
    413: b'Request Entity Too Large',
    414: b'Request-URI Too Long',
    415: b'Unsupported Media Type',
    416: b'Requested Range Not Satisfiable',
    417: b'Expectation Failed',
    422: b'Unprocessable Entity',
    423: b'Locked',
    424: b'Failed Dependency',
    426: b'Upgrade Required',
    428: b'Precondition Required',
    429: b'Too Many Requests',
    431: b'Request Header Fields Too Large',
    500: b'Internal Server Error',
    501: b'Not Implemented',
    502: b'Bad Gateway',
    503: b'Service Unavailable',
    504: b'Gateway Timeout',
    505: b'HTTP Version Not Supported',
    506: b'Variant Also Negotiates',
    507: b'Insufficient Storage',
    508: b'Loop Detected',
    510: b'Not Extended',
    511: b'Network Authentication Required'
}

class CIDict(dict):

    def get(self, key, default=None):
        return super().get(key.casefold(), default)

    def __getitem__(self, key):
        return super().__getitem__(key.casefold())

    def __setitem__(self, key, value):
        return super().__setitem__(key.casefold(), value)

    def __contains__(self, key):
        return super().__contains__(key.casefold())


class Request:
    def __init__(self, url_bytes, headers, version, method):
        self.body = []
        self.url_bytes = url_bytes
        self.headers = CIDict(headers)
        self.version = version
        self.method = method

class Response:
    def __encode_body(self, data, encoding='utf-8'):
        if isinstance(data , str):
            data = data.encode(encoding)
        elif isinstance(data, bytes):
            data = data
        else:
            raise TypeError("body only accept str or bytes object")
        return data

    def __init__(self, body=None, status=200,
                 headers=None, content_type='text/pain', cookies=None):
        if body is None:
            self.body = b''
        else:
            self.body = self.__encode_body(body)
        print("get data:", self.body)
        self.status = status
        self.headers = headers or {}
        self._cookies = CookieJar(self.headers)
        self.content_type = content_type

    def _parse_headers(self):
        headers = b''
        for name, value in self.headers.items():
            try:
                headers += (
                    b'%b: %b\r\n' % (
                        name.encode('utf-8'), value.encode('utf-8')))
            except AttributeError:
                headers += (
                    b'%b: %b\r\n' % (
                        str(name).encode('utf-8'), str(value).encode('utf-8')))

        return headers

    def output(self, version='1.1', keep_alive=True,
               keep_alive_timeout=60):
        """
        在http1.1中为了避免每一个请求都进行一次tcp连接，会建立一个tcp请求，然后多次复用，
        为兼容浏览器，所以会保留connect=keep-alive,
        """
        timeout_header = b''
        print("debug: ", self.body)
        if keep_alive and keep_alive_timeout is not None:
            timeout_header = b'Keep-Alive: %d\r\n' % keep_alive_timeout
        self.headers['Content-Length'] = self.headers.get(
            'Content-Length', len(self.body))
        self.headers['Content-Type'] = self.headers.get(
            'Content-Type', self.content_type)

        headers = self._parse_headers()

        status = COMMON_STATUS_CODES.get(self.status)
        if not status:
            status = ALL_STATUS_CODES.get(self.status)

        return (b'HTTP/%b %d %b\r\n'
                b'Connection: %b\r\n'
                b'%b'
                b'%b\r\n'
                b'%b') % (
                   version.encode(),
                   self.status,
                   status,
                   b'keep-alive' if keep_alive else b'close',
                   timeout_header,
                   headers,
                   self.body
               )


class HttpProtocol:
    def __init__(self):
        self.headers = []

    def on_url(self, url):
        self.url = url


    def on_header(self, name, value):
        # if name == b'Content-Length' and int(value) > self.request_max_size:
        #     exception = PayloadTooLarge('Payload Too Large')
        #     self.write_error(exception)

        self.headers.append((name.decode().casefold(), value.decode()))


    def on_headers_complete(self):
        self.request = Request(
            url_bytes=self.url,
            headers=CIDict(self.headers),
            version=self.parser.get_http_version(),
            method=self.parser.get_method().decode(),
        )

    def on_body(self, body):
        self.request.body.append(body)

    def on_message_complete(self):
        if self.request.body:
            self.request.body = b''.join(self.request.body)
