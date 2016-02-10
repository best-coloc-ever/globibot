from ..base import Module, command, master_only, EMOTES

from .errors import *
from .player import Player
from .queue import SongQueue, RandomQueue
from .song import Song

from . import constants as c
from . import tools as t

import asyncio

class Dj(Module):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.invoked_channel = None
        self.voice_channel = None
        self.voice = None

        self.queue = SongQueue()
        self.backup_queue = RandomQueue()
        self.player = Player(self, self.queue, self.backup_queue)

        self.show_queue = False
        self.queue_message = None
        self.refresh_queue = False

        asyncio.ensure_future(self.display_queue())

    @command('!dj join {channel_name}', master_only)
    async def join_room(self, message, channel_name):
        if self.invoked_channel:
            raise AlreadyInvoked(self.invoked_channel)
        # Finding channel by name in the current server
        voice_channel = self.bot.find_voice_channel(
            channel_name,
            message.server
        )
        if voice_channel is None:
            raise NonExistentChannel(channel_name)
        # Attempting to join
        try:
            voice = await self.bot.join_voice_channel(voice_channel)
        except Exception as e:
            raise VoiceChannelJoinError(e)
        # Success
        self.invoked_channel = message.channel
        self.voice_channel = voice_channel
        self.voice = voice
        # Start playing
        self.player.play()

        await self.send_message(
            message.channel,
            (
                'Ready to play music in `{}`!\n'
                'Use the `!dj play youtube_id_or_link` in this channel '
                'to queue songs {}'
            ).format(
                self.voice_channel.name,
                EMOTES.LirikGood
            )
        )

    @command('!dj retire', master_only)
    async def retire(self, message):
        self.ensure_channel(message)
        self.player.stop()
        # Attempting to disconnect
        try:
            await self.voice.disconnect()
        except Exception as e:
            raise VoiceChannelLeaveError(e)
        # Success
        self.invoked_channel = None
        self.voice_channel = None
        self.voice = None

        self.queue.clear()

        await self.send_message(
            message.channel,
            'Bye'
        )

    @command('!dj queue')
    async def toggle_queue(self, message):
        self.ensure_channel(message)
        # Toggling the queue display
        self.show_queue = not self.show_queue

    @command('!dj play {song_link}')
    async def play_song(self, message, song_link):
        self.ensure_channel(message)
        # Queue limit
        if len(self.queue.user_songs(message.author.id)) > c.MAX_VIDEO_PER_USER:
            raise TooManyQueuedForUser
        song = Song(song_link, message)
        # Song duration
        if song.duration > c.MAX_VIDEO_DURATION:
            raise VideoTooLong
        # Uniqueness
        if song in self.queue or song == self.player.current_song:
            raise AlreadyQueued

        await self.send_message(
            message.channel,
            (
                '{} Your song: {} has been queued {}\n'
                'It will be played in `{}`'
            ).format(
                message.author.mention,
                song.formatted(),
                EMOTES.LirikChamp,
                t.format_seconds(max(self.player.queue_duration - song.duration, 0))
            ),
            c.CLEAR_INTERVAL
        )
        # Queuing it
        self.queue.append(song)
        self.refresh_queue = True


    @command('!dj skip')
    async def skip_song(self, message):
        self.ensure_channel(message)
        self.ensure_listening(message)
        self.player.skip()

    @command('!dj blacklist')
    async def blacklist_song(self, message):
        raise NotImplemented
        # self.ensure_channel(message)
        # self.ensure_listening(message)

    def ensure_channel(self, message):
        if self.invoked_channel is None:
            raise NotInvoked
        if self.invoked_channel != message.channel:
            raise WrongChannel

    def ensure_listening(self, message):
        pass

    async def play_error(self, song, exception):
        await self.send_message(
            self.invoked_channel,
            (
                '{} I was unable to play your song {}\n'
                '```\n'
                '{}\n'
                '```'
            ).format(
                song.message.author.mention,
                EMOTES.LirikFeels,
                exception
            )
        )

    def queue_formatted(self):
        queue = self.queue if len(self.queue) else self.backup_queue
        return (
            '{}\n'
            '\n'
            '\n'
            '{}'
        ).format(
            self.player.formatted(),
            queue.formatted()
        )

    async def display_queue(self):
        while True:
            if self.show_queue:
                if self.refresh_queue:
                    self.refresh_queue = False
                    if self.queue_message:
                        await self.bot.delete_message(self.queue_message)
                        self.queue_message = None

                message = self.queue_formatted()
                if self.queue_message is None:
                    self.queue_message = await self.send_message(
                        self.invoked_channel,
                        message
                    )
                else:
                    await self.bot.edit_message(
                        self.queue_message,
                        message
                    )
            else:
                if self.queue_message:
                    await self.bot.delete_message(self.queue_message)
                    self.queue_message = None

            await asyncio.sleep(2.5)
