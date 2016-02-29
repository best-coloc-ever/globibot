from tornado import web
from tornado.platform.asyncio import AsyncIOMainLoop

from utils.logging import logger

from . import constants as c
from . import handlers

def init_web_app():
    AsyncIOMainLoop().install()

    routes = [
        # Standalone routes maybe ?
    ]

    return WebApplication(
        routes,
        autoreload=True,
    )

class WebApplication(web.Application):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def run(self):
        try:
            self.listen(c.DEFAULT_PORT)
            logger.info('Web server listening on port {}'.format(c.DEFAULT_PORT))
        except Exception as e:
            logger.error('Could not start web server: {}'.format(e))
