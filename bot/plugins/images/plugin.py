from globibot.lib.plugin import Plugin

from globibot.lib.decorators import command
from globibot.lib.helpers import parsing as p
from globibot.lib.helpers.hooks import master_only

from tornado.httpclient import AsyncHTTPClient
from tornado.platform.asyncio import to_asyncio_future

from PIL import Image

class Images(Plugin):

    # def load(self):


    GUN_URL = 'https://dl.dropboxusercontent.com/u/3427186/3071dbc60204c84ca0cf423b8b08a204.png'
    @command(p.bind(p.mention, 'user_id') + p.string('🔫'), master_only)
    async def kill_user(self, message, user_id):
        member = message.server.get_member(str(user_id))
        if member is None:
            return

        client = AsyncHTTPClient()

        tornado_future = client.fetch(member.avatar_url)
        future = to_asyncio_future(tornado_future)
        response = await future

        with open('/tmp/plop.png', 'wb') as f:
            f.write(response.body)

        tornado_future = client.fetch(Images.GUN_URL)
        future = to_asyncio_future(tornado_future)
        response = await future

        with open('/tmp/gun.svg', 'wb') as f:
            f.write(response.body)

        avatar = Image.open('/tmp/plop.png')
        gun = Image.open('/tmp/gun.svg')
        gun.resize(avatar.size)

        total = Image.new('RGB', (avatar.width * 2, avatar.height))

        total.paste(avatar, (0, 0))
        total.paste(gun, (avatar.width, 0))

        total.save('/tmp/lol.png')

        await self.send_file(
            message.channel,
            '/tmp/lol.png',
            delete_after = 30,
            content = '{} is now dead 👍'.format(member.mention)
        )

    MISTAKE_URL = 'http://i.imgur.com/3nR5fDf.png'
    @command(p.string('!mistake') + p.bind(p.mention, 'user_id'), master_only)
    async def mistake_user(self, message, user_id):
        member = message.server.get_member(str(user_id))
        if member is None:
            return

        client = AsyncHTTPClient()

        tornado_future = client.fetch(member.avatar_url)
        future = to_asyncio_future(tornado_future)
        response = await future

        with open('/tmp/plop.png', 'wb') as f:
            f.write(response.body)

        tornado_future = client.fetch(Images.MISTAKE_URL)
        future = to_asyncio_future(tornado_future)
        response = await future

        with open('/tmp/mistake.png', 'wb') as f:
            f.write(response.body)

        avatar = Image.open('/tmp/plop.png')
        mistake = Image.open('/tmp/mistake.png')
        avatar = avatar.resize((505, 557))

        mistake.paste(avatar, (mistake.width - 505, mistake.height - 557))
        mistake.save('/tmp/lol.png')

        await self.send_file(
            message.channel,
            '/tmp/lol.png',
            delete_after = 30,
        )

    @command(p.string('!mistake') + p.bind(p.word, 'url'))
    async def mistake_url(self, message, url):
        client = AsyncHTTPClient()

        try:
            tornado_future = client.fetch(url)
            future = to_asyncio_future(tornado_future)
            response = await future

            with open('/tmp/plop.png', 'wb') as f:
                f.write(response.body)
        except:
            return

        tornado_future = client.fetch(Images.MISTAKE_URL)
        future = to_asyncio_future(tornado_future)
        response = await future

        with open('/tmp/mistake.png', 'wb') as f:
            f.write(response.body)

        img = Image.open('/tmp/plop.png')
        mistake = Image.open('/tmp/mistake.png')
        img = img.resize((505, 557))

        mistake.paste(img, (mistake.width - 505, mistake.height - 557))
        mistake.save('/tmp/lol.png')

        await self.send_file(
            message.channel,
            '/tmp/lol.png',
            delete_after = 30,
        )
