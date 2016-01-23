import discord

from action import Action
from commands import COMMANDS

class Globibot:

    def __init__(self, email, password):
        self.client = discord.Client()

        self.client.on_ready = self.on_ready
        self.client.on_message = self.on_message

        self.actions = list(map(
            lambda properties: Action(*properties, self.client.send_message),
            COMMANDS
        ))

        self.client.login(email, password)

    def on_ready(self):
        print('Logged in as')
        print(self.client.user.name)
        print(self.client.user.id)
        print('------')

    def on_message(self, message):
        for action in self.actions:
            if action.matches(message.content):
                action.perform(message.channel)
                break

    def boot(self):
        self.client.run()
