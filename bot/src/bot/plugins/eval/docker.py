from docker import Client as DockerClient

from time import time
from queue import Queue
from threading import Thread

import asyncio

WORK_DIR = '/snippets'
TIMEOUT = 10

class AsyncDockerClient(DockerClient):

    class Timeout(Exception):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def async_build(self, *args, **kwargs):
        iterator = StreamIterator()
        iterator.start(self.build, *args, **kwargs)
        return iterator

    def run_async(self, directory, image, code):
        container = self.create_container(
            image       = image,
            working_dir = WORK_DIR,
            host_config = self.create_host_config(binds = {
                directory: dict(bind=WORK_DIR)
            })
        )
        self.start(container)

        iterator = StreamIterator()
        executor = iterator.start(self.logs, container, stream=True)
        asyncio.ensure_future(self.poll_container(container, executor))
        return iterator

    async def poll_container(self, container, executor):
        started = time()

        while True:
            await asyncio.sleep(1)
            state = self.inspect_container(container)
            if not state['State']['Running']:
                break
            if time() - started > TIMEOUT:
                executor.throw(AsyncDockerClient.Timeout)
                self.kill(container)
                break

        self.remove_container(container, force=True, v=True)

class StreamIterator:

    def __init__(self):
        self.queue = Queue()
        self.thread = None
        self.done = False
        self.throw_on_exit = None

    def start(self, call, *args, **kwargs):

        def run():
            for line in call(*args, **kwargs):
                self.queue.put(line)
            self.done = True

        self.thread = Thread(target=run)
        self.thread.start()

        return self

    def throw(self, cls):
        self.throw_on_exit = cls

    async def __aiter__(self):
        return self

    async def __anext__(self):
        while self.queue.empty():
            if self.done:
                if self.throw_on_exit:
                    raise self.throw_on_exit
                raise StopAsyncIteration
            await asyncio.sleep(.5)

        item = self.queue.get()
        self.queue.task_done()
        return item
