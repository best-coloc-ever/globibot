from ..base import EMOTES

from . import constants as c
from . import tools as t

from discord import opus
from time import time

import asyncio

class Player:

    def __init__(self, module, queue, backup):
        self.module = module
        self.queue = queue
        self.backup = backup

        self.current_song = None
        self.current_player = None
        self.started_at = time()
        self.running = False

        self._init_opus()

        asyncio.ensure_future(self.run_forever())

    def play(self):
        self.running = True

    def stop(self):
        self.skip()
        self.running = False

    def skip(self):
        self.current_player.stop()
        self.current_player = None
        self.current_song = None

    def formatted(self):
        message = str()
        if self.current_song:
            message += '{dj}    ▶ `{progress}`  {song}    {dj}'.format(
                dj=EMOTES.LirikDj,
                song=self.current_song.formatted(),
                progress='[{} / {}]'.format(
                    t.format_seconds(self.progress),
                    t.format_seconds(self.current_song.duration)
                )
            )

        return message

    @property
    def progress(self):
        return time() - self.started_at

    @property
    def queue_duration(self):
        duration = sum(song.duration for song in self.queue)
        if self.current_song:
            duration += (self.current_song.duration - self.progress)
        return 0

    async def run_forever(self):
        while True:
            if self.running:
                if self.current_player is None or self.current_player.is_done():
                    await self.play_next()

            await asyncio.sleep(1)

    async def play_next(self):
        if len(self.queue):
            await self.play_next_in_queue()
        elif len(self.backup):
            await self.play_next_in_backup()

    async def play_next_in_queue(self):
        song = self.queue.popleft()
        await self.play_song(song)

    async def play_next_in_backup(self):
        song = self.backup.popleft()
        self.backup.append(song)
        await self.play_song(song)

    async def play_song(self, song):
        try:
            player = await self.module.voice.create_ytdl_player(
                song.link,
                use_avconv=True,
                ytdl_options=c.YTDL_OPTIONS
            )
            player.start()
        except Exception as e:
            await self.module.play_error(song, e)

        self.started_at = time()
        self.current_song = song
        self.current_player = player

        if song not in self.backup:
            self.backup.append(song)

    def _init_opus(self):
        try:
            opus.load_opus(c.LIB_OPUS_PATH)
            self.module.info('Successfully loaded libopus')
        except Exception as e:
            self.module.error('Error while loading libopus: {}'.format(e))
