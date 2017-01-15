import asyncio

from youtube_dl import YoutubeDL

from collections import deque

class ItemType:
    LocalFile = 1
    YTDLLink = 2

DEFAULT_PLAYER_OPTIONS = {
    'use_avconv': True,
}

YTDL_PLAYER_OPTS = {
    'default_search': 'ytsearch',
    'noplaylist': True
}

class PlayerItem:

    def __init__(self, type, resource, user):
        self.type = type
        self.resource = resource
        self.user = user

        self.infos = dict()
        if self.type == ItemType.YTDLLink:
            self.infos = self.extract_info()

    async def make_player(self, voice):
        if self.type == ItemType.LocalFile:
            player = voice.create_ffmpeg_player(
                self.resource,
                **DEFAULT_PLAYER_OPTIONS
            )
        elif self.type == ItemType.YTDLLink:
            player = await voice.create_ytdl_player(
                self.resource,
                ytdl_options=YTDL_PLAYER_OPTS,
                **DEFAULT_PLAYER_OPTIONS
            )

        return player

    def extract_info(self):
        opts = {
            'simulate': True
        }
        opts.update(YTDL_PLAYER_OPTS)
        ydl = YoutubeDL(opts)
        return ydl.extract_info(self.resource)

class ServerPlayer:

    def __init__(self, server, get_voice, get_volume):
        self.server = server
        self.get_voice = get_voice
        self.get_volume = get_volume

        self.queue = asyncio.Queue()
        self.items = deque()
        self.player = None

    async def start(self, on_error, on_next):
        POLL_INTERVAL = 0.2

        while True:
            item = await self.queue.get()
            on_next(item)

            try:
                voice = self.get_voice(self.server)
                self.player = await item.make_player(voice)
                self.player.volume = self.get_volume()
                self.player.start()
            except Exception as e:
                on_error(e)
            else:
                while not self.player.is_done():
                    await asyncio.sleep(POLL_INTERVAL)

            self.queue.task_done()
            self.items.popleft()

    async def enqueue(self, item):
        self.items.append(item)
        await self.queue.put(item)

    def skip(self):
        self.player.stop()
