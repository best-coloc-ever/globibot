from globibot.lib.plugin import Plugin
from globibot.lib.decorators import command
from globibot.lib.helpers import parsing as p
from globibot.lib.helpers import formatting as f

from .handlers import ContainerLogHandler
from .specs import EVALSPEC_PER_ALIASES, EVALSPEC_PER_LANGUAGES
from . import constants as C

from collections import defaultdict
from functools import partial

import asyncio
import docker
import os

class Eval(Plugin):

    def load(self):
        self.docker = docker.from_env()

        self.container_logs = defaultdict(list)

        context = dict(plugin=self)
        self.add_web_handlers(
            (r'/eval/logs/(?P<container_id>\S+)', ContainerLogHandler, context),
        )

    '''
    Commands
    '''

    @command(p.string('!eval') + p.string('langs'))
    async def eval_langs(self, message):
        await self.send_message(
            message.channel,
            f.code_block('\n'.join(
                f'{lang: <10} -> {spec.image: <15} {spec.command("file.ext")}'
                for lang, spec in EVALSPEC_PER_LANGUAGES.items()
            ))
        )

    @command(p.bind(p.sparsed(p.snippet), 'snippet'))
    async def on_snippet(self, message, snippet):
        try:
            spec = EVALSPEC_PER_ALIASES[snippet.language]
        except KeyError:
            pass
        else:
            query = self.query_yes_no(
                f'{message.author.mention} Run this code with `{spec.image}` ?',
                channel=message.channel,
                author=message.author,
                timeout=20
            )
            if await query:
                await self.eval(
                    send_message=partial(self.send_message, message.channel),
                    user_key=message.author.id,
                    code=snippet.code,
                    spec=spec
                )

    '''
    Detail
    '''

    async def eval(self, send_message, user_key, code, spec):
        host_dir = os.path.join(C.HOST_MOUNT_DIR, user_key)
        mount_dir = os.path.join(C.DIND_MOUNT_DIR, user_key)
        user_volume_name = C.USER_STORAGE_VOLUME_NAME(user_key)

        file_name = await spec.prepare(host_dir, code)
        file_path = os.path.join(mount_dir, file_name)
        await self.create_volume(user_volume_name)

        try:
            container = self.docker.containers.run(
                image=spec.image,
                command=spec.command(file_path),
                **C.CONTAINER_OPTS(mount_dir, user_volume_name)
            )
        except docker.errors.APIError as e:
            await send_message(
                f'Error while creating container: {f.code_block(e)}\n',
                delete_after=20
            )
        else:
            logs = self.container_logs[container.id]
            stream = container.logs(**C.CONTAINER_LOG_OPTS)
            logs_url = f'https://globibot.com/bot/eval/logs/{container.id}'
            await send_message(f'Running... Full logs available at {logs_url}')

            streaming_message = await send_message('Waiting for output...')
            self.run_async(self.stream_logs(streaming_message, logs, stream))

            status = await self.wait_for_container(container)
            container.remove(force=True)

            final_notice = (
                f'Container exited with status {status}'
                if status is not None else
                f'Container killed after {C.MAX_RUN_TIME} seconds'
            )
            await send_message(final_notice, delete_after=20)

    async def create_volume(self, volume_name):
        try:
            self.docker.volumes.get(volume_name)
        except docker.errors.NotFound:
            self.info(f'Creating volume: {volume_name}')
            self.docker.volumes.create(
                volume_name,
                driver_opts=C.VOLUME_DRIVER_OPTS
            )

    async def stream_logs(self, message, logs, stream):
        async def send_update():
            if logs:
                tail = ''.join(logs[-C.MAX_STREAM_LINES:])
                await self.bot.edit_message(message, f.code_block(tail))

        def accumulate_logs():
            try:
                for line in stream:
                    logs.append(line.decode())
            except docker.errors.APIError as e:
                pass

        async def update_logs():
            try:
                while True:
                    await send_update()
                    await asyncio.sleep(C.STREAM_REFRESH_IMTERVAL)
            except asyncio.CancelledError:
                await send_update()
                if not logs:
                    await self.bot.edit_message(message, 'No output')

        loop = asyncio.get_event_loop()
        update_task = asyncio.ensure_future(update_logs(), loop=loop)
        await loop.run_in_executor(None, accumulate_logs)
        update_task.cancel()

    async def wait_for_container(self, container):
        loop = asyncio.get_event_loop()
        call = partial(container.wait, timeout=C.MAX_RUN_TIME)
        try:
            return await loop.run_in_executor(None, call)
        except:
            return None

    async def query_yes_no(self, question, channel, **kwargs):
        question_message = await self.send_message(
            channel,
            f'{question}\n[y]es/[n]o'
        )
        answer_message = await self.bot.wait_for_message(channel=channel, **kwargs)
        await self.bot.delete_message(question_message)

        if answer_message is not None:
            self.run_async(self.delete_message_after(answer_message, 1))
            return answer_message.content.lower().startswith('y')
        else:
            return False
