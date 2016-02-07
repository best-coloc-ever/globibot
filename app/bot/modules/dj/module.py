from ..base import Module, command

from . import constants as c

from datetime import timedelta
from collections import deque
from discord import opus

import asyncio
import time

class Dj(Module):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.init_opus()

        self.voice = None
        self.voice_channel = None
        self.current_player = None
        self.song_start_time = None
        self.queue = asyncio.Queue(c.MAX_QUEUE_SIZE)
        self.songs = deque()
        self.skips = set()

    def init_opus(self):
        try:
            opus.load_opus(c.LIB_OPUS_PATH)
            self.info('Successfully loaded libopus')
        except Exception as e:
            self.error('Error while loading libopus: {}'.format(e))

    @command('!dj join {channel_name}')
    async def join_voice_channel(self, message, channel_name):
        if self.bot.is_voice_connected():
            await self.send_message(
                message.channel,
                'Already playing music in `{}` #{}'.format(
                    message.server,
                    message.channel
                )
            )
        else:
            self.voice_channel = self.bot.find_voice_channel(
                channel_name,
                message.server
            )

            if self.voice_channel is None:
                await self.send_message(
                    message.channel,
                    'No voice channel named `{}` on this server'.format(
                        channel_name
                    )
                )
            else:
                try:
                    self.voice = await self.bot.join_voice_channel(
                        self.voice_channel
                    )
                    await self.send_message(
                        message.channel,
                        'Ready to play music in `{}`'.format(
                            self.voice_channel.name
                        )
                    )

                    asyncio.ensure_future(self.play_forever())
                except Exception as e:
                    await self.send_message(
                        message.channel,
                        'I can not join the voice channel: {}'.format(e)
                    )

    @command('!dj play {yt_link}')
    async def queue_yt_song(self, message, yt_link):
        if self.voice is None:
            await self.send_message(
                message.channel,
                '{} you have to make me join a channel first'.format(
                    message.author.mention
                ),
                c.CLEAR_INTERVAL
            )
        else:
            if self.queue.full():
                await self.send_message(
                    message.channel,
                    '{} queue is full'.format(
                        message.author.mention
                    ),
                    c.CLEAR_INTERVAL
                )
            else:
                if not self.user_can_enqueue(message.author):
                    await self.send_message(
                        message.channel,
                        '{} {} of your songs are already queued'.format(
                            message.author.mention,
                            c.MAX_VIDEO_PER_USER
                        ),
                        c.CLEAR_INTERVAL
                    )
                    return
                try:
                    queue_time = self.queue_time()
                    player = await self.voice.create_ytdl_player(
                        yt_link,
                        use_avconv=True,
                        ytdl_options= {
                            'noplaylist': True,
                            'ignoreerrors': True
                        }
                    )
                    self.debug(player.url)
                    if self.is_enqueued(player.url):
                        await self.send_message(
                            message.channel,
                            '{} this song is already queued'.format(
                                message.author.mention
                            ),
                            c.CLEAR_INTERVAL
                        )
                        return

                    if player.duration > c.MAX_VIDEO_DURATION:
                        raise Exception('duration is too long')

                    await self.queue.put(player)
                    self.songs.append((player, message))

                    if len(self.songs) > 1:
                        await self.send_message(
                            message.channel,
                            (
                                '{} successfully queued your song: {} ({}). '
                                'It will be played in {}'
                            ).format(
                                message.author.mention,
                                player.title,
                                timedelta(seconds=player.duration),
                                timedelta(seconds=queue_time)
                            ),
                            c.CLEAR_INTERVAL
                        )
                except Exception as e:
                    await self.send_message(
                        message.channel,
                        '{} I can not queue your song: {}'.format(
                            message.author.mention,
                            e
                        ),
                        c.CLEAR_INTERVAL
                    )

    @command('!dj skip')
    @command('!dj next song')
    async def skip_song(self, message):
        if self.current_player:
            if message.author.id not in self.skips:
                self.skips.add(message.author.id)
                await self.send_message(
                    message.channel,
                    '{} your skip was acknowledged. {} more skips to go!'.format(
                        message.author.mention,
                        self.required_skips() - len(self.skips)
                    ),
                    c.CLEAR_INTERVAL
                )
            if len(self.skips) >= self.required_skips():
                await self.send_message(
                    message.channel,
                    'Skip vote passed. Skipping song...',
                    c.CLEAR_INTERVAL
                )
                self.current_player.stop()
        else:
            await self.send_message(
                message.channel,
                '{} there are no song to skip!'.format(
                    message.author.mention
                ),
                c.CLEAR_INTERVAL
            )

    def required_skips(self):
        members = self.voice_channel.voice_members
        return max(1, len(members) - 1)


    @command('!dj queue')
    async def queue(self, message):
        if not self.songs:
            await self.send_message(
                message.channel,
                'Queue is empty!',
                c.CLEAR_INTERVAL
            )
        else:
            await self.send_message(
                message.channel,
                self.formatted_queue(),
                c.CLEAR_INTERVAL
            )

    def formatted_queue(self):
        info = 'Currently playing: **{}** ({} left)\n\n'.format(
            self.songs[0][0].title,
            timedelta(seconds=self.time_left())
        )

        for i in range(1, len(self.songs)):
            player, message = self.songs[i]
            info += '[{}] **{}** requested by {} ({})\n'.format(
                i,
                player.title,
                message.author.mention,
                timedelta(seconds=player.duration)
            )

        return info

    def time_left(self):
        if self.current_player:
            now = time.time()
            song_current = now - self.song_start_time
            return int(self.current_player.duration - song_current)
        return 0

    def queue_time(self):
        total = 0
        for player, _ in self.songs:
            total += player.duration
        if self.current_player:
            total -= self.current_player.duration
            total += self.time_left()
        return total

    def user_can_enqueue(self, author):
        from_author = lambda song: song[1].author.id == author.id
        return len(list(filter(from_author, self.songs))) < c.MAX_VIDEO_PER_USER

    def is_enqueued(self, url):
        for player, _ in self.songs:
            if url == player.url:
                return True

        return False

    async def play_forever(self):
        while True:
            if self.current_player is None:
                self.info('Waiting for next song...')
                player = await self.queue.get()
                self.info('Next song playing')
                self.song_start_time = time.time()
                self.current_player = player
                self.current_player.start()
                self.skips.clear()

                _, message = self.songs[0]
                await self.send_message(
                    message.channel,
                    '{} your song: {} is now playing'.format(
                        message.author.mention,
                        player.title
                    ),
                    c.CLEAR_INTERVAL
                )
            else:
                if self.current_player.is_done():
                    self.songs.popleft()
                    self.current_player = None
                else:
                    await asyncio.sleep(1)
