from queue import Queue
from threading import Thread

import asyncio

class AsyncIterator:

    POLL_INTERVAL = .5

    def __init__(self):
        self.queue = Queue()
        self.thread = None
        self.done = False
        self.stop_iteration_cls = StopAsyncIteration

    def start(self, call, *args, **kwargs):

        def run():
            for line in call(*args, **kwargs):
                self.queue.put(line)
            self.done = True

        self.thread = Thread(target=run)
        self.thread.start()

        return self

    def throw(self, cls):
        self.stop_iteration_cls = cls

    async def __aiter__(self):
        return self

    async def __anext__(self):
        while self.queue.empty():
            if self.done:
                raise self.stop_iteration_cls

            await asyncio.sleep(AsyncIterator.POLL_INTERVAL)

        item = self.queue.get()
        self.queue.task_done()
        return item
