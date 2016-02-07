from ..base import Module, command

from . import constants as c

from collections import deque
from discord import opus

import asyncio

class Dj(Module):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_opus()

        self.voice = None
        self.queue = asyncio.Queue(c.MAX_QUEUE_SIZE)
        self.songs = deque()

        self.current_player = None

    def init_opus(self):
        try:
            opus.load_opus(c.LIB_OPUS_PATH)
            self.info('Successfully loaded libopus')
        except Exception as e:
            self.error('Error while loading libopus: {}'.format(e))

    @command('!dj join {channel_name}')
    async def join_voice_channel(self, message, channel_name):
        channel = message.channel
        if self.bot.is_voice_connected():
            await self.send_message(channel, 'Already playing music in another server/channel')
        else:
            v_channel = self.bot.find_voice_channel(channel_name, message.server)
            if v_channel is None:
                await self.send_message(channel, 'No voice channel named `{}` on this server'.format(channel_name))
            else:
                try:
                    self.voice = await self.bot.join_voice_channel(v_channel)
                    await self.send_message(channel, 'Ready to play music in `{}`'.format(v_channel.name))
                    asyncio.ensure_future(self.play())
                except Exception as e:
                    await self.send_message(channel, 'I could not join the voice channel: {}'.format(e))

    @command('!dj play {yt_link}')
    async def queue_yt_song(self, message, yt_link):
        channel = message.channel
        if self.voice is None:
            await self.send_message(channel, 'You have to make me join a channel first')
        else:
            if self.queue.full():
                await self.send_message(channel, '@{} Queue is full'.format(message.author.name))
            else:
                try:
                    player = await self.voice.create_ytdl_player(
                        yt_link,
                        use_avconv=True
                    )
                    await self.queue.put(player)
                    self.songs.append((player, message.author))
                    await self.send_message(channel, '@{} Successfully queued your song'.format(message.author.name))
                except Exception as e:
                    await self.send_message(channel, 'Could not queue song: {}'.format(e))

    @command('!dj skip')
    async def skip_song(self, message):
        if self.current_player:
            self.current_player.stop()
            await self.send_message(message.channel, 'Skipping song...')
        else:
            await self.send_message(message.channel, 'There is no song to skip!')

    @command('!dj next song')
    async def next_song(self, message):
        await self.skip_song(message)

    @command('!dj queue')
    async def queue(self, message):
        if not self.songs:
            await self.send_message(message.channel, 'There is currently no queue!')
        else:
            msg = ''
            for player, who in self.songs:
                msg += '{} requested by @{}\n'.format(player.title, who.name)
            await self.send_message(message.channel, msg)

    async def play(self):
        while True:
            if self.current_player is None:
                self.info('Waiting for next song...')
                player = await self.queue.get()
                self.info('Next song playing')
                self.current_player = player
                self.current_player.start()
            else:
                if self.current_player.is_done():
                    self.songs.popleft()
                    self.current_player = None
                else:
                    await asyncio.sleep(2)
