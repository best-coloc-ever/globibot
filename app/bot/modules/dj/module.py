from ..base import Module, command

from . import constants as c

from utils.logging import logger

from collections import deque
from discord import ChannelType, opus

import asyncio

class Dj(Module):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            opus.load_opus(c.LIB_OPUS_PATH)
            logger.info('Successfully loaded libopus')
        except Exception as e:
            logger.error('Error while loading libopus: {}'.format(e))

        self.voice = None
        self.queue = asyncio.Queue(c.MAX_QUEUE_SIZE)
        self.songs = deque()

        self.current_player = None

    def find_voice_channel(self, name):
        server = self.last_message.channel.server

        for channel in server.channels:
            if channel.type == ChannelType.voice and channel.name.lower() == name.lower():
                return channel

        return None

    @command('!dj join {channel_name}')
    async def join_voice_channel(self, message, channel_name):
        channel = self.last_message.channel
        if self.bot.client.is_voice_connected():
            await self.bot.client.send_message(channel, 'Already playing music in another server/channel')
        else:
            v_channel = self.find_voice_channel(channel_name)
            if v_channel is None:
                await self.bot.client.send_message(channel, 'No voice channel named `{}` on this server'.format(channel_name))
            else:
                try:
                    self.voice = await self.bot.client.join_voice_channel(v_channel)
                    await self.bot.client.send_message(channel, 'Ready to play music in `{}`'.format(v_channel.name))
                    asyncio.ensure_future(self.play())
                except Exception as e:
                    await self.bot.client.send_message(channel, 'I could not join the voice channel: {}'.format(e))

    @command('!dj play {yt_link}')
    async def queue_yt_song(self, message, yt_link):
        channel = self.last_message.channel
        if self.voice is None:
            await self.bot.client.send_message(channel, 'You have to make me join a channel first')
        else:
            if self.queue.full():
                await self.bot.client.send_message(channel, '@{} Queue is full'.format(message.author.name))
            else:
                try:
                    player = await self.voice.create_ytdl_player(
                        yt_link,
                        use_avconv=True
                    )
                    await self.queue.put(player)
                    self.songs.append((player, message.author))
                    await self.bot.client.send_message(channel, '@{} Successfully queued your song'.format(message.author.name))
                except Exception as e:
                    await self.bot.client.send_message(channel, 'Could not queue song: {}'.format(e))

    @command('!dj skip')
    async def skip_song(self, message):
        if self.current_player:
            self.current_player.stop()
            await self.respond('Skipping song...')
        else:
            await self.respond('There is no song to skip!')

    @command('!dj next song')
    async def next_song(self, message):
        await self.skip_song(message)

    @command('!dj queue')
    async def queue(self, message):
        if not self.songs:
            await self.respond('There is currently no queue!')
        else:
            message = ''
            for player, who in list(self.songs):
                message += '{} requested by @{}\n'.format(player.title, who.name)
            await self.respond(message)

    async def play(self):
        while True:
            if self.current_player is None:
                logger.info('Waiting for next song...')
                player = await self.queue.get()
                logger.info('Next song playing')
                self.current_player = player
                self.current_player.start()
            else:
                if self.current_player.is_done():
                    self.songs.pop()
                    self.current_player = None
                else:
                    await asyncio.sleep(2)
