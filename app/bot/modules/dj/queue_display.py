from . import constants as c

import asyncio

class QueueDisplay:

    def __init__(self, module):
        self.module = module

        self.queue_message = None
        self.pull_down_next = False
        self.show_queue = True

    def toggle(self):
        self.show_queue = not self.show_queue

    def pull_down(self):
        self.pull_down_next = True

    async def run(self):
        while True:

            if self.show_queue:
                await self.refresh_queue()
            else:
                await self.delete_queue()

            await asyncio.sleep(c.QUEUE_REFRESH_TIME)

    async def delete_queue(self):
        if self.queue_message:
            try:
                await self.module.bot.delete_message(self.queue_message)
            except:
                pass
            self.queue_message = None

    async def refresh_queue(self):
        # Acknowledging pull down requests
        if self.pull_down_next:
            await self.delete_queue()
            self.pull_down_next = False

        message = self.formatted()

        if self.queue_message is None:
            self.queue_message = await self.module.send_message(
                    self.module.invoked_channel,
                    message
                )
        else:
            try:
                await self.module.bot.edit_message(
                    self.queue_message,
                    message
                )
            except:
                await self.delete_queue()

    def formatted(self):
        queue = self.module.queue if len(self.module.queue) else self.module.backup_queue
        return (
            '{}\n'
            '\n'
            '\n'
            '{}'
        ).format(
            self.module.player.formatted(),
            queue.formatted()
        )
