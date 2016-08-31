from globibot.lib.helpers.async_iterator import AsyncIterator

from docker import Client as DockerClient
from time import time

import asyncio

# TODO: sort those constants out
WORK_DIR = '/snippets'
TIMEOUT = 10
PID_LIMIT = 20
VOLUME_PREFIX = 'globibot_user-volume_'
VOLUME_MAX_SIZE = '150m'
PERSISTENT_DATA_DIR = '/persistent'

volume_name = lambda snowflake: '{}{}'.format(VOLUME_PREFIX, snowflake)

class AsyncDockerClient(DockerClient):

    class Timeout(Exception):
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs, version='auto')

        self.user_volumes = set()
        for volume in self.volumes()['Volumes']:
            if volume['Name'].startswith(VOLUME_PREFIX):
                user_id = volume['Name'][len(VOLUME_PREFIX):]
                self.user_volumes.add(user_id)

    def async_build(self, *args, **kwargs):
        iterator = AsyncIterator()
        iterator.start(self.build, *args, **kwargs)

        return iterator

    def run_async(self, directory, image, user_id):
        if user_id not in self.user_volumes:
            self.create_volume_for(user_id)

        volume = volume_name(user_id)
        host_config = self.create_host_config(binds = {
            directory: dict(bind=WORK_DIR),
            volume: dict(bind=PERSISTENT_DATA_DIR)
        })
        host_config['PidsLimit'] = PID_LIMIT

        container = self.create_container(
            volumes     = [WORK_DIR, PERSISTENT_DATA_DIR],
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

        self.remove_container(container, force=True)

    def create_volume_for(self, user_id):
        self.create_volume(
            name        = volume_name(user_id),
            driver      = 'local',
            # driver_opts = dict(
            #     type   = 'ext4',
            #     device = '/dev/sda1',
            #     o      = 'size={}'.format(VOLUME_MAX_SIZE)
            # ),
            labels      = dict(globibot='yes')
        )
        self.user_volumes.add(user_id)
