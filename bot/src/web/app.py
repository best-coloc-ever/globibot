from tornado import web
from tornado.platform.asyncio import AsyncIOMainLoop

from utils.logging import logger

from . import constants as c
from . import handlers

def init_web_app(config, static_root):
    AsyncIOMainLoop().install()

    routes = [
        (r'/', handlers.RootHandler, dict(path=static_root)),
        (r'/(favicon\.png)', web.StaticFileHandler, dict(path=static_root)),
        (r'/(styles\.css)', web.StaticFileHandler, dict(path=static_root)),
    ]

    port = config.get(c.WEB_PORT_KEY, c.DEFAULT_WEB_PORT)

    return WebApplication(
        port,
        routes,
    )

class WebApplication(web.Application):

    def __init__(self, port, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.port = port

    async def run(self):
        try:
            self.listen(self.port)
            logger.info('Web server listening on port {}'.format(self.port))
        except Exception as e:
            logger.error('Could not start web server: {}'.format(e))
