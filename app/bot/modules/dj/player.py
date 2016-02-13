from ..base import EMOTES

from . import constants as c
from . import tools as t

from discord import opus
from time import time

import asyncio

class Player:

    def __init__(self, module):
        self.module = module
        self.queue = module.queue
        self.backup = module.backup_queue

        self.current_song = None
        self.current_player = None
        self.started_at = time()
        self.running = False

        self._init_opus()

    def play(self):
        self.running = True
        self.module.run_async(
            self.run_forever(),
            self.module.invoked_channel
        )

    def stop(self):
        self.running = False

    def skip(self):
        self.current_player.stop()
        self.current_player = None
        self.current_song = None

    def __str__(self):
        if self.current_song:
            return (
                '{dj} 🎵   *Now playing*   🎵{dj}\n'
                '--------------------------------------------------\n'
                '**{song}**   [`{views:,}` 👀  |  `{likes:,}` 👍  |  `{dislikes:,}` 👎]\n'
                '*Added by {who}*\n'
                '--------------------------------------------------\n'
                '▶ `{progress}` ▶'
            ).format(
                dj=EMOTES.LirikDj,
                song=self.current_song,
                views=self.current_song.views,
                likes=self.current_song.likes,
                dislikes=self.current_song.dislikes,
                who=self.current_song.message.author.mention,
                progress='[{} / {}]'.format(
                    t.format_seconds(self.progress),
                    t.format_seconds(self.current_song.duration)
                )
            )

        return str()

    @property
    def progress(self):
        return time() - self.started_at

    @property
    def queue_duration(self):
        duration = sum(song.duration for song in self.queue)
        if self.current_song:
            duration += (self.current_song.duration - self.progress)
        return duration

    async def run_forever(self):
        while self.running:
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
