import asyncio

from youtube_dl import YoutubeDL

from collections import deque

class ItemType:
    LocalFile = 1
    YTDLLink = 2

DEFAULT_PLAYER_OPTIONS = {
    'use_avconv': True,
}

YTDL_PLAYER_OPTS = lambda pl: {
    'default_search': 'ytsearch',
    'noplaylist': not pl
}

BOOTBANDITS_ID = '98468595742302208'

class PlayerItem:

    def __init__(self, type, resource, user):
        self.type = type
        self.resource = resource
        self.user = user
        self.allow_playlists = user.server.id == BOOTBANDITS_ID

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
                ytdl_options=YTDL_PLAYER_OPTS(self.allow_playlists),
                **DEFAULT_PLAYER_OPTIONS
            )

        return player

    def extract_info(self):
        opts = {
            'simulate': True
        }
        opts.update(YTDL_PLAYER_OPTS(self.allow_playlists))
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

    async def start(self, on_error, debug, on_next):
        POLL_INTERVAL = 1

        while True:
            item = await self.queue.get()
            on_next(item)

            try:
                voice = self.get_voice(self.server)
                debug(self.server.voice_client)
                # debug(voice)
                self.player = await item.make_player(voice)
                self.player.volume = self.get_volume()
                self.player.start()
            except Exception as e:
                on_error(e)
            else:
                while not self.player.is_done():
                    debug(
                        'Player iteration:\n'
                        ' - Playing: {}\n'
                        ' - Done: {}\n'
                            .format(
                                self.player.is_playing(),
                                self.player.is_done()
                            )
                    )
                    await asyncio.sleep(POLL_INTERVAL)


                mb_err = self.player.error
                if mb_err is not None:
                    on_error('PLAYER STOPPED WITH ERROR: {}'.format(mb_err))

            self.queue.task_done()
            self.items.popleft()

    async def enqueue(self, item):
        self.items.append(item)
        await self.queue.put(item)

    def skip(self):
        self.player.stop()
