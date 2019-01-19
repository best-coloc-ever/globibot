from tornado import web
from tornado.platform.asyncio import AsyncIOMainLoop

import asyncio

async def run_command(*args):
    process = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    return (
        process.returncode,
        stdout.decode().strip(),
        stderr.decode().strip() if stderr else None
    )

class MainHandler(web.RequestHandler):

    async def get(self):
        args = self.get_query_argument('args')
        code, out, err = await run_command(
            '/opt/factorio-init/factorio',
            *args.split(' ')
        )

        self.write('Command exited with status `{}`\nout:```{}```\nerr:```{}```'.format(code, out, err))

def run():
    app = web.Application([
        (r"/factorio", MainHandler),
    ])
    app.listen(8899)

AsyncIOMainLoop().install()
loop = asyncio.get_event_loop()
run()
loop.run_forever()
