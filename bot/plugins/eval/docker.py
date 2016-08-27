from globibot.lib.helpers.async_iterator import AsyncIterator

from docker import Client as DockerClient
from time import time

import asyncio

# TODO: sort those constants out
WORK_DIR = '/snippets'
TIMEOUT = 10
PID_LIMIT = 10

class AsyncDockerClient(DockerClient):

    class Timeout(Exception):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def async_build(self, *args, **kwargs):
        iterator = AsyncIterator()
        iterator.start(self.build, *args, **kwargs)

        return iterator

    def run_async(self, directory, image, code):
        host_config = self.create_host_config(binds = {
            directory: dict(bind=WORK_DIR)
        })
        host_config['PidsLimit'] = PID_LIMIT

        container = self.create_container(
            image       = image,
            working_dir = WORK_DIR,
            host_config = host_config
        )
        self.start(container)

        iterator = AsyncIterator()
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
