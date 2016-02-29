from ..base import EMOTES

import random

class Kappa:

    DEFAULT_KAPPA_LEVEL = 0.3

    def __init__(self, emote_store, text_sender, file_sender):
        self.emote_store = emote_store
        self.text_sender = text_sender
        self.file_sender = file_sender

        self.level = Kappa.DEFAULT_KAPPA_LEVEL

        self.behaviors = [
            self.wrong_emote,
            self.deny_not_boss,
            self.deny_ugly_emote,
            self.nope,
            self.dont_like_you,
            self.report_abuse,
        ]

    async def reply_to_emote(self, message, emote_name, emote_size):
        emote_file = self.emote_store.get(emote_name, emote_size)

        if emote_file is None:
            return

        if random.random() <= self.level:
            behavior = random.choice(self.behaviors)
            await behavior(message, emote_name, emote_size)
        else:
            await self.file_sender(message.channel, emote_file)

    DRUNK_EMOJIS = ['🍷', '🍺', '🍻']
    async def wrong_emote(self, message, emote_name, emote_size):
        # Find another emote name
        emote_names = list(self.emote_store.url_store.keys())
        while True:
            new_emote_name = random.choice(emote_names)
            if new_emote_name != emote_name:
                break

        emote_file = self.emote_store.get(new_emote_name, emote_size)

        await self.file_sender(message.channel, emote_file)
        await self.text_sender(
            message.channel,
            '{} sorry I\'m kinda drunk right now {}'.format(
                message.author.mention,
                random.choice(Kappa.DRUNK_EMOJIS)
            )
        )

    async def deny_not_boss(self, message, emote_name, emote_size):
        await self.text_sender(
            message.channel,
            '{} you\'re not the boss of me {}'.format(
                message.author.mention,
                EMOTES.LirikNot
            )
        )

    async def deny_ugly_emote(self, message, emote_name, emote_size):
        await self.text_sender(
            message.channel,
            '{} Ewww not that one {}'.format(
                message.author.mention,
                EMOTES.LirikPuke
            )
        )

        if emote_name != 'danSgame':
            await self.file_sender(
                message.channel,
                self.emote_store.get('danSgame', emote_size)
            )

    async def nope(self, message, emote_name, emote_size):
        await self.text_sender(
            message.channel,
            '{} nope'.format(message.author.mention)
        )

        if emote_name != 'Kappa':
            await self.file_sender(
                message.channel,
                self.emote_store.get('Kappa', emote_size)
            )

    async def dont_like_you(self, message, emote_name, emote_size):
        await self.text_sender(
            message.channel,
            '{} I don\'t like you {}'.format(
                message.author.mention,
                EMOTES.LirikNot
            )
        )

    async def report_abuse(self, message, emote_name, emote_size):
        await self.text_sender(
            message.channel,
            '{} I won\'t do it, stop abusing me {}'.format(
                message.author.mention,
                EMOTES.LirikFeels
            )
        )
