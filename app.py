# coding: utf-8
"""
async 与await 关键词 和yield from 解决的问题是: 嵌套的generator的调度问题。
为了实现异步编程的回调函数用同步的代码去实现， 因此在future.Future的代码中去进行 yield self.
然后在实现selectors的调度网络资源的代码中去 send这个

"""
import asyncio
# asyncio.get_event_loop().create_task()
from inspect import isawaitable
loop = []
class SimpleFuture:
    def __init__(self):
        self.done = False
        self.ret = None
        self.callbacks = []

    def result(self):
        # if self.done is True:
        #    return self.ret
        return 'result'

    def add_callback(self, fn):
        loop.append(fn)

    def __await__(self):
        if not self.done:
            print("await")
            yield self
        print("debug")
        return self.result()

class CusHttp:
    async def read(self):
        z = SimpleFuture()
        print("gggh")
        b = await z
        print("b", b)
        return b

class CusH2:
    async def write(self):
        def print_():
            print("test hello world\n")

        z = SimpleFuture()
        z.add_callback(print_)
        b = await z
        return b


async def test_http():
    http_obj = CusHttp()
    obj = CusH2()
    ret = await http_obj.read()
    print('ret', ret)
    ret2 = await  obj.write()
    print("ret2: ", ret2)

a = test_http()
# print(type(a))
ret = a.send(None)
print("test: ", type(ret))
#print(type(ret))
# loop.append(a)
# # while True:
# # if len(loop)
# for i in loop:
#     try:
#         if isawaitable(i):
#             ret = i.send(None)
#             print("debug**** ", ret)
#             if isinstance(ret, SimpleFuture):
#                 loop.append(i)
#         else:
#             print("not async ", type(i))
#             i()
#     except Exception as e:
#         print(e)
#         import traceback
#         traceback.print_exc()
        #pass

# loop[0].send(None)
# try:
#     z = a.send(None)
#
# except:
#     pass
# #   print('zzz', z)

