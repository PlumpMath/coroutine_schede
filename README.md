# asycio dispatch with httpserver
* 实现了asyncio模块 对coroutine 对象的调度算法。
* 实现了一个基于上述调度算法的http web server

## what is the async、await

    python3.5 引入了async 、await  语法，作用是生成了coroutine对象， 这个对象和其他dict、list一样。就像一个迭代器对象有_iter_ 、_next_ 内置方法一样, coroutine对象实现了__await__方法。
### code
 
     class CusCoroutine:
         def __await__(self):
            yield self
            reurn 

## what is the difference between the coroutine and generator
熟悉tornado的应该了解@gen.coroutine这个装饰器，它的本质是管理多个generator的切换。让我们来看下如下代码：
    
    def fibonacci(n):
        if n <= 1:
            return 1
        c1 = yield fibonacci(n-1)
        c2 = yield fibonacci(n-2)
        return c1 + c2
也许你绞尽脑汁也无法让这段 "简单" 的代码正常运行起来。
原因在于 fibonacci(n-1)会生成一个新的generator。 这个看来就像一个函数调用另一个函数一样，事实上的确如此，但却又有所不同，在我们调用普通函数时，操作系统会将当前函数的上下文信息压到堆栈中，函数调用完成时又会从堆栈中弹出当前上下文信息。但是我们的generator和普通函数不一样。要想和普通
函数一样进行上下文的保存和切换，程序员们只能自己去控制。
而这就是tornado的@@gen.coroutine装饰器所要做的事情。python3.5为了让协程看起来更酷一点。于是有了coroutine 对象， async、await语法糖。
可能有的小伙伴对上述程序耿耿于怀，篇幅原因，在这里没办法给出完成的解答。有兴趣的可以看一下这篇问文章 http://sahandsaba.com/understanding-asyncio-node-js-python-3-4.html
## what is the asyncio
通过上面的内容我们知道了协程的核心构成单元 coroutine对象。现在是时候来展示它真正的价值了，就是asyncio模块了。
首先在搞清楚asyncio之前，我需要再说明一些东西。
### async io and selector
selector 是python3.5中添加的异步事件触发机制epoll的封装。
写异步的代码免不了回掉函数，即使asyncio 一样。
这里是selector模块的基本用法

    import selectors
    import socket
    sel = selectors.DefaultSelector()
    def accept(sock, mask):
        conn, addr = sock.accept()  # Should be ready
        print('accepted', conn, 'from', addr)
        conn.setblocking(False)
        sel.register(conn, selectors.EVENT_READ, read)

    def read(conn, mask):
        data = conn.recv(1000)  # Should be ready
        if data:
            print('echoing', repr(data), 'to', conn)
            conn.send(data)  # Hope it won't block
        else: 
            print('closing', conn)
            sel.unregister(conn)
            conn.close()

    sock = socket.socket()
    sock.bind(('localhost', 1234))
    sock.listen(100)
    sock.setblocking(False)
    sel.register(sock, selectors.EVENT_READ, accept)
    
    while True:
        events = sel.select()
        for key, mask in events:
            callback = key.data
            callback(key.fileobj, mask)
同过上面的代码应该知晓了异步编程的基本模式和思路。
接下来展示用async 编写的代码

    async def accept2(self, sock):
        fut = future(self.loop)
        conn, addr = sock.accept()  # Should be ready
        conn.setblocking(False)
        self.recv(fut, conn, 1024*1024*10)
        data = await fut

    class future:
        def __init__(self, loop):
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
            self.done = True
    
        def set_exception(self, exc):
            print("exc", exc)
    
        def __await__(self):
            if not self.done:
                yield self
            return self.result()
            
     def recv(self, fut, sock, n):
        try:
            data = sock.recv(n)
        except (BlockingIOError, InterruptedError):
            self.add_reader(sock, self.recv, fut, sock, n)
        except Exception as exc:
            fut.set_exception(exc)
        else:
            fut.set_result(data)
            
    class Task:

        def __init__(self, core, loop):
            self.core = core
            self.loop = loop
    
        def step(self):
            try:
                result = self.core.send(None)
            except StopIteration as ex:
                return
            else:
                if result is None:
                    self.loop.call_soon(self.step)
                elif isinstance(result, future):
                    if result.done is False:
                        result.add_done_callback(self.step)
                    else:
                        self.loop.call_soon(self.step)
                else:
                    result.set_exception("can not handle, runtime error")
这里的future和其他的异步编程中的future对象没什么大的区别，仅仅是功能简单点而已，仔细看看accept2 函数和上面的selector 样例代码（下面称呼为code1）有什么区别。 在code1中，我们将recv函数使用register函数进行注册，在code2中我们通过BlockingIOError异常调用add_reader函数进行注册，。和code1一样了是不是？然后我们等着sock进行数据传输。that 
is all right. 然后fut.set_result()，然后我们发现await fut对象，当IO操作执行完成之后，是如何继续向下执行的咧？我们知道coroutine 对象的本质还是一个 generator, coroutine对象帮助我们管理了嵌套的generator对象的上下文。但是一个coroutine如何调度，却还是由我们来掌控，调度的方法就是send方法。核心调度的代码就是step函数。
###基本原理已经讲完了，如有疑惑可以参考具体代码实现。


