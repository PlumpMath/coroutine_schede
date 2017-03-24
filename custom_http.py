# coding: utf-8
"""
implement the http parser
"""
class CIDict(dict):
    """Case Insensitive dict where all keys are converted to lowercase
    This does not maintain the inputted case when calling items() or keys()
    in favor of speed, since headers are case insensitive
    """

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
    def __init__(self, **args):
        pass


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
        print("before body: **", body)
        self.request.body.append(body)

    def on_message_complete(self):
        if self.request.body:
            self.request.body = b''.join(self.request.body)

        print("body", self.request.body, self.request.headers)
