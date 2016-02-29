from . import constants as c

import asyncio

class QueueDisplay:

    def __init__(self, module, channel):
        self.module = module

        self.enabled = True

        self.queue_message = None
        self.pull_down_next = False
        self.show_queue = True

        module.run_async(
            self.run(),
            channel
        )

    def toggle(self):
        self.show_queue = not self.show_queue

    def disable(self):
        self.enabled = False

    def pull_down(self):
        self.pull_down_next = True

    async def run(self):
        while self.enabled:

            if self.show_queue:
                await self.refresh_queue()
            else:
                await self.delete_queue()

            await asyncio.sleep(c.QUEUE_REFRESH_TIME)

        await self.delete_queue()

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

        if self.queue_message is None:
            if self.module.invoked_channel:
                self.queue_message = await self.module.send_message(
                    self.module.invoked_channel,
                    self
                )
        else:
            try:
                await self.module.bot.edit_message(
                    self.queue_message,
                    self
                )
            except:
                await self.delete_queue()

    def __str__(self):
        queue = self.module.queue if len(self.module.queue) else self.module.backup_queue
        if len(queue):
            return (
                '{}\n'
                '{}'
            ).format(
                self.module.player,
                queue
            )
        return ' '
